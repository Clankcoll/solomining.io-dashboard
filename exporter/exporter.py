#!/usr/bin/env python3
"""
Prometheus exporter for solomining.io mining pool statistics.
Scrapes mining data and exposes metrics for Prometheus.
"""

import json
import logging
import math
import os
import time
from typing import Dict, Any, Optional

import requests
from bs4 import BeautifulSoup
from prometheus_client import start_http_server, Gauge, Info, Counter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
SCRAPE_INTERVAL = int(os.getenv('SCRAPE_INTERVAL', '60'))  # seconds
EXPORTER_PORT = int(os.getenv('EXPORTER_PORT', '9123'))
BCH_ADDRESS = os.getenv('BCH_ADDRESS', 'bitcoincash:YOUR_BCH_ADDRESS_HERE')
BASE_URL = os.getenv('BASE_URL', 'https://bchnode.solomining.io/address.php')
BCH_DIFFICULTY_URL = os.getenv('BCH_DIFFICULTY_URL', 'https://api.blockchair.com/bitcoin-cash/stats')

# Constants for block calculations
MAX_TARGET = 0xFFFF * (2 ** 208)  # Bitcoin/BCH max target
BLOCK_TIME_SECONDS = 600  # BCH block time (10 minutes)

# Prometheus metrics
# Account-level metrics
account_hashrate = Gauge('solomining_account_hashrate', 'Account hashrate', ['timeframe'])
account_workers = Gauge('solomining_account_workers', 'Number of active workers')
account_shares_accepted = Counter('solomining_account_shares_accepted_total', 'Total accepted shares')
account_shares_rejected = Counter('solomining_account_shares_rejected_total', 'Total rejected shares')
account_best_share = Gauge('solomining_account_best_share_difficulty', 'Best share difficulty')
account_last_update = Gauge('solomining_account_last_update_timestamp', 'Last update timestamp')

# Worker-level metrics
worker_hashrate = Gauge('solomining_worker_hashrate', 'Worker hashrate', ['worker', 'timeframe'])
worker_shares_accepted = Counter('solomining_worker_shares_accepted_total', 'Worker accepted shares', ['worker'])
worker_shares_rejected = Counter('solomining_worker_shares_rejected_total', 'Worker rejected shares', ['worker'])
worker_last_share = Gauge('solomining_worker_last_share_timestamp', 'Worker last share timestamp', ['worker'])

# Scrape status
scrape_success = Gauge('solomining_scrape_success', 'Whether the last scrape was successful')
scrape_duration = Gauge('solomining_scrape_duration_seconds', 'Duration of the last scrape')

# BCH Network and Block Finding Metrics
bch_network_difficulty = Gauge('bch_network_difficulty', 'Current BCH network difficulty')
solomining_block_progress_percent = Gauge('solomining_block_progress_percent', 'Best share as percentage of network difficulty')
solomining_expected_time_to_block_seconds = Gauge('solomining_expected_time_to_block_seconds', 'Expected time to find a block in seconds')
solomining_block_chance_daily = Gauge('solomining_block_chance_daily', 'Probability of finding a block in one day (0-1)')
solomining_block_chance_weekly = Gauge('solomining_block_chance_weekly', 'Probability of finding a block in one week (0-1)')
solomining_block_chance_monthly = Gauge('solomining_block_chance_monthly', 'Probability of finding a block in one month (0-1)')
solomining_block_chance_yearly = Gauge('solomining_block_chance_yearly', 'Probability of finding a block in one year (0-1)')


def clean_worker_name(worker_name: str) -> str:
    """
    Clean worker name by removing the Bitcoin Cash address prefix.

    Example: 'bitcoincash:YOUR_BCH_ADDRESS_HERE.Apollo2' -> 'Apollo2'

    Args:
        worker_name: Raw worker name from API

    Returns:
        Cleaned worker name
    """
    # Worker names are formatted as "address.workername"
    # Split on the last dot and take the part after it
    if '.' in worker_name:
        return worker_name.split('.')[-1]
    return worker_name


def fetch_bch_difficulty() -> Optional[float]:
    """
    Fetch current BCH network difficulty from Blockchair API.

    Returns:
        Current network difficulty or None if fetch fails
    """
    try:
        logger.info(f"Fetching BCH network difficulty from {BCH_DIFFICULTY_URL}")
        response = requests.get(BCH_DIFFICULTY_URL, timeout=10)
        response.raise_for_status()

        data = response.json()
        difficulty = data.get('data', {}).get('difficulty')

        if difficulty:
            logger.info(f"BCH network difficulty: {difficulty:,.2f}")
            return float(difficulty)
        else:
            logger.warning("No difficulty field found in API response")
            return None

    except requests.RequestException as e:
        logger.error(f"Failed to fetch BCH difficulty: {e}")
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse BCH difficulty: {e}")
        return None


def calculate_expected_time_to_block(hashrate: float, difficulty: float) -> float:
    """
    Calculate expected time to find a block in seconds.

    Formula: ETB = (difficulty * 2^32) / hashrate

    Args:
        hashrate: Hashrate in hashes/second
        difficulty: Network difficulty

    Returns:
        Expected time to block in seconds
    """
    if hashrate <= 0:
        return float('inf')

    # ETB = (difficulty * 2^32) / hashrate
    etb_seconds = (difficulty * (2 ** 32)) / hashrate
    return etb_seconds


def calculate_block_chance(etb_seconds: float, time_period_seconds: int) -> float:
    """
    Calculate probability of finding a block within a given time period.

    Formula: Chance = 1 - e^(-time_period / ETB)

    Args:
        etb_seconds: Expected time to block in seconds
        time_period_seconds: Time period to calculate chance for

    Returns:
        Probability between 0 and 1
    """
    if etb_seconds <= 0 or etb_seconds == float('inf'):
        return 0.0

    # Poisson distribution: P(at least 1 block) = 1 - e^(-λ)
    # where λ = time_period / ETB
    lambda_val = time_period_seconds / etb_seconds
    chance = 1 - math.exp(-lambda_val)
    return chance


def fetch_mining_data() -> Dict[str, Any]:
    """
    Fetch and parse mining data from solomining.io.

    Returns:
        Dictionary containing parsed mining statistics
    """
    url = f"{BASE_URL}?a={BCH_ADDRESS}"

    try:
        logger.info(f"Fetching data from {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Parse HTML and extract JSON from <pre> tag
        soup = BeautifulSoup(response.text, 'html.parser')
        pre_tag = soup.find('pre')

        if not pre_tag:
            raise ValueError("No <pre> tag found in response")

        # Parse JSON
        data = json.loads(pre_tag.text)
        logger.info("Successfully parsed mining data")
        return data

    except requests.RequestException as e:
        logger.error(f"Failed to fetch data: {e}")
        raise
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse data: {e}")
        raise


def update_metrics(data: Dict[str, Any]) -> None:
    """
    Update Prometheus metrics with the latest mining data.

    Args:
        data: Parsed mining statistics dictionary
    """
    try:
        # Account-level metrics
        account_workers.set(data.get('workers', 0))

        # Hashrate metrics - using raw unformatted values (u_hashrate*)
        # Map the API field names to clean timeframe labels
        hashrate_fields = {
            'u_hashrate1m': '1min',
            'u_hashrate5m': '5min',
            'u_hashrate1hr': '1hr',
            'u_hashrate1d': '1day',
            'u_hashrate7d': '7day'
        }

        for field_name, timeframe in hashrate_fields.items():
            value = data.get(field_name, 0)
            if value:
                account_hashrate.labels(timeframe=timeframe).set(value)

        # Share metrics
        account_shares_accepted._value._value = data.get('shares_diff_a', 0)
        account_shares_rejected._value._value = data.get('shares_diff_r', 0)
        account_best_share.set(data.get('bestshare', 0))
        account_last_update.set(data.get('lastupdate', 0))

        # Worker-level metrics
        workers_list = data.get('worker', [])
        for worker_info in workers_list:
            # Get worker name and clean it (strip address prefix)
            worker_name = worker_info.get('workername', 'unknown')
            clean_name = clean_worker_name(worker_name)

            # Worker hashrate fields mapping
            worker_hashrate_fields = {
                'w_hashrate1m': '1min',
                'w_hashrate5m': '5min',
                'w_hashrate1hr': '1hr',
                'w_hashrate1d': '1day',
                'w_hashrate7d': '7day'
            }

            for field_name, timeframe in worker_hashrate_fields.items():
                value = worker_info.get(field_name, 0)
                if value:
                    worker_hashrate.labels(worker=clean_name, timeframe=timeframe).set(value)

            # Worker shares
            worker_shares_accepted.labels(worker=clean_name)._value._value = worker_info.get('shares_diff_a', 0)
            worker_shares_rejected.labels(worker=clean_name)._value._value = worker_info.get('shares_diff_r', 0)

            # Worker last update time
            if 'lastupdate' in worker_info:
                worker_last_share.labels(worker=clean_name).set(worker_info['lastupdate'])

        # BCH Network difficulty and block finding calculations
        difficulty = fetch_bch_difficulty()
        if difficulty:
            bch_network_difficulty.set(difficulty)

            # Get best share and 1-minute hashrate for calculations
            best_share = data.get('bestshare', 0)
            hashrate_1min = data.get('u_hashrate1m', 0)

            # Calculate block progress percentage
            if difficulty > 0 and best_share > 0:
                progress_percent = (best_share / difficulty) * 100
                solomining_block_progress_percent.set(progress_percent)
                logger.info(f"Block progress: {progress_percent:.6f}% (best share: {best_share:,.0f})")
            else:
                solomining_block_progress_percent.set(0)

            # Calculate expected time to block and chances
            if hashrate_1min > 0:
                etb_seconds = calculate_expected_time_to_block(hashrate_1min, difficulty)
                solomining_expected_time_to_block_seconds.set(etb_seconds)

                # Calculate block chances for different time periods
                chance_daily = calculate_block_chance(etb_seconds, 86400)  # 1 day
                chance_weekly = calculate_block_chance(etb_seconds, 86400 * 7)  # 1 week
                chance_monthly = calculate_block_chance(etb_seconds, 86400 * 30)  # 1 month
                chance_yearly = calculate_block_chance(etb_seconds, 86400 * 365)  # 1 year

                solomining_block_chance_daily.set(chance_daily)
                solomining_block_chance_weekly.set(chance_weekly)
                solomining_block_chance_monthly.set(chance_monthly)
                solomining_block_chance_yearly.set(chance_yearly)

                # Log ETB in human-readable format
                etb_days = etb_seconds / 86400
                logger.info(f"Expected time to block: {etb_days:.1f} days ({chance_daily*100:.2f}% daily, {chance_weekly*100:.2f}% weekly, {chance_monthly*100:.2f}% monthly)")

        logger.info("Metrics updated successfully")

    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")
        raise


def collect_metrics() -> None:
    """
    Main collection loop - fetch data and update metrics.
    """
    start_time = time.time()

    try:
        data = fetch_mining_data()
        update_metrics(data)
        scrape_success.set(1)

    except Exception as e:
        logger.error(f"Scrape failed: {e}")
        scrape_success.set(0)

    finally:
        duration = time.time() - start_time
        scrape_duration.set(duration)
        logger.info(f"Scrape completed in {duration:.2f} seconds")


def main():
    """
    Main entry point - start HTTP server and collection loop.
    """
    logger.info(f"Starting Prometheus exporter on port {EXPORTER_PORT}")
    logger.info(f"Scrape interval: {SCRAPE_INTERVAL} seconds")
    logger.info(f"Monitoring BCH address: {BCH_ADDRESS}")

    # Start Prometheus HTTP server
    start_http_server(EXPORTER_PORT)
    logger.info(f"Metrics available at http://0.0.0.0:{EXPORTER_PORT}/metrics")

    # Initial collection
    collect_metrics()

    # Collection loop
    while True:
        try:
            time.sleep(SCRAPE_INTERVAL)
            collect_metrics()
        except KeyboardInterrupt:
            logger.info("Shutting down exporter")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            time.sleep(SCRAPE_INTERVAL)


if __name__ == '__main__':
    main()

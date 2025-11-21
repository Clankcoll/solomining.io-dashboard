# Grafana Dashboard Setup Guide

This guide will help you import and configure the BCH Solo Mining Dashboard in Grafana 12.

## Dashboard Overview

The dashboard includes:
- 🎯 **Block Progress Gauge** - How close you are to finding a block (0-100%)
- ⏰ **Expected Time to Block** - Statistical average in days
- 🎲 **Block Chances** - Daily, Weekly, Monthly, Yearly probabilities
- 👷 **Active Workers** - Number of workers currently mining
- 🌐 **BCH Network Difficulty** - Live network difficulty
- 🏆 **Best Share** - Your highest difficulty share
- 📈 **Total Hashrate** - Account hashrate over multiple timeframes
- 👷 **Worker Comparison** - Per-worker hashrate breakdown
- ✅ **Share Submission Rate** - Accepted vs rejected shares
- ❌ **Rejection Rate** - Track share quality
- 🍀 **Mining Luck Tracker** - Historical best share progress

## Method 1: Import Dashboard JSON (Recommended - Quick!)

### Step 1: Access Grafana
1. Open your browser and go to: `http://localhost:3000` (or your Grafana URL)
2. Log in (default: admin/admin)

### Step 2: Import the Dashboard
1. In the left sidebar, click **"Dashboards"** (4 squares icon)
2. Click **"New"** → **"Import"**
3. You have two options:

   **Option A: Upload JSON file**
   - Click **"Upload dashboard JSON file"**
   - Select `grafana-dashboard.json` from your project folder

   **Option B: Paste JSON**
   - Open `grafana-dashboard.json` in a text editor
   - Copy the entire contents
   - Paste into the "Import via dashboard JSON model" text box
   - Click **"Load"**

### Step 3: Configure the Dashboard
1. In the import screen, you'll see:
   - **Name**: "BCH Solo Mining Dashboard" (you can change this)
   - **Folder**: Select where to save it (or leave as "General")
   - **Prometheus**: Select your Prometheus datasource from the dropdown

2. Click **"Import"**

### Step 4: Done! 🎉
Your dashboard is now ready! It should automatically start showing data.

## Method 2: Build Dashboard Manually (Step-by-Step)

If you prefer to build it yourself or customize it:

### 1. Create New Dashboard
1. Go to **Dashboards** → **New** → **New Dashboard**
2. Click **"Add visualization"**

### 2. Add Block Progress Gauge
1. Click **"Add visualization"**
2. Select your **Prometheus** datasource
3. In the query box, enter: `solomining_block_progress_percent`
4. On the right panel:
   - **Panel Title**: "🎯 Block Progress"
   - **Visualization**: Select **"Gauge"**
   - Under **"Standard options"**:
     - Min: 0
     - Max: 100
     - Unit: Percent (0-100)
   - Under **"Thresholds"**:
     - 0: Red
     - 10: Orange
     - 50: Yellow
     - 90: Green
5. Click **"Apply"**

### 3. Add Expected Time to Block
1. Click **"Add"** → **"Visualization"**
2. Query: `solomining_expected_time_to_block_seconds / 86400`
3. Settings:
   - **Panel Title**: "⏰ Expected Time to Block"
   - **Visualization**: "Stat"
   - **Unit**: Select "time" → "days (d)"
4. Click **"Apply"**

### 4. Add Block Chance (Monthly)
1. Click **"Add"** → **"Visualization"**
2. Query: `solomining_block_chance_monthly * 100`
3. Settings:
   - **Panel Title**: "🎲 Block Chance (30 Days)"
   - **Visualization**: "Stat"
   - **Unit**: "Percent (0-100)"
   - **Color scheme**: Set thresholds (0=red, 20=yellow, 50=green)
4. Click **"Apply"**

### 5. Add Active Workers
1. Query: `solomining_account_workers`
2. Settings:
   - **Title**: "👷 Active Workers"
   - **Visualization**: "Stat"
   - **Unit**: "short"

### 6. Add Total Hashrate Graph
1. Query A: `solomining_account_hashrate{timeframe="1min"}`
   - Legend: "1 min"
2. Query B: `solomining_account_hashrate{timeframe="5min"}`
   - Legend: "5 min"
3. Query C: `solomining_account_hashrate{timeframe="1hr"}`
   - Legend: "1 hour"
4. Query D: `solomining_account_hashrate{timeframe="1day"}`
   - Legend: "1 day"
5. Settings:
   - **Title**: "📈 Total Hashrate"
   - **Visualization**: "Time series"
   - **Unit**: "Hashes/sec" (Hs)
   - **Legend**: Show as table with "Last" and "Mean" calculations

### 7. Add Worker Comparison
1. Query: `solomining_worker_hashrate{timeframe="1min"}`
2. Settings:
   - **Title**: "👷 Worker Hashrate Comparison"
   - **Visualization**: "Time series"
   - **Legend format**: `{{worker}} (1min)`
   - **Unit**: "Hashes/sec" (Hs)

### 8. Add Share Submission Rate
1. Query A: `rate(solomining_account_shares_accepted_total[5m])`
   - Legend: "Accepted"
2. Query B: `rate(solomining_account_shares_rejected_total[5m])`
   - Legend: "Rejected"
3. Settings:
   - **Title**: "✅ Share Submission Rate"
   - **Visualization**: "Time series"

### 9. Add Rejection Rate
1. Query:
   ```promql
   (rate(solomining_account_shares_rejected_total[5m]) /
    (rate(solomining_account_shares_accepted_total[5m]) +
     rate(solomining_account_shares_rejected_total[5m]))) * 100
   ```
2. Settings:
   - **Title**: "❌ Share Rejection Rate"
   - **Visualization**: "Time series"
   - **Unit**: "Percent (0-100)"
   - **Min**: 0
   - **Max**: 100

### 10. Add Mining Luck Tracker
1. Query: `solomining_block_progress_percent`
2. Settings:
   - **Title**: "🍀 Mining Luck Tracker - Best Share vs Network Difficulty"
   - **Visualization**: "Time series"
   - **Unit**: "Percent (0-100)"
   - This shows your historical best shares over time

### 11. Save Dashboard
1. Click the **Save** icon (💾) in the top right
2. Give it a name: "BCH Solo Mining Dashboard"
3. Click **"Save"**

## Dashboard Configuration

### Time Range
- Default: Last 6 hours
- You can change this in the top right corner
- Recommended: 6h-24h for active monitoring, 7d for trends

### Auto-Refresh
- The dashboard auto-refreshes every 30 seconds
- You can change this in the top right (click the refresh dropdown)
- Options: 5s, 10s, 30s, 1m, 5m, etc.

### Panel Arrangement
The panels are organized in this layout:
```
Row 1: Block Progress | ETB | Monthly Chance | Workers | Network Diff | Best Share
Row 2: Block Chances (Daily | Weekly | Yearly)
Row 3: Total Hashrate | Worker Comparison
Row 4: Share Rate | Rejection Rate
Row 5: Mining Luck Tracker (full width)
```

## Customization Tips

### Change Colors
1. Click panel title → **Edit**
2. Go to **"Overrides"** or **"Thresholds"**
3. Adjust color ranges

### Adjust Time Ranges
- Some queries use `[5m]` for rate calculations
- You can change this to `[1m]`, `[10m]`, etc. for different granularity

### Add Alerts
1. Edit any panel
2. Click **"Alert"** tab
3. Create alert rules (e.g., alert if hashrate drops below threshold)

### Change Units
- Hashrate: Hs, KHs, MHs, GHs, THs
- Time: seconds, minutes, hours, days
- Percent: 0-100 or 0.0-1.0

## Troubleshooting

### "No data" showing
1. Check that Prometheus is scraping the exporter:
   - Go to `http://localhost:9090/targets`
   - Look for your `solomining` job - should be "UP"
2. Verify exporter is running: `docker-compose ps`
3. Check metrics are available: `curl http://localhost:9123/metrics`

### Wrong datasource
1. Click dashboard settings (⚙️ icon)
2. Go to **"Variables"**
3. Edit `DS_PROMETHEUS`
4. Select correct Prometheus datasource

### Panels not showing correctly
1. Edit the panel
2. Check the query is valid
3. Try running the query in Prometheus directly: `http://localhost:9090`

### Values seem wrong
- Hashrate should be in the trillions (TH/s range)
- Block progress should be very small (< 1% usually)
- Block chances should be reasonable percentages

## What Each Panel Tells You

### 🎯 Block Progress (0-100%)
- **What it is**: Your best share as % of network difficulty
- **When 100%+**: You found a block! 🎉
- **Typical value**: 0.0001% - 0.01% (very small)
- **Color guide**:
  - Red (0-10%): Just starting
  - Orange (10-50%): Getting warmer
  - Yellow (50-90%): Very close!
  - Green (90-100%): Almost there!

### ⏰ Expected Time to Block
- **What it is**: Statistical average time until you find a block
- **Based on**: Your current hashrate vs network difficulty
- **Note**: This is AVERAGE - you could find one tomorrow or in 3 months

### 🎲 Block Chances
- **Daily**: Probability in next 24 hours
- **Weekly**: Probability in next 7 days
- **Monthly**: Probability in next 30 days (most useful)
- **Yearly**: Probability in next 365 days
- **Example**: 3% daily = you have 3% chance each day

### 👷 Active Workers
- Should match your mining rigs
- If this drops, a worker went offline

### 📈 Total Hashrate
- Shows your mining power over time
- Multiple timeframes to see short/long-term trends
- Spikes = good, dips = investigate

### 👷 Worker Comparison
- Compare performance of Apollo2 vs NerdQaxe++-Home1
- Identify underperforming workers
- Plan upgrades/troubleshooting

### ✅ Share Submission Rate
- How many shares you're submitting per minute
- Higher hashrate = more shares
- Accepted should be >> Rejected

### ❌ Rejection Rate
- Should be < 1% ideally
- High rate = network/config issues
- Troubleshoot if > 5%

### 🍀 Mining Luck Tracker
- Historical view of your best shares
- If line spikes high = you got lucky!
- Helps visualize how close you've been to a block

## Next Steps

1. **Watch for patterns** - Understand your normal hashrate
2. **Set up alerts** - Get notified if hashrate drops
3. **Monitor luck** - See your best shares over time
4. **Share with friends** - Show off your dashboard! 📊

Enjoy your mining dashboard! 🚀

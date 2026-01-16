# 🚀 Quick Start Guide

## Get Started in 3 Minutes

### Option 1: Automated Setup (Recommended)

```bash
# Run the setup script
chmod +x setup.sh
./setup.sh

# Launch the dashboard
streamlit run app.py
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Generate data
python generate_location_data.py

# Run queries
python queries.py

# Perform spatial analysis
python spatial_analysis.py

# Launch dashboard
streamlit run app.py
```

### Option 3: View the Live Demo

**🌐 Live Dashboard**: [YOUR_URL_HERE]

---

## What You'll See

### 📍 Page 1: Overview Map
- Interactive heatmap with 50K+ events
- City markers sized by user count
- Real-time filters (date, event type, city)

### 📈 Page 2: Regional Analytics
- Bar charts: Users and events by city
- Line chart: Daily engagement trends
- Table: Top 10 active locations

### 🎯 Page 3: Retention Analysis
- D1, D7, D30 retention by city
- Engagement vs retention scatter plots
- Key insights and recommendations

### 📱 Page 4: Event Distribution
- Pie chart: Event types breakdown
- Histogram: Session duration distribution
- Line charts: Hourly and weekly patterns

---

## Key Commands

```bash
# Generate fresh data
python generate_location_data.py

# View analytics in terminal
python queries.py

# Run spatial analysis
python spatial_analysis.py

# Launch dashboard locally
streamlit run app.py

# Deploy to Streamlit Cloud
# See DEPLOYMENT.md for details
```

---

## Files Overview

| File | Description | Size |
|------|-------------|------|
| `app.py` | Main Streamlit dashboard | 24 KB |
| `generate_location_data.py` | Data generation script | 9 KB |
| `queries.py` | DuckDB analytics | 13 KB |
| `spatial_analysis.py` | Geospatial analysis | 14 KB |
| `location_events.csv` | Event data (50K rows) | 4.4 MB |
| `location_events.geojson` | Geo-enabled events | 17 MB |
| `hex_analysis.geojson` | H3 hexagonal bins | 222 KB |
| `location_analytics.duckdb` | DuckDB database | 6.6 MB |

---

## System Requirements

- **Python**: 3.9 or higher
- **RAM**: 2 GB minimum
- **Storage**: 50 MB for code + data
- **OS**: Windows, macOS, or Linux

---

## Troubleshooting

### Dashboard won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Try again
streamlit run app.py
```

### Import errors
```bash
# Install missing packages
pip install pandas numpy geopandas duckdb streamlit plotly folium h3
```

### Data files missing
```bash
# Regenerate data
python generate_location_data.py
python queries.py
python spatial_analysis.py
```

### Port already in use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

---

## Next Steps

1. ✅ Run the setup
2. ✅ Explore the dashboard locally
3. ✅ Review the analysis findings (ANALYSIS.md)
4. ✅ Deploy to Streamlit Cloud (DEPLOYMENT.md)
5. ✅ Add to your portfolio
6. ✅ Share on LinkedIn!

---

## Documentation

- **README.md** - Full project documentation
- **ANALYSIS.md** - Detailed findings and insights
- **DEPLOYMENT.md** - Cloud deployment guide
- **requirements.txt** - Python dependencies

---

## Support

Found a bug or have a question?
- Open an issue on GitHub
- Review the documentation
- Check Streamlit forums

---

**Ready to get started? Run `./setup.sh` now!** 🚀

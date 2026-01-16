# 🚀 Deployment Guide - Streamlit Cloud

This guide walks you through deploying your Location Analytics dashboard to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free - sign up at share.streamlit.io)
- Project pushed to GitHub

## Step 1: Prepare Your Repository

### 1.1 Generate Data Files

Since Streamlit Cloud doesn't persist data between runs, generate all data files locally and commit them:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate all data
python generate_location_data.py
python queries.py
python spatial_analysis.py

# Check generated files
ls -lh *.csv *.geojson *.json *.duckdb
```

You should see:
- `location_events.csv` (~5 MB)
- `location_events.geojson` (~8 MB)
- `hex_analysis.geojson` (~2 MB)
- `hotspots.geojson` (~500 KB)
- `spatial_summary.json` (~1 KB)
- `data_summary.json` (~1 KB)
- `location_analytics.duckdb` (~3 MB)

### 1.2 Update .gitignore

Make sure data files are NOT ignored:

```bash
# Edit .gitignore and comment out these lines if present:
# *.csv
# *.geojson
# *.duckdb
# *.json
```

### 1.3 Commit and Push

```bash
git add .
git commit -m "Add generated data files for deployment"
git push origin main
```

## Step 2: Deploy on Streamlit Cloud

### 2.1 Create New App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app" button
3. Select your repository
4. Configure deployment:
   - **Repository**: your-username/location-analytics
   - **Branch**: main
   - **Main file path**: app.py
   - **App URL**: choose a custom subdomain (e.g., `location-analytics-demo`)

### 2.2 Advanced Settings (Optional)

Click "Advanced settings" if you need to configure:

- **Python version**: 3.9 or higher
- **Secrets**: Not needed for this project
- **Environment variables**: None required

### 2.3 Deploy

1. Click "Deploy!"
2. Wait 3-5 minutes for initial deployment
3. Watch the build logs for any errors

### 2.4 Verify Deployment

Your app should be live at:
```
https://your-app-name.streamlit.app
```

Test all pages:
- ✓ Overview Map loads with heatmap
- ✓ Regional Analytics shows charts
- ✓ Retention Analysis displays metrics
- ✓ Event Distribution shows patterns

## Step 3: Update README

Update the README.md with your live URL:

```markdown
## 🚀 Live Demo

**[View Live Dashboard →](https://your-app-name.streamlit.app)**
```

Commit and push:
```bash
git add README.md
git commit -m "Add live demo URL"
git push
```

## Troubleshooting

### Issue: "File not found" errors

**Solution**: Make sure all data files are committed to git:
```bash
git status
git add *.csv *.geojson *.json *.duckdb
git commit -m "Add missing data files"
git push
```

### Issue: "Module not found" errors

**Solution**: Check requirements.txt includes all dependencies:
```bash
# Locally test with fresh environment
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Issue: App crashes on startup

**Solution**: Check Streamlit Cloud logs:
1. Go to your app's dashboard
2. Click "Manage app"
3. View logs for error messages
4. Common fixes:
   - Update package versions in requirements.txt
   - Check file paths (use relative paths)
   - Verify data files are present

### Issue: Memory errors

**Solution**: Streamlit Cloud free tier has 1GB RAM. Optimize:
```python
# In app.py, add caching
@st.cache_data
def load_event_data():
    return pd.read_csv('location_events.csv')

# Sample data for map
df_sample = df.sample(n=5000, random_state=42)
```

### Issue: Slow loading

**Solution**: 
1. Reduce data size for demo
2. Add loading spinners:
```python
with st.spinner('Loading data...'):
    df = load_event_data()
```

## Step 4: Share Your Dashboard

### Add to README

```markdown
## 🚀 Live Demo

**[View Live Dashboard](https://your-app-name.streamlit.app)** - Deployed on Streamlit Cloud

![Dashboard Preview](https://i.imgur.com/your-screenshot.png)
```

### Share on Social Media

LinkedIn post template:
```
🗺️ Just launched my Location-Based Analytics Dashboard!

Built with:
- Python + DuckDB for fast analytics
- GeoPandas + H3 for geospatial analysis
- Streamlit + Folium for interactive viz
- 50K+ synthetic events across 5 cities

Features:
✅ Interactive heatmaps
✅ Retention analysis
✅ Hexagonal binning
✅ Engagement metrics

Live demo: https://your-app-name.streamlit.app
GitHub: https://github.com/your-username/location-analytics

#DataScience #Geospatial #Analytics #Python
```

### Add Badges to README

```markdown
![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)
[![GitHub](https://img.shields.io/github/stars/your-username/location-analytics?style=social)](https://github.com/your-username/location-analytics)
```

## Step 5: Monitor and Maintain

### Check Analytics

Streamlit Cloud provides basic analytics:
- View count
- Unique visitors
- Load times

Access at: `https://share.streamlit.io/[username]/[repo]/[branch]/app.py/analytics`

### Update App

To update your deployed app:
```bash
# Make changes locally
git add .
git commit -m "Update: feature description"
git push
```

Streamlit Cloud auto-deploys on push to main branch.

### Reboot App

If app becomes unresponsive:
1. Go to Streamlit Cloud dashboard
2. Click "Manage app"
3. Click "Reboot app"

## Alternative: Deploy with Docker

If you prefer Docker deployment:

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy to Cloud Run, Railway, or Heroku

Follow platform-specific Docker deployment guides.

## Cost Comparison

| Platform | Free Tier | Cost After |
|----------|-----------|------------|
| Streamlit Cloud | ✅ 1 GB RAM, 1 CPU | $20/month (Pro) |
| Railway | ✅ $5 free credit | $5+ usage-based |
| Heroku | ❌ No free tier | $7+/month |
| Cloud Run | ✅ 2M requests/month | Usage-based |

**Recommendation**: Start with Streamlit Cloud free tier for portfolio projects.

## Success Checklist

- [ ] All data files committed to git
- [ ] requirements.txt is complete
- [ ] App runs locally without errors
- [ ] Deployed to Streamlit Cloud
- [ ] All 4 pages working correctly
- [ ] Filters and interactions functional
- [ ] README updated with live URL
- [ ] Screenshots added to repo
- [ ] Shared on LinkedIn/portfolio

## Support

If you encounter issues:
1. Check [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
2. Visit [Streamlit Forum](https://discuss.streamlit.io/)
3. Review [Common Errors Guide](https://docs.streamlit.io/knowledge-base/deploy)

---

**Happy deploying! 🚀**

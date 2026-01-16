# 🚀 Deployment Guide - Render (24/7 Uptime)

## Why Render Over Streamlit Cloud?

| Feature | Render Free | Streamlit Cloud Free |
|---------|-------------|---------------------|
| **Uptime** | ✅ 24/7 | ❌ Sleeps after inactivity |
| **Monthly Hours** | 750 hours | Unlimited (but sleeps) |
| **Cold Starts** | Minimal | Frequent |
| **Performance** | Better | Good |
| **Custom Domain** | ✅ Yes | ❌ No |
| **HTTPS** | ✅ Automatic | ✅ Automatic |

**Recommendation:** Use Render for portfolio projects you want always available.

---

## Step-by-Step Render Deployment

### Prerequisites
- GitHub account
- Render account (sign up free at render.com)
- Project pushed to GitHub

---

## Part 1: Prepare Your Repository

### 1. Update requirements.txt

Make sure you have the exact versions that work:

```txt
pandas==2.1.4
numpy==1.26.2
geopandas==0.14.1
shapely==2.0.2
duckdb==0.9.2
h3==3.7.6
folium==0.15.1
streamlit==1.29.0
streamlit-folium==0.16.0
plotly==5.18.0
pyarrow==14.0.1
```

### 2. Add render.yaml to your repo

The `render.yaml` file is already created. This tells Render how to deploy your app.

### 3. Ensure data files are in repo

```bash
# Make sure these files are committed:
git add location_events.csv
git add location_events.geojson
git add hex_analysis.geojson
git add hotspots.geojson
git add location_analytics.duckdb
git add data_summary.json
git add spatial_summary.json

git commit -m "Add data files for deployment"
git push
```

### 4. Create .python-version file (Optional)

```bash
echo "3.9.16" > .python-version
git add .python-version
git commit -m "Add Python version specification"
git push
```

---

## Part 2: Deploy on Render

### Step 1: Sign Up for Render

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest method)
4. Authorize Render to access your repositories

### Step 2: Create New Web Service

1. **Click "New +" button** (top right)
2. Select **"Web Service"**
3. **Connect your GitHub repository**
   - If first time: Click "Connect GitHub"
   - Select your `location-analytics` repository
   - Click "Connect"

### Step 3: Configure Your Service

Fill in the deployment settings:

**Basic Settings:**
- **Name:** `location-analytics` (or your preferred name)
- **Region:** Choose closest to your target audience
  - Oregon (US West)
  - Ohio (US East)
  - Frankfurt (Europe)
  - Singapore (Asia)
- **Branch:** `main` (or your default branch)
- **Root Directory:** Leave blank (unless your app is in a subdirectory)

**Build Settings:**
- **Runtime:** Python 3
- **Build Command:** 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command:**
  ```bash
  streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
  ```

**Plan:**
- Select **"Free"** (750 hours/month, plenty for 24/7)

### Step 4: Environment Variables (Optional)

If you need any environment variables, add them here. For this project, none are required.

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Render will start building your app
3. Watch the build logs (this takes 3-5 minutes first time)
4. Wait for "Deploy live" message

### Step 6: Get Your Live URL

Once deployed, you'll get a URL like:
```
https://location-analytics-xxxx.onrender.com
```

This is your **permanent, 24/7 accessible** dashboard!

---

## Part 3: Verify Deployment

### Test Your App

1. **Open the Render URL** in your browser
2. **Test all 4 pages:**
   - ✅ Overview Map loads with heatmap
   - ✅ Regional Analytics shows charts
   - ✅ Retention Analysis displays correctly
   - ✅ Event Distribution works
3. **Test filters:**
   - Date range selection
   - Event type filtering
   - City filtering
4. **Test on mobile** - check responsiveness

### Common First-Time Issues

**Issue: Build fails with "No module named 'X'"**
```bash
# Solution: Add missing package to requirements.txt
echo "missing-package==version" >> requirements.txt
git commit -am "Add missing dependency"
git push
# Render auto-redeploys
```

**Issue: App runs but maps don't load**
```bash
# Solution: Check data files are in repo
git add *.csv *.geojson *.json *.duckdb
git commit -m "Add data files"
git push
```

**Issue: App crashes on startup**
```bash
# Solution: Check Render logs
# Go to your service > Logs tab
# Look for Python tracebacks
# Fix the error and push
```

**Issue: "Port not found"**
```bash
# Solution: Start command must use $PORT
# Correct:
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Part 4: Custom Domain (Optional)

### Free Custom Domain Setup

1. Go to your service **Settings**
2. Scroll to **Custom Domain**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `maps-analytics.yourdomain.com`)
5. Add the CNAME record to your DNS provider
6. Wait for DNS propagation (up to 24 hours)
7. Render automatically provisions SSL certificate

---

## Part 5: Monitoring & Maintenance

### Check Service Health

**Render Dashboard shows:**
- Deploy status (live/building/failed)
- Resource usage (RAM, CPU)
- Request count
- Error rate
- Build history

### View Logs

```
Your Service > Logs tab
```

See:
- Application logs
- Error messages
- Request logs
- Build output

### Auto-Deploy on Push

Render automatically deploys when you push to your branch:

```bash
# Make changes locally
git add .
git commit -m "Update dashboard styling"
git push

# Render automatically:
# 1. Detects the push
# 2. Runs build command
# 3. Deploys new version
# 4. Zero downtime switch
```

---

## Part 6: Performance Optimization

### For Faster Rendering

**1. Streamlit Caching**

Already implemented in `app.py`:
```python
@st.cache_data
def load_event_data():
    return pd.read_csv('location_events.csv')
```

**2. Reduce Data Size for Demo**

If app is slow, reduce data:
```python
# In generate_location_data.py
NUM_EVENTS = 25000  # Instead of 50000
```

**3. Sample Data for Maps**

Already implemented:
```python
# Only show 5000 points on heatmap
df_sample = df.sample(n=5000, random_state=42)
```

### Free Tier Limits

- **750 hours/month** = 31.25 days (more than enough for 24/7)
- **512 MB RAM** (sufficient for this app)
- **0.1 CPU** (shared, adequate)
- **Sleeps after 15 min inactivity** ❌ WAIT, this changed!

**UPDATE:** Render free tier NOW sleeps after inactivity (as of 2023). For true 24/7, you need:

### Option 1: Keep It Awake (Free Solutions)

**Use UptimeRobot:**
1. Sign up at https://uptimerobot.com (free)
2. Add your Render URL as a monitor
3. Set check interval: Every 5 minutes
4. UptimeRobot pings your app, keeping it awake

**Use Cron-job.org:**
1. Go to https://cron-job.org (free)
2. Create account
3. Add cronjob to ping your URL every 5 minutes
4. Prevents sleep

### Option 2: Paid Render ($7/month)

Upgrade to "Starter" plan for:
- ✅ True 24/7 uptime (no sleep)
- ✅ More resources
- ✅ Faster performance

---

## Part 7: Update Documentation

### Update README.md

Replace Streamlit Cloud section with:

```markdown
## 🚀 Live Demo

**[View Live Dashboard →](https://location-analytics-xxxx.onrender.com)**

Hosted on Render with 24/7 uptime.
```

### Add Badge

```markdown
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
```

---

## Alternative: Railway (Another Good Option)

### Railway vs Render

| Feature | Railway Free | Render Free |
|---------|--------------|-------------|
| Hours/month | 500 | 750 |
| Sleep behavior | Yes | Yes |
| Performance | Excellent | Excellent |
| Setup | Easier | Easy |

**Railway Deploy:**
1. Go to railway.app
2. "New Project" > "Deploy from GitHub"
3. Select repo
4. Railway auto-detects Streamlit
5. Deploy

---

## Comparison: All Options

| Platform | Free Tier | 24/7 True? | Setup Difficulty |
|----------|-----------|------------|------------------|
| **Render + UptimeRobot** | ✅ | ✅ | Medium |
| **Railway + UptimeRobot** | ✅ | ✅ | Easy |
| **Streamlit Cloud** | ✅ | ❌ | Easiest |
| **Heroku** | ❌ | N/A | Medium |
| **Google Cloud Run** | ✅ Limited | ✅ | Hard |

**My Recommendation:**

1. **For Portfolio (24/7 required):** Render + UptimeRobot
2. **For Quick Demo:** Streamlit Cloud (accepts sleep)
3. **For Production:** Paid Render ($7/mo)

---

## Full Deployment Checklist

- [ ] Create GitHub repository
- [ ] Push all code and data files
- [ ] Add render.yaml to repo
- [ ] Sign up for Render account
- [ ] Create new Web Service
- [ ] Configure build and start commands
- [ ] Deploy and wait for "Deploy live"
- [ ] Test all features
- [ ] Set up UptimeRobot (for 24/7)
- [ ] Add custom domain (optional)
- [ ] Update README with live URL
- [ ] Share on LinkedIn!

---

## Troubleshooting Guide

### Build Fails

**Check Python version:**
```bash
# Add to repo
echo "3.9.16" > .python-version
```

**Check requirements.txt:**
```bash
# All packages must have versions
pandas==2.1.4  # ✅ Good
pandas         # ❌ Bad (no version)
```

### App Runs But Has Errors

**Check logs:**
- Render Dashboard > Your Service > Logs
- Look for Python tracebacks
- Common issues: File not found, import errors

**File paths:**
```python
# Use relative paths
df = pd.read_csv('location_events.csv')  # ✅
df = pd.read_csv('/home/user/data.csv')  # ❌
```

### App Is Slow

**Options:**
1. Reduce data size (25K instead of 50K events)
2. Upgrade to paid tier ($7/mo)
3. Optimize caching in Streamlit

---

## Support Resources

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **Streamlit Docs:** https://docs.streamlit.io
- **This Project:** See README.md and other docs

---

## Next Steps After Deployment

1. ✅ Set up UptimeRobot for 24/7 availability
2. ✅ Test thoroughly on different devices
3. ✅ Update README with live URL
4. ✅ Add to your portfolio website
5. ✅ Share on LinkedIn
6. ✅ Monitor logs for errors
7. ✅ Respond to feedback

---

**Your dashboard will be live 24/7 at your Render URL! 🎉**

**Typical URL format:** `https://location-analytics-xxxx.onrender.com`

Good luck with your deployment!

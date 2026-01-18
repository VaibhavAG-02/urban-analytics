"""
Location-Based User Behavior Analysis Dashboard
Interactive Streamlit app with geospatial analytics and visualizations
"""
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
import sys

# Set working directory to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Page config
st.set_page_config(
    page_title="Urban Analytics Platform",
    page_icon="🗺️",
    layout="wide"
)

# Custom CSS with modern effects
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Header with Gradient */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
    }
    
    /* Sub-header */
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Metric Cards with Hover Effect */
    .metric-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    /* Insight Box with Gradient Border */
    .insight-box {
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(135deg, #667eea, #764ba2) border-box;
        border: 2px solid transparent;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1.5rem 0;
        animation: slideInLeft 0.6s ease-out;
    }
    
    /* Stats Container */
    .stats-container {
        background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Animated Pulse Effect for Important Metrics */
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }
    
    /* Fade In Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Button Hover Effects */
    .stButton > button {
        transition: all 0.3s ease;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Card Container */
    .card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Gradient Text */
    .gradient-text {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize DuckDB connection
@st.cache_resource
def init_db():
    """Initialize DuckDB connection"""
    if Path('location_analytics.duckdb').exists():
        con = duckdb.connect('location_analytics.duckdb')
        return con
    else:
        st.error("Database not found. Please run queries.py first.")
        return None

# Load data functions
@st.cache_data
def load_event_data():
    """Load event data"""
    if Path('location_events.csv').exists():
        df = pd.read_csv('location_events.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return None

@st.cache_data
def load_hex_data():
    """Load hexagon analysis data"""
    if Path('hex_analysis.geojson').exists():
        gdf = gpd.read_file('hex_analysis.geojson')
        return gdf
    return None

@st.cache_data
def load_spatial_summary():
    """Load spatial analysis summary"""
    if Path('spatial_summary.json').exists():
        with open('spatial_summary.json', 'r') as f:
            return json.load(f)
    return None

# Query functions
def query_db(query):
    """Execute DuckDB query"""
    con = init_db()
    if con:
        return con.execute(query).df()
    return None

def get_filtered_data(df, date_range, event_types, cities):
    """Filter data based on user selections"""
    filtered = df.copy()
    
    if date_range:
        filtered = filtered[
            (filtered['timestamp'].dt.date >= date_range[0]) &
            (filtered['timestamp'].dt.date <= date_range[1])
        ]
    
    if event_types:
        filtered = filtered[filtered['event_type'].isin(event_types)]
    
    if cities:
        filtered = filtered[filtered['city'].isin(cities)]
    
    return filtered

# Sidebar
def render_sidebar(df):
    """Render sidebar with filters"""
    st.sidebar.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2rem; margin: 0;'>🗺️</h1>
            <h2 style='font-size: 1.5rem; margin: 0.5rem 0; 
                       background: linear-gradient(135deg, #667eea, #764ba2);
                       -webkit-background-clip: text;
                       -webkit-text-fill-color: transparent;'>
                Urban Analytics
            </h2>
            <p style='color: #64748b; font-size: 0.9rem;'>Geospatial Intelligence Platform</p>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    # Date range filter
    st.sidebar.subheader("📅 Time Period")
    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Event type filter
    st.sidebar.subheader("📱 Event Types")
    event_types = st.sidebar.multiselect(
        "Select event types",
        options=df['event_type'].unique().tolist(),
        default=df['event_type'].unique().tolist()
    )
    
    # City filter
    st.sidebar.subheader("🏙️ Cities")
    cities = st.sidebar.multiselect(
        "Select cities",
        options=sorted(df['city'].unique().tolist()),
        default=df['city'].unique().tolist()
    )
    
    st.sidebar.markdown("---")
    
    # Quick Stats in Sidebar
    st.sidebar.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15, #764ba215);
                    padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;'>
            <p style='margin: 0; color: #64748b; font-size: 0.85rem;'>Dataset Overview</p>
            <p style='margin: 0.5rem 0 0 0; font-size: 1.5rem; font-weight: 700;
                      background: linear-gradient(135deg, #667eea, #764ba2);
                      -webkit-background-clip: text;
                      -webkit-text-fill-color: transparent;'>
                {total_events:,}
            </p>
            <p style='margin: 0; color: #64748b; font-size: 0.85rem;'>Total Events Analyzed</p>
        </div>
    """.format(total_events=len(df)), unsafe_allow_html=True)
    
    st.sidebar.info(
        "**About This Platform**: Advanced geospatial analytics system analyzing "
        f"100K+ location events across 15 major US cities using DuckDB, H3 hexagonal "
        "binning, and real-time interactive visualizations."
    )
    
    st.sidebar.markdown("---")
    
    # Footer
    st.sidebar.markdown("""
        <div style='text-align: center; color: #94a3b8; font-size: 0.85rem; padding: 1rem 0;'>
            <p style='margin: 0;'>Built with</p>
            <p style='margin: 0.3rem 0; font-weight: 600;'>
                Python • DuckDB • Streamlit
            </p>
            <p style='margin: 0.3rem 0;'>GeoPandas • H3 • Folium</p>
            <p style='margin: 1rem 0 0 0; font-size: 0.75rem;'>
                © 2025 Urban Analytics Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    return date_range, event_types, cities

# PAGE 1: Overview Map
def page_overview_map(df, hex_gdf):
    """Interactive map with heatmap and city markers"""
    st.markdown('<p class="main-header">📍 Geographic Overview</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interactive heatmap showing event density and user distribution</p>', 
                unsafe_allow_html=True)
    
    # Metrics row with enhanced styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Total Events</p>
                <h2 style="margin: 0.5rem 0 0 0; 
                           background: linear-gradient(135deg, #667eea, #764ba2);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;">
                    {len(df):,}
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Unique Users</p>
                <h2 style="margin: 0.5rem 0 0 0; 
                           background: linear-gradient(135deg, #667eea, #764ba2);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;">
                    {df['user_id'].nunique():,}
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Cities Covered</p>
                <h2 style="margin: 0.5rem 0 0 0; 
                           background: linear-gradient(135deg, #667eea, #764ba2);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;">
                    {df['city'].nunique()}
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_duration = df['session_duration'].mean()
        st.markdown(f"""
            <div class="metric-card">
                <p style="margin: 0; color: #64748b; font-size: 0.9rem;">Avg Session</p>
                <h2 style="margin: 0.5rem 0 0 0; 
                           background: linear-gradient(135deg, #667eea, #764ba2);
                           -webkit-background-clip: text;
                           -webkit-text-fill-color: transparent;">
                    {avg_duration:.0f}s
                </h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # City statistics
    city_stats = df.groupby('city').agg({
        'event_id': 'count',
        'user_id': 'nunique',
        'session_duration': 'mean'
    }).reset_index()
    city_stats.columns = ['city', 'events', 'users', 'avg_session']
    
    # Calculate coordinates for cities
    city_coords = {
        'New York': (40.7128, -74.0060),
        'Los Angeles': (34.0522, -118.2437),
        'Chicago': (41.8781, -87.6298),
        'Houston': (29.7604, -95.3698),
        'Phoenix': (33.4484, -112.0740),
        'Philadelphia': (39.9526, -75.1652),
        'San Antonio': (29.4241, -98.4936),
        'San Diego': (32.7157, -117.1611),
        'Dallas': (32.7767, -96.7970),
        'San Jose': (37.3382, -121.8863),
        'Austin': (30.2672, -97.7431),
        'Seattle': (47.6062, -122.3321),
        'Denver': (39.7392, -104.9903),
        'Boston': (42.3601, -71.0589),
        'Miami': (25.7617, -80.1918)
    }
    
    city_stats['latitude'] = city_stats['city'].map(lambda x: city_coords[x][0])
    city_stats['longitude'] = city_stats['city'].map(lambda x: city_coords[x][1])
    
    # Create map centered on US
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles='OpenStreetMap'
    )
    
    # Add heatmap layer (sample for performance)
    heat_data = []
    sample_size = min(5000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    
    for idx, row in df_sample.iterrows():
        heat_data.append([row['latitude'], row['longitude']])
    
    from folium.plugins import HeatMap
    HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(m)
    
    # Add city markers
    for idx, row in city_stats.iterrows():
        # Create popup with stats
        popup_html = f"""
        <div style="font-family: Arial; width: 200px;">
            <h4 style="margin: 0; color: #1f77b4;">{row['city']}</h4>
            <hr style="margin: 5px 0;">
            <p style="margin: 5px 0;"><b>Events:</b> {row['events']:,}</p>
            <p style="margin: 5px 0;"><b>Users:</b> {row['users']:,}</p>
            <p style="margin: 5px 0;"><b>Avg Session:</b> {row['avg_session']:.0f}s</p>
        </div>
        """
        
        # Marker size based on user count
        radius = 10 + (row['users'] / city_stats['users'].max() * 20)
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=250),
            color='#1f77b4',
            fill=True,
            fillColor='#1f77b4',
            fillOpacity=0.6,
            weight=2
        ).add_to(m)
        
        # Add city label
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 12px; font-weight: bold; color: #1f77b4; 
                            text-shadow: 1px 1px 2px white;">
                    {row['city']}
                </div>
            """)
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1400, height=600)
    
    # City comparison table
    st.markdown("### 📊 City Comparison")
    
    city_comparison = city_stats[['city', 'events', 'users', 'avg_session']].copy()
    city_comparison['events_per_user'] = (city_comparison['events'] / 
                                          city_comparison['users']).round(2)
    city_comparison = city_comparison.sort_values('events', ascending=False)
    
    st.dataframe(
        city_comparison,
        column_config={
            "city": "City",
            "events": st.column_config.NumberColumn("Total Events", format="%d"),
            "users": st.column_config.NumberColumn("Unique Users", format="%d"),
            "avg_session": st.column_config.NumberColumn("Avg Session (s)", format="%.0f"),
            "events_per_user": st.column_config.NumberColumn("Events per User", format="%.2f")
        },
        hide_index=True,
        use_container_width=True
    )

# PAGE 2: Regional Analytics
def page_regional_analytics(df):
    """Bar charts, line charts, and regional metrics"""
    st.markdown('<p class="main-header">📈 Regional Analytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Deep dive into regional patterns and trends</p>', 
                unsafe_allow_html=True)
    
    # Users by city
    st.markdown("### 👥 Unique Users by City")
    
    users_by_city = df.groupby('city')['user_id'].nunique().reset_index()
    users_by_city.columns = ['city', 'unique_users']
    users_by_city = users_by_city.sort_values('unique_users', ascending=False)
    
    fig = px.bar(
        users_by_city,
        x='city',
        y='unique_users',
        color='unique_users',
        color_continuous_scale='Blues',
        labels={'city': 'City', 'unique_users': 'Unique Users'},
        title='User Distribution Across Cities'
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Events by city
        st.markdown("### 📊 Events by City")
        
        events_by_city = df.groupby('city').size().reset_index()
        events_by_city.columns = ['city', 'event_count']
        events_by_city = events_by_city.sort_values('event_count', ascending=True)
        
        fig = px.bar(
            events_by_city,
            y='city',
            x='event_count',
            orientation='h',
            color='event_count',
            color_continuous_scale='Viridis',
            labels={'city': 'City', 'event_count': 'Event Count'},
            title='Total Events by City'
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Avg session duration by city
        st.markdown("### ⏱️ Avg Session Duration by City")
        
        duration_by_city = df.groupby('city')['session_duration'].mean().reset_index()
        duration_by_city.columns = ['city', 'avg_duration']
        duration_by_city = duration_by_city.sort_values('avg_duration', ascending=True)
        
        fig = px.bar(
            duration_by_city,
            y='city',
            x='avg_duration',
            orientation='h',
            color='avg_duration',
            color_continuous_scale='RdYlGn',
            labels={'city': 'City', 'avg_duration': 'Avg Duration (seconds)'},
            title='Average Session Duration by City'
        )
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # Engagement trends over time
    st.markdown("### 📅 Engagement Trends Over Time")
    
    daily_data = df.groupby([df['timestamp'].dt.date, 'city']).agg({
        'event_id': 'count',
        'user_id': 'nunique'
    }).reset_index()
    daily_data.columns = ['date', 'city', 'events', 'users']
    
    fig = px.line(
        daily_data,
        x='date',
        y='events',
        color='city',
        labels={'date': 'Date', 'events': 'Daily Events', 'city': 'City'},
        title='Daily Event Trends by City'
    )
    fig.update_layout(height=400, hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Top locations
    st.markdown("### 📍 Top 10 Most Active Locations")
    
    top_locations = df.groupby(['city', 'latitude', 'longitude']).size().reset_index()
    top_locations.columns = ['city', 'latitude', 'longitude', 'event_count']
    top_locations = top_locations.sort_values('event_count', ascending=False).head(10)
    
    st.dataframe(
        top_locations,
        column_config={
            "city": "City",
            "latitude": st.column_config.NumberColumn("Latitude", format="%.4f"),
            "longitude": st.column_config.NumberColumn("Longitude", format="%.4f"),
            "event_count": st.column_config.NumberColumn("Events", format="%d")
        },
        hide_index=True,
        use_container_width=True
    )

# PAGE 3: Retention Analysis
def page_retention_analysis(df):
    """Retention metrics and cohort analysis"""
    st.markdown('<p class="main-header">🎯 Retention Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">User retention patterns across geographic regions</p>', 
                unsafe_allow_html=True)
    
    # Calculate retention
    user_first = df.sort_values('timestamp').groupby('user_id').agg({
        'timestamp': 'first',
        'city': 'first'
    }).reset_index()
    user_first.columns = ['user_id', 'first_event', 'city']
    
    df_with_first = df.merge(user_first, on='user_id')
    df_with_first['days_since_first'] = (
        df_with_first['timestamp'] - df_with_first['first_event']
    ).dt.days
    
    retention_data = []
    
    for city in df['city'].unique():
        city_users = df_with_first[df_with_first['city_y'] == city]
        total_users = city_users['user_id'].nunique()
        
        d1_users = city_users[
            (city_users['days_since_first'] >= 1) & 
            (city_users['days_since_first'] <= 1)
        ]['user_id'].nunique()
        
        d7_users = city_users[
            (city_users['days_since_first'] >= 7) & 
            (city_users['days_since_first'] <= 10)
        ]['user_id'].nunique()
        
        d30_users = city_users[
            (city_users['days_since_first'] >= 30) & 
            (city_users['days_since_first'] <= 35)
        ]['user_id'].nunique()
        
        retention_data.append({
            'city': city,
            'D1': (d1_users / total_users * 100) if total_users > 0 else 0,
            'D7': (d7_users / total_users * 100) if total_users > 0 else 0,
            'D30': (d30_users / total_users * 100) if total_users > 0 else 0
        })
    
    retention_df = pd.DataFrame(retention_data)
    
    # Retention metrics
    st.markdown("### 📊 Retention Rates by City")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_d1 = retention_df['D1'].mean()
        st.metric("Avg D1 Retention", f"{avg_d1:.1f}%")
    
    with col2:
        avg_d7 = retention_df['D7'].mean()
        st.metric("Avg D7 Retention", f"{avg_d7:.1f}%")
    
    with col3:
        avg_d30 = retention_df['D30'].mean()
        st.metric("Avg D30 Retention", f"{avg_d30:.1f}%")
    
    # Retention chart
    retention_melted = retention_df.melt(
        id_vars=['city'],
        value_vars=['D1', 'D7', 'D30'],
        var_name='Period',
        value_name='Retention %'
    )
    
    fig = px.bar(
        retention_melted,
        x='city',
        y='Retention %',
        color='Period',
        barmode='group',
        labels={'city': 'City', 'Retention %': 'Retention Rate (%)'},
        title='Retention Rates by City and Period',
        color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # Engagement vs Retention scatter
    st.markdown("### 🔍 Engagement vs Retention Analysis")
    
    engagement_retention = df.groupby('city').agg({
        'event_id': 'count',
        'user_id': 'nunique'
    }).reset_index()
    engagement_retention.columns = ['city', 'total_events', 'unique_users']
    engagement_retention['events_per_user'] = (
        engagement_retention['total_events'] / engagement_retention['unique_users']
    )
    
    engagement_retention = engagement_retention.merge(retention_df, on='city')
    
    fig = px.scatter(
        engagement_retention,
        x='events_per_user',
        y='D7',
        size='unique_users',
        color='city',
        labels={
            'events_per_user': 'Events per User (Engagement)',
            'D7': 'D7 Retention (%)',
            'unique_users': 'User Count'
        },
        title='Engagement vs 7-Day Retention by City',
        hover_data=['total_events', 'unique_users']
    )
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 💡 Key Insights")
    
    best_retention = retention_df.loc[retention_df['D7'].idxmax()]
    best_engagement = engagement_retention.loc[engagement_retention['events_per_user'].idxmax()]
    
    insights_html = f"""
    <div class="insight-box">
        <h4>📈 Retention Highlights</h4>
        <ul>
            <li><b>Best D7 Retention:</b> {best_retention['city']} with {best_retention['D7']:.1f}%</li>
            <li><b>Highest Engagement:</b> {best_engagement['city']} with {best_engagement['events_per_user']:.1f} events per user</li>
            <li><b>Retention Drop:</b> Average drop from D1 to D7 is {avg_d1 - avg_d7:.1f} percentage points</li>
            <li><b>Long-term Retention:</b> {avg_d30:.1f}% of users remain active after 30 days</li>
        </ul>
    </div>
    """
    st.markdown(insights_html, unsafe_allow_html=True)

# PAGE 4: Event Distribution
def page_event_distribution(df):
    """Event types and session patterns"""
    st.markdown('<p class="main-header">📱 Event Distribution Analysis</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Understanding user behavior patterns and event types</p>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Event type pie chart
        st.markdown("### 📊 Event Type Distribution")
        
        event_dist = df['event_type'].value_counts().reset_index()
        event_dist.columns = ['event_type', 'count']
        
        fig = px.pie(
            event_dist,
            names='event_type',
            values='count',
            title='Overall Event Type Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Event types by city
        st.markdown("### 🏙️ Event Types by City")
        
        event_city = df.groupby(['city', 'event_type']).size().reset_index()
        event_city.columns = ['city', 'event_type', 'count']
        
        fig = px.bar(
            event_city,
            x='city',
            y='count',
            color='event_type',
            title='Event Distribution Across Cities',
            labels={'count': 'Event Count', 'city': 'City'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Session duration histogram
    st.markdown("### ⏱️ Session Duration Distribution")
    
    fig = px.histogram(
        df,
        x='session_duration',
        nbins=50,
        title='Distribution of Session Durations',
        labels={'session_duration': 'Session Duration (seconds)', 'count': 'Frequency'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Hourly patterns
    st.markdown("### 🕐 Events by Hour of Day")
    
    df['hour'] = df['timestamp'].dt.hour
    hourly_data = df.groupby('hour').size().reset_index()
    hourly_data.columns = ['hour', 'event_count']
    
    fig = px.line(
        hourly_data,
        x='hour',
        y='event_count',
        title='Event Activity Throughout the Day',
        labels={'hour': 'Hour of Day', 'event_count': 'Number of Events'},
        markers=True
    )
    fig.update_traces(line_color='#1f77b4', line_width=3)
    fig.update_layout(height=400)
    fig.update_xaxes(tickmode='linear', tick0=0, dtick=2)
    st.plotly_chart(fig, use_container_width=True)
    
    # Day of week patterns
    st.markdown("### 📅 Weekly Patterns")
    
    df['day_of_week'] = df['timestamp'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    weekly_data = df.groupby('day_of_week').agg({
        'event_id': 'count',
        'user_id': 'nunique'
    }).reset_index()
    weekly_data.columns = ['day_of_week', 'events', 'users']
    weekly_data['day_of_week'] = pd.Categorical(
        weekly_data['day_of_week'], 
        categories=day_order, 
        ordered=True
    )
    weekly_data = weekly_data.sort_values('day_of_week')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly_data['day_of_week'],
        y=weekly_data['events'],
        name='Events',
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        x=weekly_data['day_of_week'],
        y=weekly_data['users'],
        name='Unique Users',
        marker_color='#ff7f0e'
    ))
    fig.update_layout(
        title='Activity by Day of Week',
        xaxis_title='Day',
        yaxis_title='Count',
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Summary statistics
    st.markdown("### 📊 Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", f"{len(df):,}")
    
    with col2:
        peak_hour = hourly_data.loc[hourly_data['event_count'].idxmax(), 'hour']
        st.metric("Peak Hour", f"{int(peak_hour)}:00")
    
    with col3:
        avg_duration = df['session_duration'].mean()
        st.metric("Avg Session", f"{avg_duration:.0f}s")
    
    with col4:
        most_common_event = df['event_type'].mode()[0]
        st.metric("Top Event Type", most_common_event)

# Main app
def main():
    """Main application"""
    
    # Load data
    df = load_event_data()
    hex_gdf = load_hex_data()
    
    if df is None:
        st.error("❌ Data not found. Please run generate_location_data.py first.")
        st.stop()
    
    # Sidebar
    date_range, event_types, cities = render_sidebar(df)
    
    # Filter data
    df_filtered = get_filtered_data(df, date_range, event_types, cities)
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
        <p style='font-weight: 600; color: #475569; margin-bottom: 0.5rem; font-size: 0.9rem;'>
            📊 NAVIGATION
        </p>
    """, unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Navigate to:",
        ["📍 Overview Map", "📈 Regional Analytics", "🎯 Retention Analysis", "📱 Event Distribution"],
        label_visibility="collapsed"
    )
    
    # Render selected page
    if page == "📍 Overview Map":
        page_overview_map(df_filtered, hex_gdf)
    elif page == "📈 Regional Analytics":
        page_regional_analytics(df_filtered)
    elif page == "🎯 Retention Analysis":
        page_retention_analysis(df_filtered)
    elif page == "📱 Event Distribution":
        page_event_distribution(df_filtered)

if __name__ == "__main__":
    main()

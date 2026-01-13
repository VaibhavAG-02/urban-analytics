"""
Location-Based Event Data Generator
Generates synthetic user behavior data for 5 US cities with realistic geographic patterns
"""

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(2024)

# City configurations - 15 major US cities (lat, lon, name)
CITIES = {
    'New York': {'lat': 40.7128, 'lon': -74.0060, 'timezone': 'US/Eastern'},
    'Los Angeles': {'lat': 34.0522, 'lon': -118.2437, 'timezone': 'US/Pacific'},
    'Chicago': {'lat': 41.8781, 'lon': -87.6298, 'timezone': 'US/Central'},
    'Houston': {'lat': 29.7604, 'lon': -95.3698, 'timezone': 'US/Central'},
    'Phoenix': {'lat': 33.4484, 'lon': -112.0740, 'timezone': 'US/Mountain'},
    'Philadelphia': {'lat': 39.9526, 'lon': -75.1652, 'timezone': 'US/Eastern'},
    'San Antonio': {'lat': 29.4241, 'lon': -98.4936, 'timezone': 'US/Central'},
    'San Diego': {'lat': 32.7157, 'lon': -117.1611, 'timezone': 'US/Pacific'},
    'Dallas': {'lat': 32.7767, 'lon': -96.7970, 'timezone': 'US/Central'},
    'San Jose': {'lat': 37.3382, 'lon': -121.8863, 'timezone': 'US/Pacific'},
    'Austin': {'lat': 30.2672, 'lon': -97.7431, 'timezone': 'US/Central'},
    'Seattle': {'lat': 47.6062, 'lon': -122.3321, 'timezone': 'US/Pacific'},
    'Denver': {'lat': 39.7392, 'lon': -104.9903, 'timezone': 'US/Mountain'},
    'Boston': {'lat': 42.3601, 'lon': -71.0589, 'timezone': 'US/Eastern'},
    'Miami': {'lat': 25.7617, 'lon': -80.1918, 'timezone': 'US/Eastern'}
}

# Event types and their relative frequencies
EVENT_TYPES = {
    'search': 0.40,
    'navigation': 0.30,
    'place_view': 0.20,
    'share_location': 0.10
}

# Configuration
NUM_EVENTS = 100000
NUM_USERS = 8000
RADIUS_KM = 5.0
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

def generate_point_in_radius(center_lat, center_lon, radius_km):
    """
    Generate random point within radius of center using realistic distribution
    Uses higher density near center (urban core) with exponential falloff
    """
    # Convert radius from km to degrees (approximate)
    radius_deg = radius_km / 111.0
    
    # Use exponential distribution for distance (more points near center)
    distance = np.random.exponential(scale=0.3) * radius_deg
    distance = min(distance, radius_deg)  # Cap at max radius
    
    # Random angle
    angle = np.random.uniform(0, 2 * np.pi)
    
    # Calculate new coordinates
    lat = center_lat + (distance * np.cos(angle))
    lon = center_lon + (distance * np.sin(angle))
    
    return lat, lon

def generate_user_behavior_pattern():
    """
    Generate user behavior characteristics (engagement level, retention probability)
    """
    # User engagement level (low, medium, high)
    engagement = np.random.choice(['low', 'medium', 'high'], p=[0.5, 0.3, 0.2])
    
    # Retention probability based on engagement
    retention_probs = {
        'low': {'d1': 0.3, 'd7': 0.15, 'd30': 0.05},
        'medium': {'d1': 0.6, 'd7': 0.4, 'd30': 0.2},
        'high': {'d1': 0.85, 'd7': 0.7, 'd30': 0.5}
    }
    
    return engagement, retention_probs[engagement]

def generate_session_duration(event_type, engagement):
    """
    Generate realistic session duration based on event type and user engagement
    """
    base_durations = {
        'search': (30, 60),
        'navigation': (180, 600),
        'place_view': (45, 120),
        'share_location': (20, 40)
    }
    
    multipliers = {
        'low': 0.7,
        'medium': 1.0,
        'high': 1.5
    }
    
    min_dur, max_dur = base_durations[event_type]
    duration = np.random.uniform(min_dur, max_dur) * multipliers[engagement]
    
    return int(duration)

def generate_timestamp(start_date, end_date):
    """
    Generate timestamp with realistic hourly patterns (peak hours 8am-10pm)
    """
    # Random date
    delta = end_date - start_date
    random_days = np.random.randint(0, delta.days)
    date = start_date + timedelta(days=random_days)
    
    # Hour with peak distribution
    hour_probs = np.array([
        0.01, 0.01, 0.01, 0.01, 0.01, 0.02,  # 0-5am
        0.03, 0.05, 0.08, 0.09, 0.08, 0.07,  # 6-11am
        0.07, 0.06, 0.06, 0.07, 0.08, 0.09,  # 12-5pm
        0.08, 0.07, 0.05, 0.03, 0.02, 0.01   # 6-11pm
    ])
    hour_probs = hour_probs / hour_probs.sum()
    
    hour = np.random.choice(range(24), p=hour_probs)
    minute = np.random.randint(0, 60)
    second = np.random.randint(0, 60)
    
    timestamp = date.replace(hour=hour, minute=minute, second=second)
    return timestamp

def generate_location_events():
    """
    Generate synthetic location-based events for all cities
    """
    print("Generating location-based event data...")
    
    # Create user profiles - weighted by city population
    user_ids = [f"user_{i:05d}" for i in range(NUM_USERS)]
    # Population-weighted distribution (approximate)
    city_weights = [0.10, 0.09, 0.08, 0.07, 0.06, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.06, 0.13]
    user_city = np.random.choice(list(CITIES.keys()), size=NUM_USERS, p=city_weights)
    
    user_profiles = {}
    for uid, city in zip(user_ids, user_city):
        engagement, retention = generate_user_behavior_pattern()
        user_profiles[uid] = {
            'primary_city': city,
            'engagement': engagement,
            'retention': retention,
            'first_event': None
        }
    
    events = []
    
    # Event type choices
    event_type_list = list(EVENT_TYPES.keys())
    event_type_probs = list(EVENT_TYPES.values())
    
    for i in range(NUM_EVENTS):
        if i % 10000 == 0:
            print(f"  Generated {i}/{NUM_EVENTS} events...")
        
        # Select random user
        user_id = np.random.choice(user_ids)
        profile = user_profiles[user_id]
        
        # Generate timestamp
        timestamp = generate_timestamp(START_DATE, END_DATE)
        
        # Track first event for retention analysis
        if profile['first_event'] is None:
            profile['first_event'] = timestamp
        
        # Get user's primary city
        city_name = profile['primary_city']
        city_info = CITIES[city_name]
        
        # Generate location within city radius
        lat, lon = generate_point_in_radius(
            city_info['lat'], 
            city_info['lon'], 
            RADIUS_KM
        )
        
        # Select event type
        event_type = np.random.choice(event_type_list, p=event_type_probs)
        
        # Generate session duration
        session_duration = generate_session_duration(event_type, profile['engagement'])
        
        # Create event record
        event = {
            'event_id': f"evt_{i:06d}",
            'user_id': user_id,
            'timestamp': timestamp,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'event_type': event_type,
            'session_duration': session_duration,
            'city': city_name,
            'user_engagement': profile['engagement']
        }
        
        events.append(event)
    
    print(f"  Generated {NUM_EVENTS} events successfully!")
    
    # Create DataFrame
    df = pd.DataFrame(events)
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df, user_profiles

def save_data(df):
    """
    Save data in multiple formats
    """
    print("\nSaving data...")
    
    # Save as CSV
    csv_path = 'location_events.csv'
    df.to_csv(csv_path, index=False)
    print(f"  ✓ Saved CSV: {csv_path}")
    
    # Create GeoDataFrame for GeoJSON
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df.longitude, df.latitude)],
        crs='EPSG:4326'
    )
    
    # Save as GeoJSON
    geojson_path = 'location_events.geojson'
    gdf.to_file(geojson_path, driver='GeoJSON')
    print(f"  ✓ Saved GeoJSON: {geojson_path}")
    
    # Save summary statistics
    summary = {
        'total_events': len(df),
        'unique_users': df['user_id'].nunique(),
        'cities': df['city'].unique().tolist(),
        'date_range': {
            'start': df['timestamp'].min().isoformat(),
            'end': df['timestamp'].max().isoformat()
        },
        'event_types': df['event_type'].value_counts().to_dict(),
        'events_by_city': df['city'].value_counts().to_dict()
    }
    
    with open('data_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"  ✓ Saved summary: data_summary.json")
    
    return csv_path, geojson_path

def print_data_overview(df):
    """
    Print overview statistics
    """
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)
    
    print(f"\n📊 Total Events: {len(df):,}")
    print(f"👥 Unique Users: {df['user_id'].nunique():,}")
    print(f"📅 Date Range: {df['timestamp'].min().date()} to {df['timestamp'].max().date()}")
    
    print(f"\n🏙️  Events by City:")
    for city, count in df['city'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {city:15s}: {count:6,} ({pct:5.1f}%)")
    
    print(f"\n📱 Events by Type:")
    for event_type, count in df['event_type'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {event_type:15s}: {count:6,} ({pct:5.1f}%)")
    
    print(f"\n⏱️  Session Duration Stats:")
    print(f"  Mean: {df['session_duration'].mean():.1f} seconds")
    print(f"  Median: {df['session_duration'].median():.1f} seconds")
    print(f"  Min: {df['session_duration'].min()} seconds")
    print(f"  Max: {df['session_duration'].max()} seconds")
    
    print(f"\n🎯 User Engagement Distribution:")
    for engagement, count in df['user_engagement'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {engagement:10s}: {count:6,} ({pct:5.1f}%)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🗺️  Location-Based Event Data Generator")
    print("="*60)
    
    # Generate events
    df, user_profiles = generate_location_events()
    
    # Save data
    csv_path, geojson_path = save_data(df)
    
    # Print overview
    print_data_overview(df)
    
    print("\n✅ Data generation complete!")
    print(f"\nFiles created:")
    print(f"  - {csv_path}")
    print(f"  - {geojson_path}")
    print(f"  - data_summary.json")

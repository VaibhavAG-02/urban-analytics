"""
Geospatial Analysis with H3 Hexagonal Binning
Performs advanced spatial analytics on location events
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point, Polygon
import h3
import json
from collections import defaultdict

class GeospatialAnalyzer:
    """
    Geospatial analytics using H3 hexagonal grid system
    """
    
    def __init__(self, csv_path='location_events.csv'):
        """Initialize with event data"""
        print("🗺️  Loading geospatial data...")
        
        # Load data
        self.df = pd.read_csv(csv_path)
        
        # Create GeoDataFrame
        self.gdf = gpd.GeoDataFrame(
            self.df,
            geometry=[Point(xy) for xy in zip(self.df.longitude, self.df.latitude)],
            crs='EPSG:4326'
        )
        
        print(f"  ✓ Loaded {len(self.df):,} events")
        print(f"  ✓ Covering {self.df['city'].nunique()} cities")
    
    def create_h3_hexagons(self, resolution=8):
        """
        Create H3 hexagonal bins and aggregate events
        Resolution 8 = ~0.46 km² hex area (ideal for city-level analysis)
        """
        print(f"\n🔷 Creating H3 hexagonal bins (resolution {resolution})...")
        
        # Add H3 index to each event
        self.df['h3_index'] = self.df.apply(
            lambda row: h3.latlng_to_cell(row['latitude'], row['longitude'], resolution),
            axis=1
        )
        
        # Aggregate events by hexagon
        hex_stats = self.df.groupby('h3_index').agg({
            'event_id': 'count',
            'user_id': 'nunique',
            'session_duration': 'mean',
            'city': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0]
        }).reset_index()
        
        hex_stats.columns = ['h3_index', 'event_count', 'unique_users', 
                            'avg_session_duration', 'city']
        
        # Add hex center coordinates
        hex_stats['center_lat'] = hex_stats['h3_index'].apply(
            lambda x: h3.cell_to_latlng(x)[0]
        )
        hex_stats['center_lon'] = hex_stats['h3_index'].apply(
            lambda x: h3.cell_to_latlng(x)[1]
        )
        
        # Add hex boundaries as polygons
        hex_stats['geometry'] = hex_stats['h3_index'].apply(
            lambda x: Polygon(h3.cell_to_boundary(x))
        )
        
        # Create GeoDataFrame
        hex_gdf = gpd.GeoDataFrame(hex_stats, geometry='geometry', crs='EPSG:4326')
        
        # Calculate hex area in km²
        hex_gdf = hex_gdf.to_crs('EPSG:3857')  # Project to meters
        hex_gdf['area_km2'] = hex_gdf.geometry.area / 1e6
        hex_gdf = hex_gdf.to_crs('EPSG:4326')  # Back to lat/lon
        
        # Calculate event density (events per km²)
        hex_gdf['event_density'] = hex_gdf['event_count'] / hex_gdf['area_km2']
        
        print(f"  ✓ Created {len(hex_gdf):,} hexagonal bins")
        print(f"  ✓ Average hex area: {hex_gdf['area_km2'].mean():.2f} km²")
        
        self.hex_gdf = hex_gdf
        return hex_gdf
    
    def identify_hotspots(self, percentile=90):
        """
        Identify high-activity hotspots
        """
        print(f"\n🔥 Identifying hotspots (top {100-percentile}%)...")
        
        if not hasattr(self, 'hex_gdf'):
            self.create_h3_hexagons()
        
        # Calculate threshold
        threshold = self.hex_gdf['event_density'].quantile(percentile / 100)
        
        # Identify hotspots
        hotspots = self.hex_gdf[self.hex_gdf['event_density'] >= threshold].copy()
        hotspots = hotspots.sort_values('event_density', ascending=False)
        
        print(f"  ✓ Found {len(hotspots)} hotspots")
        print(f"  ✓ Density threshold: {threshold:.1f} events/km²")
        print(f"\n  Top 5 Hotspots:")
        for idx, row in hotspots.head().iterrows():
            print(f"    {row['city']:15s}: {row['event_density']:6.1f} events/km² "
                  f"({row['event_count']:,} events)")
        
        return hotspots
    
    def calculate_engagement_density_by_city(self):
        """
        Calculate engagement density metrics for each city
        """
        print("\n📊 Calculating engagement density by city...")
        
        if not hasattr(self, 'hex_gdf'):
            self.create_h3_hexagons()
        
        city_metrics = self.hex_gdf.groupby('city').agg({
            'event_count': 'sum',
            'unique_users': 'sum',
            'event_density': ['mean', 'max', 'std'],
            'h3_index': 'count'
        }).reset_index()
        
        city_metrics.columns = ['city', 'total_events', 'total_users', 
                               'avg_density', 'max_density', 'std_density', 'hex_count']
        
        # Calculate events per hexagon
        city_metrics['events_per_hex'] = (
            city_metrics['total_events'] / city_metrics['hex_count']
        )
        
        city_metrics = city_metrics.sort_values('avg_density', ascending=False)
        
        print("\n  Engagement Density by City:")
        print("  " + "-" * 70)
        for idx, row in city_metrics.iterrows():
            print(f"  {row['city']:15s}: Avg Density: {row['avg_density']:6.1f} events/km²  "
                  f"Max: {row['max_density']:6.1f}")
        
        return city_metrics
    
    def analyze_urban_vs_suburban(self, center_radius_km=2.5):
        """
        Compare urban core vs suburban engagement patterns
        """
        print(f"\n🏙️  Analyzing urban vs suburban patterns...")
        print(f"  Urban core defined as {center_radius_km}km from city center")
        
        # City centers
        city_centers = {
            'San Francisco': (37.7749, -122.4194),
            'New York': (40.7128, -74.0060),
            'Los Angeles': (34.0522, -118.2437),
            'Chicago': (41.8781, -87.6298),
            'Seattle': (47.6062, -122.3321)
        }
        
        # Calculate distance from city center for each event
        def calculate_distance(lat, lon, city):
            if city not in city_centers:
                return None
            
            center_lat, center_lon = city_centers[city]
            
            # Haversine formula
            R = 6371  # Earth radius in km
            
            lat1, lon1 = np.radians(center_lat), np.radians(center_lon)
            lat2, lon2 = np.radians(lat), np.radians(lon)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            
            return R * c
        
        self.df['distance_from_center'] = self.df.apply(
            lambda row: calculate_distance(row['latitude'], row['longitude'], row['city']),
            axis=1
        )
        
        # Classify as urban or suburban
        self.df['area_type'] = self.df['distance_from_center'].apply(
            lambda x: 'urban' if x <= center_radius_km else 'suburban' if x is not None else None
        )
        
        # Calculate metrics for each area type
        comparison = self.df.groupby(['city', 'area_type']).agg({
            'event_id': 'count',
            'user_id': 'nunique',
            'session_duration': 'mean'
        }).reset_index()
        
        comparison.columns = ['city', 'area_type', 'event_count', 
                             'unique_users', 'avg_session_duration']
        
        print("\n  Urban vs Suburban Comparison:")
        print("  " + "-" * 70)
        for city in comparison['city'].unique():
            city_data = comparison[comparison['city'] == city]
            print(f"\n  {city}:")
            for _, row in city_data.iterrows():
                if row['area_type']:
                    print(f"    {row['area_type'].capitalize():10s}: "
                          f"{row['event_count']:6,} events, "
                          f"{row['unique_users']:5,} users, "
                          f"{row['avg_session_duration']:5.1f}s avg session")
        
        return comparison
    
    def calculate_retention_by_region(self):
        """
        Calculate retention rates by geographic region (using hexagons)
        """
        print("\n🎯 Calculating retention by geographic region...")
        
        if not hasattr(self, 'hex_gdf'):
            self.create_h3_hexagons()
        
        # Get user first event and subsequent returns
        user_hex_first = self.df.sort_values('timestamp').groupby('user_id').agg({
            'timestamp': 'first',
            'h3_index': 'first',
            'city': 'first'
        }).reset_index()
        
        user_hex_first.columns = ['user_id', 'first_event_date', 'first_hex', 'city']
        
        # Merge back to get all events with first event info
        df_with_first = self.df.merge(user_hex_first, on='user_id', suffixes=('', '_first'))
        
        # Calculate days since first event
        df_with_first['timestamp'] = pd.to_datetime(df_with_first['timestamp'])
        df_with_first['first_event_date'] = pd.to_datetime(df_with_first['first_event_date'])
        df_with_first['days_since_first'] = (
            df_with_first['timestamp'] - df_with_first['first_event_date']
        ).dt.days
        
        # Calculate retention by hex
        hex_retention = []
        
        for h3_idx in df_with_first['first_hex'].unique():
            hex_users = df_with_first[df_with_first['first_hex'] == h3_idx]
            total_users = hex_users['user_id'].nunique()
            
            # D1 retention
            d1_users = hex_users[
                (hex_users['days_since_first'] >= 1) & 
                (hex_users['days_since_first'] <= 1)
            ]['user_id'].nunique()
            
            # D7 retention
            d7_users = hex_users[
                (hex_users['days_since_first'] >= 7) & 
                (hex_users['days_since_first'] <= 10)
            ]['user_id'].nunique()
            
            # D30 retention
            d30_users = hex_users[
                (hex_users['days_since_first'] >= 30) & 
                (hex_users['days_since_first'] <= 35)
            ]['user_id'].nunique()
            
            city = hex_users['city_first'].iloc[0]
            
            hex_retention.append({
                'h3_index': h3_idx,
                'city': city,
                'total_users': total_users,
                'd1_retention_pct': (d1_users / total_users * 100) if total_users > 0 else 0,
                'd7_retention_pct': (d7_users / total_users * 100) if total_users > 0 else 0,
                'd30_retention_pct': (d30_users / total_users * 100) if total_users > 0 else 0
            })
        
        retention_df = pd.DataFrame(hex_retention)
        
        # Summary by city
        city_retention = retention_df.groupby('city').agg({
            'd1_retention_pct': 'mean',
            'd7_retention_pct': 'mean',
            'd30_retention_pct': 'mean'
        }).round(2).reset_index()
        
        print("\n  Average Retention by City:")
        print("  " + "-" * 70)
        for _, row in city_retention.iterrows():
            print(f"  {row['city']:15s}: D1: {row['d1_retention_pct']:5.1f}%  "
                  f"D7: {row['d7_retention_pct']:5.1f}%  "
                  f"D30: {row['d30_retention_pct']:5.1f}%")
        
        return retention_df, city_retention
    
    def export_for_visualization(self):
        """
        Export processed data for Streamlit visualization
        """
        print("\n💾 Exporting data for visualization...")
        
        if not hasattr(self, 'hex_gdf'):
            self.create_h3_hexagons()
        
        # Export hexagon data
        hex_export = self.hex_gdf.copy()
        hex_export.to_file('hex_analysis.geojson', driver='GeoJSON')
        print("  ✓ Saved: hex_analysis.geojson")
        
        # Export hotspots
        hotspots = self.identify_hotspots()
        hotspots.to_file('hotspots.geojson', driver='GeoJSON')
        print("  ✓ Saved: hotspots.geojson")
        
        # Export summary statistics
        summary = {
            'total_hexagons': len(self.hex_gdf),
            'total_hotspots': len(hotspots),
            'avg_event_density': float(self.hex_gdf['event_density'].mean()),
            'max_event_density': float(self.hex_gdf['event_density'].max()),
            'cities_analyzed': self.hex_gdf['city'].unique().tolist()
        }
        
        with open('spatial_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        print("  ✓ Saved: spatial_summary.json")
        
        return summary

def run_spatial_analysis():
    """
    Run complete geospatial analysis pipeline
    """
    print("="*70)
    print("GEOSPATIAL ANALYSIS WITH H3 HEXAGONAL BINNING")
    print("="*70)
    
    analyzer = GeospatialAnalyzer()
    
    # Create hexagonal bins
    hex_gdf = analyzer.create_h3_hexagons(resolution=8)
    
    # Identify hotspots
    hotspots = analyzer.identify_hotspots(percentile=90)
    
    # Calculate engagement density
    city_metrics = analyzer.calculate_engagement_density_by_city()
    
    # Urban vs suburban analysis
    urban_suburban = analyzer.analyze_urban_vs_suburban(center_radius_km=2.5)
    
    # Retention by region
    hex_retention, city_retention = analyzer.calculate_retention_by_region()
    
    # Export for visualization
    summary = analyzer.export_for_visualization()
    
    print("\n" + "="*70)
    print("✅ Geospatial analysis complete!")
    print("="*70)
    print("\nFiles created:")
    print("  - hex_analysis.geojson")
    print("  - hotspots.geojson")
    print("  - spatial_summary.json")

if __name__ == "__main__":
    run_spatial_analysis()

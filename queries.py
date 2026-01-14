"""
DuckDB Analytical Queries
Performs fast analytical queries on location-based event data
"""

import duckdb
import pandas as pd
from pathlib import Path

class LocationAnalytics:
    """
    DuckDB-based analytics for location events
    """
    
    def __init__(self, csv_path='location_events.csv', db_path='location_analytics.duckdb'):
        """Initialize DuckDB connection and load data"""
        self.db_path = db_path
        self.con = duckdb.connect(db_path)
        
        print("🦆 Initializing DuckDB...")
        
        # Load data from CSV
        if Path(csv_path).exists():
            print(f"  Loading data from {csv_path}...")
            self.con.execute(f"""
                CREATE OR REPLACE TABLE events AS 
                SELECT * FROM read_csv_auto('{csv_path}')
            """)
            
            # Create indices for performance
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_city ON events(city)")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_user ON events(user_id)")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            self.con.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
            
            print("  ✓ Data loaded and indexed")
        else:
            raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    def get_events_by_city(self):
        """Total events by city"""
        query = """
            SELECT 
                city,
                COUNT(*) as total_events,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM events
            GROUP BY city
            ORDER BY total_events DESC
        """
        return self.con.execute(query).df()
    
    def get_unique_users_by_city(self):
        """Unique users by city"""
        query = """
            SELECT 
                city,
                COUNT(DISTINCT user_id) as unique_users,
                ROUND(COUNT(DISTINCT user_id) * 100.0 / 
                      (SELECT COUNT(DISTINCT user_id) FROM events), 2) as percentage
            FROM events
            GROUP BY city
            ORDER BY unique_users DESC
        """
        return self.con.execute(query).df()
    
    def get_avg_session_duration_by_city(self):
        """Average session duration by city"""
        query = """
            SELECT 
                city,
                ROUND(AVG(session_duration), 2) as avg_duration_seconds,
                ROUND(AVG(session_duration) / 60.0, 2) as avg_duration_minutes,
                ROUND(STDDEV(session_duration), 2) as stddev_seconds
            FROM events
            GROUP BY city
            ORDER BY avg_duration_seconds DESC
        """
        return self.con.execute(query).df()
    
    def get_events_per_user_by_city(self):
        """Events per user by city"""
        query = """
            SELECT 
                city,
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) as unique_users,
                ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT user_id), 2) as events_per_user
            FROM events
            GROUP BY city
            ORDER BY events_per_user DESC
        """
        return self.con.execute(query).df()
    
    def get_retention_by_city(self):
        """Calculate D1, D7, D30 retention by city"""
        query = """
            WITH user_first_event AS (
                SELECT 
                    user_id,
                    city,
                    MIN(timestamp) as first_event_date
                FROM events
                GROUP BY user_id, city
            ),
            user_return_events AS (
                SELECT 
                    e.user_id,
                    e.city,
                    ufe.first_event_date,
                    e.timestamp as event_date,
                    DATE_DIFF('day', ufe.first_event_date::DATE, e.timestamp::DATE) as days_since_first
                FROM events e
                JOIN user_first_event ufe ON e.user_id = ufe.user_id AND e.city = ufe.city
                WHERE DATE_DIFF('day', ufe.first_event_date::DATE, e.timestamp::DATE) > 0
            ),
            retention_calc AS (
                SELECT 
                    city,
                    COUNT(DISTINCT CASE WHEN days_since_first >= 1 AND days_since_first <= 1 THEN user_id END) as d1_retained,
                    COUNT(DISTINCT CASE WHEN days_since_first >= 7 AND days_since_first <= 10 THEN user_id END) as d7_retained,
                    COUNT(DISTINCT CASE WHEN days_since_first >= 30 AND days_since_first <= 35 THEN user_id END) as d30_retained
                FROM user_return_events
                GROUP BY city
            ),
            total_users AS (
                SELECT 
                    city,
                    COUNT(DISTINCT user_id) as total_users
                FROM user_first_event
                GROUP BY city
            )
            SELECT 
                rc.city,
                tu.total_users,
                rc.d1_retained,
                ROUND(rc.d1_retained * 100.0 / tu.total_users, 2) as d1_retention_pct,
                rc.d7_retained,
                ROUND(rc.d7_retained * 100.0 / tu.total_users, 2) as d7_retention_pct,
                rc.d30_retained,
                ROUND(rc.d30_retained * 100.0 / tu.total_users, 2) as d30_retention_pct
            FROM retention_calc rc
            JOIN total_users tu ON rc.city = tu.city
            ORDER BY d1_retention_pct DESC
        """
        return self.con.execute(query).df()
    
    def get_peak_hours_by_city(self):
        """Peak usage hours by city"""
        query = """
            SELECT 
                city,
                EXTRACT(HOUR FROM timestamp) as hour,
                COUNT(*) as event_count
            FROM events
            GROUP BY city, hour
            ORDER BY city, hour
        """
        df = self.con.execute(query).df()
        
        # Find peak hour for each city
        peak_hours = df.loc[df.groupby('city')['event_count'].idxmax()]
        return peak_hours[['city', 'hour', 'event_count']]
    
    def get_hourly_distribution(self):
        """Get hourly event distribution across all cities"""
        query = """
            SELECT 
                EXTRACT(HOUR FROM timestamp) as hour,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM events
            GROUP BY hour
            ORDER BY hour
        """
        return self.con.execute(query).df()
    
    def get_event_type_distribution(self):
        """Event type distribution overall and by city"""
        query = """
            SELECT 
                event_type,
                COUNT(*) as total_events,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM events
            GROUP BY event_type
            ORDER BY total_events DESC
        """
        overall = self.con.execute(query).df()
        
        query_by_city = """
            SELECT 
                city,
                event_type,
                COUNT(*) as event_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY city), 2) as pct_in_city
            FROM events
            GROUP BY city, event_type
            ORDER BY city, event_count DESC
        """
        by_city = self.con.execute(query_by_city).df()
        
        return overall, by_city
    
    def get_top_locations(self, limit=10):
        """Top most active locations (lat/lon clusters)"""
        query = f"""
            SELECT 
                ROUND(latitude, 3) as lat,
                ROUND(longitude, 3) as lon,
                city,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM events
            GROUP BY lat, lon, city
            ORDER BY event_count DESC
            LIMIT {limit}
        """
        return self.con.execute(query).df()
    
    def get_engagement_trends(self):
        """Daily engagement trends"""
        query = """
            SELECT 
                DATE_TRUNC('day', timestamp) as date,
                city,
                COUNT(*) as daily_events,
                COUNT(DISTINCT user_id) as daily_active_users
            FROM events
            GROUP BY date, city
            ORDER BY date, city
        """
        return self.con.execute(query).df()
    
    def get_user_segments_by_city(self):
        """User segmentation by engagement level"""
        query = """
            SELECT 
                city,
                user_engagement,
                COUNT(DISTINCT user_id) as user_count,
                COUNT(*) as total_events,
                ROUND(AVG(session_duration), 2) as avg_session_duration
            FROM events
            GROUP BY city, user_engagement
            ORDER BY city, user_count DESC
        """
        return self.con.execute(query).df()
    
    def get_session_duration_distribution(self):
        """Session duration distribution with buckets"""
        query = """
            SELECT 
                CASE 
                    WHEN session_duration < 60 THEN '0-1 min'
                    WHEN session_duration < 180 THEN '1-3 min'
                    WHEN session_duration < 300 THEN '3-5 min'
                    WHEN session_duration < 600 THEN '5-10 min'
                    ELSE '10+ min'
                END as duration_bucket,
                COUNT(*) as event_count,
                ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM events
            GROUP BY duration_bucket
            ORDER BY 
                CASE duration_bucket
                    WHEN '0-1 min' THEN 1
                    WHEN '1-3 min' THEN 2
                    WHEN '3-5 min' THEN 3
                    WHEN '5-10 min' THEN 4
                    ELSE 5
                END
        """
        return self.con.execute(query).df()
    
    def get_day_of_week_patterns(self):
        """Usage patterns by day of week"""
        query = """
            SELECT 
                DAYNAME(timestamp) as day_of_week,
                DAYOFWEEK(timestamp) as day_num,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as unique_users,
                ROUND(AVG(session_duration), 2) as avg_session_duration
            FROM events
            GROUP BY day_of_week, day_num
            ORDER BY day_num
        """
        return self.con.execute(query).df()
    
    def close(self):
        """Close database connection"""
        self.con.close()
        print("  ✓ Database connection closed")

def run_all_queries():
    """Run all analytical queries and display results"""
    print("="*70)
    print("LOCATION-BASED USER BEHAVIOR ANALYTICS")
    print("="*70)
    
    analytics = LocationAnalytics()
    
    # 1. Events by city
    print("\n📊 TOTAL EVENTS BY CITY")
    print("-" * 70)
    df = analytics.get_events_by_city()
    print(df.to_string(index=False))
    
    # 2. Unique users by city
    print("\n👥 UNIQUE USERS BY CITY")
    print("-" * 70)
    df = analytics.get_unique_users_by_city()
    print(df.to_string(index=False))
    
    # 3. Average session duration by city
    print("\n⏱️  AVERAGE SESSION DURATION BY CITY")
    print("-" * 70)
    df = analytics.get_avg_session_duration_by_city()
    print(df.to_string(index=False))
    
    # 4. Events per user by city
    print("\n📈 EVENTS PER USER BY CITY")
    print("-" * 70)
    df = analytics.get_events_per_user_by_city()
    print(df.to_string(index=False))
    
    # 5. Retention by city
    print("\n🎯 RETENTION ANALYSIS BY CITY")
    print("-" * 70)
    df = analytics.get_retention_by_city()
    print(df.to_string(index=False))
    
    # 6. Peak hours by city
    print("\n🕐 PEAK USAGE HOURS BY CITY")
    print("-" * 70)
    df = analytics.get_peak_hours_by_city()
    print(df.to_string(index=False))
    
    # 7. Event type distribution
    print("\n📱 EVENT TYPE DISTRIBUTION")
    print("-" * 70)
    overall, by_city = analytics.get_event_type_distribution()
    print("Overall:")
    print(overall.to_string(index=False))
    
    # 8. Top locations
    print("\n📍 TOP 10 MOST ACTIVE LOCATIONS")
    print("-" * 70)
    df = analytics.get_top_locations()
    print(df.to_string(index=False))
    
    # 9. Session duration distribution
    print("\n⏲️  SESSION DURATION DISTRIBUTION")
    print("-" * 70)
    df = analytics.get_session_duration_distribution()
    print(df.to_string(index=False))
    
    analytics.close()
    print("\n✅ All queries completed successfully!")

if __name__ == "__main__":
    run_all_queries()

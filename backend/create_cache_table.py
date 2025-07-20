import sqlite3
import os

def create_analysis_cache_table():
    """Create the analysis_cache table directly in SQLite"""
    
    # Get the database path
    db_path = os.path.join('instance', 'x_sentiment.db')
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the analysis_cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) NOT NULL,
            analysis_type VARCHAR(50) NOT NULL,
            user_profile TEXT,
            tweets_data TEXT,
            analysis_results TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_dynamic BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Create index on username
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS ix_analysis_cache_username 
        ON analysis_cache (username)
    ''')
    
    # Commit the changes
    conn.commit()
    conn.close()
    
    print("✅ Analysis cache table created successfully!")

if __name__ == "__main__":
    create_analysis_cache_table() 
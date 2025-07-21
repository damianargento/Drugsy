import sqlite3

def add_reset_columns():
    # Connect to the database
    conn = sqlite3.connect('drugsy.db')
    cursor = conn.cursor()
    
    try:
        # Check if the columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add reset_token column if it doesn't exist
        if "reset_token" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
            print("Added reset_token column to users table")
        
        # Add reset_token_expires column if it doesn't exist
        if "reset_token_expires" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP")
            print("Added reset_token_expires column to users table")
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_reset_columns()

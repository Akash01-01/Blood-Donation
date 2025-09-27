from app import app, db
from sqlalchemy import text

def add_scheduled_date_column():
    """Add scheduled_date column to donation_response table"""
    try:
        with app.app_context():
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(donation_response)"))
            columns = [row[1] for row in result]
            
            if 'scheduled_date' not in columns:
                # Add the column
                db.session.execute(text("ALTER TABLE donation_response ADD COLUMN scheduled_date DATE"))
                db.session.commit()
                print("✅ Added scheduled_date column to donation_response table")
            else:
                print("ℹ️ scheduled_date column already exists")
                
    except Exception as e:
        print(f"❌ Error adding column: {e}")
        db.session.rollback()

if __name__ == "__main__":
    add_scheduled_date_column()
# Create a new file: migrations/add_user_columns.py
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.database import engine
from sqlalchemy import text

def add_user_columns():
    """
    Add missing columns to users table
    """
    with engine.connect() as conn:
        # Add is_active column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;
            """))
            print("✓ Added is_active column")
        except Exception as e:
            print(f"Error adding is_active: {e}")
        
        # Add is_verified column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_verified BOOLEAN DEFAULT FALSE NOT NULL;
            """))
            print("✓ Added is_verified column")
        except Exception as e:
            print(f"Error adding is_verified: {e}")
        
        # Add verification_code column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS verification_code VARCHAR(6);
            """))
            print("✓ Added verification_code column")
        except Exception as e:
            print(f"Error adding verification_code: {e}")
        
        # Add verification_code_expires column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS verification_code_expires TIMESTAMP WITH TIME ZONE;
            """))
            print("✓ Added verification_code_expires column")
        except Exception as e:
            print(f"Error adding verification_code_expires: {e}")
        
        # Add password_reset_token column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255);
            """))
            print("✓ Added password_reset_token column")
        except Exception as e:
            print(f"Error adding password_reset_token: {e}")
        
        # Add password_reset_expires column
        try:
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP WITH TIME ZONE;
            """))
            print("✓ Added password_reset_expires column")
        except Exception as e:
            print(f"Error adding password_reset_expires: {e}")
        
        # Create index on password_reset_token if it doesn't exist
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_password_reset_token 
                ON users(password_reset_token);
            """))
            print("✓ Created index on password_reset_token")
        except Exception as e:
            print(f"Error creating index: {e}")
        
        # Update existing users to have is_active = True and is_verified = False
        try:
            conn.execute(text("""
                UPDATE users 
                SET is_active = TRUE 
                WHERE is_active IS NULL;
            """))
            conn.execute(text("""
                UPDATE users 
                SET is_verified = FALSE 
                WHERE is_verified IS NULL;
            """))
            print("✓ Updated existing users")
        except Exception as e:
            print(f"Error updating existing users: {e}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    add_user_columns()
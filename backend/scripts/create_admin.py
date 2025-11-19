"""Script to create an initial admin user."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_database
from db_models import Admin
from auth import get_password_hash


async def create_admin(username: str, password: str):
    """Create an admin user."""
    # Initialize database
    await init_database([Admin])
    
    # Check if admin already exists
    existing = await Admin.find_one({"username": username})
    if existing:
        print(f"Admin user '{username}' already exists.")
        return False
    
    # Create new admin
    password_hash = get_password_hash(password)
    admin = Admin(
        username=username,
        password_hash=password_hash
    )
    await admin.insert()
    
    print(f"Admin user '{username}' created successfully.")
    return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    if len(password) < 8:
        print("Error: Password must be at least 8 characters long.")
        sys.exit(1)
    
    result = asyncio.run(create_admin(username, password))
    sys.exit(0 if result else 1)


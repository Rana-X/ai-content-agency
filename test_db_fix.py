"""Test database connection after fixing Supabase package versions"""

import asyncio
from config import config
from state.storage import StateManager

async def test_connection():
    try:
        # Test Supabase client creation
        client = config.get_supabase_client()
        print("✅ Supabase client created successfully")
        
        # Test StateManager initialization
        state_manager = StateManager(client)
        print("✅ StateManager initialized")
        
        # Test database operation
        projects = await state_manager.list_projects()
        print(f"✅ Database connected! Found {len(projects)} projects")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_connection())
    exit(0 if result else 1)
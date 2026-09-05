#!/usr/bin/env python
"""Initialize database on first startup"""
import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.database import init_database

if __name__ == "__main__":
    try:
        init_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        sys.exit(1)

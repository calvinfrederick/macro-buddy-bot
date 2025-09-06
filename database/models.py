import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class User:
    id: Optional[int] = None
    chat_id: int = 0
    calories_goal: int = 2000
    protein_goal: float = 150.0
    carbs_goal: float = 160.0
    fat_goal: float = 60.0

@dataclass
class Food:
    id: Optional[int] = None
    name: str = ""
    calories_per_100g: float = 0.0
    protein_per_100g: float = 0.0
    carbs_per_100g: float = 0.0
    fat_per_100g: float = 0.0

@dataclass
class Log:
    id: Optional[int] = None
    user_id: int = 0
    food_id: int = 0
    amount_grams: float = 0.0
    date: str = ""

@dataclass
class Inventory:
    user_id: int = 0
    food_id: int = 0
    quantity_grams: float = 0.0

class Database:
    def __init__(self, db_path: str = "macro_buddy.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                calories_goal INTEGER DEFAULT 2000,
                protein_goal REAL DEFAULT 150.0,
                carbs_goal REAL DEFAULT 160.0,
                fat_goal REAL DEFAULT 60.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create foods table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                calories_per_100g REAL NOT NULL,
                protein_per_100g REAL NOT NULL,
                carbs_per_100g REAL NOT NULL,
                fat_per_100g REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                amount_grams REAL NOT NULL,
                date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (food_id) REFERENCES foods (id)
            )
        ''')
        
        # Create inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER NOT NULL,
                food_id INTEGER NOT NULL,
                quantity_grams REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, food_id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (food_id) REFERENCES foods (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
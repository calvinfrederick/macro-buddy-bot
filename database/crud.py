from typing import List, Optional, Dict, Any
from datetime import datetime, date
import sqlite3
from .models import Database, User, Food, Log, Inventory

class UserCRUD:
    def __init__(self, db: Database):
        self.db = db
    
    def create_or_update_user(self, chat_id: int, calories_goal: int = 2000, 
                            protein_goal: float = 150.0, carbs_goal: float = 160.0, 
                            fat_goal: float = 60.0) -> User:
        """Create or update user with macro goals"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE chat_id = ?", (chat_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET calories_goal = ?, protein_goal = ?, carbs_goal = ?, fat_goal = ?
                WHERE chat_id = ?
            """, (calories_goal, protein_goal, carbs_goal, fat_goal, chat_id))
            user_id = existing[0]
        else:
            # Create new user
            cursor.execute("""
                INSERT INTO users (chat_id, calories_goal, protein_goal, carbs_goal, fat_goal)
                VALUES (?, ?, ?, ?, ?)
            """, (chat_id, calories_goal, protein_goal, carbs_goal, fat_goal))
            user_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return User(id=user_id, chat_id=chat_id, calories_goal=calories_goal,
                   protein_goal=protein_goal, carbs_goal=carbs_goal, fat_goal=fat_goal)
    
    def get_user_by_chat_id(self, chat_id: int) -> Optional[User]:
        """Get user by chat_id"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, chat_id, calories_goal, protein_goal, carbs_goal, fat_goal
            FROM users WHERE chat_id = ?
        """, (chat_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return User(id=row[0], chat_id=row[1], calories_goal=row[2],
                       protein_goal=row[3], carbs_goal=row[4], fat_goal=row[5])
        return None

class FoodCRUD:
    def __init__(self, db: Database):
        self.db = db
    
    def create_food(self, name: str, calories_per_100g: float, protein_per_100g: float,
                   carbs_per_100g: float, fat_per_100g: float) -> Food:
        """Create a new food item"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO foods (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g)
            VALUES (?, ?, ?, ?, ?)
        """, (name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g))
        
        food_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Food(id=food_id, name=name, calories_per_100g=calories_per_100g,
                   protein_per_100g=protein_per_100g, carbs_per_100g=carbs_per_100g,
                   fat_per_100g=fat_per_100g)
    
    def get_food_by_name(self, name: str) -> Optional[Food]:
        """Get food by name (case insensitive)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g
            FROM foods WHERE LOWER(name) = LOWER(?)
        """, (name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Food(id=row[0], name=row[1], calories_per_100g=row[2],
                       protein_per_100g=row[3], carbs_per_100g=row[4], fat_per_100g=row[5])
        return None
    
    def search_foods(self, query: str) -> List[Food]:
        """Search foods by name (partial match)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g
            FROM foods WHERE LOWER(name) LIKE LOWER(?)
            LIMIT 10
        """, (f"%{query}%",))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Food(id=row[0], name=row[1], calories_per_100g=row[2],
                    protein_per_100g=row[3], carbs_per_100g=row[4], fat_per_100g=row[5])
                for row in rows]
    
    def get_all_foods(self) -> List[Food]:
        """Get all foods"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g
            FROM foods ORDER BY name
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Food(id=row[0], name=row[1], calories_per_100g=row[2],
                    protein_per_100g=row[3], carbs_per_100g=row[4], fat_per_100g=row[5])
                for row in rows]

class LogCRUD:
    def __init__(self, db: Database):
        self.db = db
    
    def log_food(self, user_id: int, food_id: int, amount_grams: float, log_date: str = None) -> Log:
        """Log food consumption"""
        if log_date is None:
            log_date = date.today().isoformat()
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO logs (user_id, food_id, amount_grams, date)
            VALUES (?, ?, ?, ?)
        """, (user_id, food_id, amount_grams, log_date))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return Log(id=log_id, user_id=user_id, food_id=food_id, 
                  amount_grams=amount_grams, date=log_date)
    
    def get_user_logs_today(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's food logs for today with food details"""
        today = date.today().isoformat()
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT l.id, l.amount_grams, l.date,
                   f.name, f.calories_per_100g, f.protein_per_100g, 
                   f.carbs_per_100g, f.fat_per_100g
            FROM logs l
            JOIN foods f ON l.food_id = f.id
            WHERE l.user_id = ? AND l.date = ?
            ORDER BY l.created_at DESC
        """, (user_id, today))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'log_id': row[0],
            'amount_grams': row[1],
            'date': row[2],
            'food_name': row[3],
            'calories_per_100g': row[4],
            'protein_per_100g': row[5],
            'carbs_per_100g': row[6],
            'fat_per_100g': row[7]
        } for row in rows]

class InventoryCRUD:
    def __init__(self, db: Database):
        self.db = db
    
    def add_to_inventory(self, user_id: int, food_id: int, quantity_grams: float) -> Inventory:
        """Add or update food in user's inventory"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if food already in inventory
        cursor.execute("""
            SELECT quantity_grams FROM inventory 
            WHERE user_id = ? AND food_id = ?
        """, (user_id, food_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing quantity
            new_quantity = existing[0] + quantity_grams
            cursor.execute("""
                UPDATE inventory SET quantity_grams = ?
                WHERE user_id = ? AND food_id = ?
            """, (new_quantity, user_id, food_id))
        else:
            # Add new food to inventory
            cursor.execute("""
                INSERT INTO inventory (user_id, food_id, quantity_grams)
                VALUES (?, ?, ?)
            """, (user_id, food_id, quantity_grams))
        
        conn.commit()
        conn.close()
        
        return Inventory(user_id=user_id, food_id=food_id, quantity_grams=quantity_grams)
    
    def get_user_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's inventory with food details"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT i.quantity_grams, f.id, f.name, f.calories_per_100g, 
                   f.protein_per_100g, f.carbs_per_100g, f.fat_per_100g
            FROM inventory i
            JOIN foods f ON i.food_id = f.id
            WHERE i.user_id = ? AND i.quantity_grams > 0
            ORDER BY f.name
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'quantity_grams': row[0],
            'food_id': row[1],
            'food_name': row[2],
            'calories_per_100g': row[3],
            'protein_per_100g': row[4],
            'carbs_per_100g': row[5],
            'fat_per_100g': row[6]
        } for row in rows]
    
    def remove_from_inventory(self, user_id: int, food_id: int, quantity_grams: float) -> bool:
        """Remove food from inventory (for suggestions)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quantity_grams FROM inventory 
            WHERE user_id = ? AND food_id = ?
        """, (user_id, food_id))
        
        existing = cursor.fetchone()
        
        if not existing or existing[0] < quantity_grams:
            conn.close()
            return False
        
        new_quantity = existing[0] - quantity_grams
        
        if new_quantity <= 0:
            cursor.execute("""
                DELETE FROM inventory WHERE user_id = ? AND food_id = ?
            """, (user_id, food_id))
        else:
            cursor.execute("""
                UPDATE inventory SET quantity_grams = ?
                WHERE user_id = ? AND food_id = ?
            """, (new_quantity, user_id, food_id))
        
        conn.commit()
        conn.close()
        return True
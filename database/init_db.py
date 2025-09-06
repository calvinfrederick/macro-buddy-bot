import json
import os
from .models import Database
from .crud import FoodCRUD

def init_database_with_seed_data():
    """Initialize database and populate with seed food data"""
    # Initialize database
    db = Database()
    
    # Check if foods already exist
    food_crud = FoodCRUD(db)
    existing_foods = food_crud.get_all_foods()
    
    if existing_foods:
        print(f"Database already initialized with {len(existing_foods)} foods")
        return db
    
    # Load seed data
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    foods_file = os.path.join(data_dir, 'foods.json')
    
    try:
        with open(foods_file, 'r') as f:
            foods_data = json.load(f)
        
        # Insert seed foods
        for food_data in foods_data:
            food_crud.create_food(
                name=food_data['name'],
                calories_per_100g=food_data['calories_per_100g'],
                protein_per_100g=food_data['protein_per_100g'],
                carbs_per_100g=food_data['carbs_per_100g'],
                fat_per_100g=food_data['fat_per_100g']
            )
        
        print(f"Successfully initialized database with {len(foods_data)} foods")
        
    except FileNotFoundError:
        print(f"Warning: Could not find {foods_file}")
        print("Database initialized but no seed data loaded")
    except Exception as e:
        print(f"Error loading seed data: {e}")
    
    return db

if __name__ == "__main__":
    init_database_with_seed_data()
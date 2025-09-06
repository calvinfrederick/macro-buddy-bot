#!/usr/bin/env python3
"""
Test script for Macro Buddy Bot
Tests core functionality without requiring Telegram bot token
"""

import os
import sys
from datetime import date

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.init_db import init_database_with_seed_data
from database.crud import UserCRUD, FoodCRUD, LogCRUD, InventoryCRUD
from engine.macro_calculator import MacroCalculator, MacroTargets, MacroConsumed

def test_database_operations():
    """Test database operations"""
    print("🧪 Testing database operations...")
    
    # Initialize database
    db = init_database_with_seed_data()
    print("✅ Database initialized")
    
    # Test user operations
    user_crud = UserCRUD(db)
    user = user_crud.create_or_update_user(12345, 2000, 150, 160, 60)
    print(f"✅ User created: {user.chat_id}")
    
    # Test food operations
    food_crud = FoodCRUD(db)
    chicken = food_crud.get_food_by_name("chicken breast")
    if chicken:
        print(f"✅ Found food: {chicken.name} ({chicken.calories_per_100g} cal/100g)")
    else:
        print("❌ Could not find chicken breast")
        return False
    
    # Test logging
    log_crud = LogCRUD(db)
    log = log_crud.log_food(user.id, chicken.id, 150.0)
    print(f"✅ Logged food: {log.amount_grams}g")
    
    # Test inventory
    inventory_crud = InventoryCRUD(db)
    inventory_crud.add_to_inventory(user.id, chicken.id, 500.0)
    print(f"✅ Added to inventory: 500g")
    
    # Test macro calculations
    macro_calc = MacroCalculator()
    consumed = macro_calc.calculate_food_macros({
        'calories_per_100g': chicken.calories_per_100g,
        'protein_per_100g': chicken.protein_per_100g,
        'carbs_per_100g': chicken.carbs_per_100g,
        'fat_per_100g': chicken.fat_per_100g
    }, 150.0)
    
    print(f"✅ Macro calculation: {consumed.calories:.0f} cal, {consumed.protein:.1f}p")
    
    # Test suggestions
    targets = MacroTargets(2000, 150, 160, 60)
    remaining = macro_calc.calculate_remaining_macros(targets, consumed)
    inventory = inventory_crud.get_user_inventory(user.id)
    suggestions = macro_calc.calculate_meal_suggestion(remaining, inventory)
    
    print(f"✅ Generated {len(suggestions)} suggestions")
    for suggestion in suggestions:
        print(f"   - {suggestion.food_name}: {suggestion.amount_grams:.0f}g")
    
    return True

def test_example_interactions():
    """Test example user interactions"""
    print("\n🎭 Testing example interactions...")
    
    # Initialize database
    db = init_database_with_seed_data()
    user_crud = UserCRUD(db)
    food_crud = FoodCRUD(db)
    log_crud = LogCRUD(db)
    inventory_crud = InventoryCRUD(db)
    macro_calc = MacroCalculator()
    
    # Simulate user journey
    print("\n1. User sets goals: 2000 cal, 150p, 160c, 60f")
    user = user_crud.create_or_update_user(99999, 2000, 150, 160, 60)
    
    print("2. User adds foods to inventory:")
    foods_to_add = [
        ("eggs", 500),
        ("rice", 300),
        ("broccoli", 200),
        ("olive oil", 100)
    ]
    
    for food_name, amount in foods_to_add:
        food = food_crud.get_food_by_name(food_name)
        if food:
            inventory_crud.add_to_inventory(user.id, food.id, amount)
            print(f"   ✅ Added {food_name}: {amount}g")
    
    print("3. User logs breakfast:")
    breakfast_foods = [
        ("eggs", 100),  # 2 eggs
        ("rice", 50)    # 50g rice
    ]
    
    for food_name, amount in breakfast_foods:
        food = food_crud.get_food_by_name(food_name)
        if food:
            log_crud.log_food(user.id, food.id, amount)
            print(f"   ✅ Logged {food_name}: {amount}g")
    
    print("4. Check status:")
    logs = log_crud.get_user_logs_today(user.id)
    consumed = MacroConsumed(0, 0, 0, 0)
    for log in logs:
        food_macros = macro_calc.calculate_food_macros(log, log['amount_grams'])
        consumed.calories += food_macros.calories
        consumed.protein += food_macros.protein
        consumed.carbs += food_macros.carbs
        consumed.fat += food_macros.fat
    
    targets = MacroTargets(user.calories_goal, user.protein_goal, user.carbs_goal, user.fat_goal)
    progress = macro_calc.calculate_daily_progress(targets, consumed)
    
    print(f"   📊 Calories: {consumed.calories:.0f}/{targets.calories:.0f} ({progress['calories']['percentage']:.1f}%)")
    print(f"   💪 Protein: {consumed.protein:.1f}/{targets.protein:.1f}g ({progress['protein']['percentage']:.1f}%)")
    
    print("5. Get meal suggestion:")
    remaining = macro_calc.calculate_remaining_macros(targets, consumed)
    inventory = inventory_crud.get_user_inventory(user.id)
    suggestions = macro_calc.calculate_meal_suggestion(remaining, inventory)
    
    if suggestions:
        print("   🍽️ Suggested meal:")
        for suggestion in suggestions:
            print(f"      - {suggestion.food_name}: {suggestion.amount_grams:.0f}g")
            print(f"        ({suggestion.calories:.0f} cal, {suggestion.protein:.1f}p, {suggestion.carbs:.1f}c, {suggestion.fat:.1f}f)")
    else:
        print("   🎯 No suggestions needed - goals already met!")
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Macro Buddy Bot Tests\n")
    
    try:
        # Test database operations
        if not test_database_operations():
            print("❌ Database tests failed")
            return False
        
        # Test example interactions
        if not test_example_interactions():
            print("❌ Example interaction tests failed")
            return False
        
        print("\n✅ All tests passed! Bot is ready to use.")
        print("\nTo start the bot:")
        print("1. Copy env.example to .env")
        print("2. Add your BOT_TOKEN to .env")
        print("3. Run: python main.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
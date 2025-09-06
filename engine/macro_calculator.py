from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class MacroTargets:
    calories: float
    protein: float
    carbs: float
    fat: float

@dataclass
class MacroConsumed:
    calories: float
    protein: float
    carbs: float
    fat: float

@dataclass
class FoodSuggestion:
    food_name: str
    food_id: int
    amount_grams: float
    calories: float
    protein: float
    carbs: float
    fat: float

class MacroCalculator:
    def __init__(self):
        pass
    
    def calculate_remaining_macros(self, targets: MacroTargets, consumed: MacroConsumed) -> MacroTargets:
        """Calculate remaining macros needed"""
        return MacroTargets(
            calories=max(0, targets.calories - consumed.calories),
            protein=max(0, targets.protein - consumed.protein),
            carbs=max(0, targets.carbs - consumed.carbs),
            fat=max(0, targets.fat - consumed.fat)
        )
    
    def calculate_food_macros(self, food: Dict[str, Any], amount_grams: float) -> MacroConsumed:
        """Calculate macros for a specific amount of food"""
        multiplier = amount_grams / 100.0
        return MacroConsumed(
            calories=food['calories_per_100g'] * multiplier,
            protein=food['protein_per_100g'] * multiplier,
            carbs=food['carbs_per_100g'] * multiplier,
            fat=food['fat_per_100g'] * multiplier
        )
    
    def calculate_meal_suggestion(self, remaining_macros: MacroTargets, 
                                inventory: List[Dict[str, Any]], 
                                max_foods: int = 3) -> List[FoodSuggestion]:
        """
        Calculate optimal meal suggestion from available inventory
        Uses a greedy algorithm to find foods that best fit remaining macros
        """
        if not inventory:
            return []
        
        suggestions = []
        remaining = MacroTargets(
            calories=remaining_macros.calories,
            protein=remaining_macros.protein,
            carbs=remaining_macros.carbs,
            fat=remaining_macros.fat
        )
        
        # Sort foods by macro density (calories per gram) for better suggestions
        sorted_foods = sorted(inventory, key=lambda x: x['calories_per_100g'], reverse=True)
        
        for food in sorted_foods[:max_foods * 2]:  # Check more foods than needed
            if len(suggestions) >= max_foods:
                break
                
            # Calculate optimal amount for this food
            amount = self._calculate_optimal_amount(food, remaining)
            
            if amount > 0 and amount <= food['quantity_grams']:
                # Calculate macros for this amount
                food_macros = self.calculate_food_macros(food, amount)
                
                # Add to suggestions
                suggestion = FoodSuggestion(
                    food_name=food['food_name'],
                    food_id=food['food_id'],
                    amount_grams=amount,
                    calories=food_macros.calories,
                    protein=food_macros.protein,
                    carbs=food_macros.carbs,
                    fat=food_macros.fat
                )
                suggestions.append(suggestion)
                
                # Update remaining macros
                remaining.calories -= food_macros.calories
                remaining.protein -= food_macros.protein
                remaining.carbs -= food_macros.carbs
                remaining.fat -= food_macros.fat
        
        return suggestions
    
    def _calculate_optimal_amount(self, food: Dict[str, Any], remaining: MacroTargets) -> float:
        """
        Calculate optimal amount of food to suggest based on remaining macros
        Prioritizes protein, then calories, then other macros
        """
        if remaining.protein <= 0 and remaining.calories <= 0:
            return 0
        
        # Calculate amounts needed for each macro
        amounts = []
        
        if food['protein_per_100g'] > 0 and remaining.protein > 0:
            amounts.append((remaining.protein / food['protein_per_100g']) * 100)
        
        if food['calories_per_100g'] > 0 and remaining.calories > 0:
            amounts.append((remaining.calories / food['calories_per_100g']) * 100)
        
        if food['carbs_per_100g'] > 0 and remaining.carbs > 0:
            amounts.append((remaining.carbs / food['carbs_per_100g']) * 100)
        
        if food['fat_per_100g'] > 0 and remaining.fat > 0:
            amounts.append((remaining.fat / food['fat_per_100g']) * 100)
        
        if not amounts:
            return 0
        
        # Use the smallest amount that satisfies at least one macro
        optimal_amount = min(amounts)
        
        # Cap at available quantity and reasonable portion size (max 500g)
        optimal_amount = min(optimal_amount, food['quantity_grams'], 500)
        
        # Round to reasonable precision
        return round(optimal_amount, 1)
    
    def calculate_daily_progress(self, targets: MacroTargets, consumed: MacroConsumed) -> Dict[str, Any]:
        """Calculate daily progress with percentages and remaining amounts"""
        remaining = self.calculate_remaining_macros(targets, consumed)
        
        def safe_percentage(consumed_val: float, target_val: float) -> float:
            if target_val == 0:
                return 100.0
            return min(100.0, (consumed_val / target_val) * 100)
        
        return {
            'calories': {
                'consumed': consumed.calories,
                'target': targets.calories,
                'remaining': remaining.calories,
                'percentage': safe_percentage(consumed.calories, targets.calories)
            },
            'protein': {
                'consumed': consumed.protein,
                'target': targets.protein,
                'remaining': remaining.protein,
                'percentage': safe_percentage(consumed.protein, targets.protein)
            },
            'carbs': {
                'consumed': consumed.carbs,
                'target': targets.carbs,
                'remaining': remaining.carbs,
                'percentage': safe_percentage(consumed.carbs, targets.carbs)
            },
            'fat': {
                'consumed': consumed.fat,
                'target': targets.fat,
                'remaining': remaining.fat,
                'percentage': safe_percentage(consumed.fat, targets.fat)
            }
        }
    
    def format_progress_bar(self, percentage: float, width: int = 10) -> str:
        """Create a simple text progress bar"""
        filled = int((percentage / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
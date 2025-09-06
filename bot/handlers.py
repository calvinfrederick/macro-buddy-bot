from telegram import Update
from telegram.ext import ContextTypes
from typing import List, Dict, Any
import re
from datetime import date

from database.crud import UserCRUD, FoodCRUD, LogCRUD, InventoryCRUD
from database.models import Database
from engine.macro_calculator import MacroCalculator, MacroTargets, MacroConsumed

class BotHandlers:
    def __init__(self, db: Database):
        self.db = db
        self.user_crud = UserCRUD(db)
        self.food_crud = FoodCRUD(db)
        self.log_crud = LogCRUD(db)
        self.inventory_crud = InventoryCRUD(db)
        self.macro_calc = MacroCalculator()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        
        # Create or get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            user = self.user_crud.create_or_update_user(chat_id)
        
        welcome_message = """
🥗 **Macro Buddy Bot** 🥗

Welcome! I help you hit your nutrition goals with what you have in your kitchen.

**Quick Start:**
1. Set your daily macro targets: `/setgoal 2000 150 160 60`
2. Add foods to your inventory: `/inventory add eggs 500`
3. Log what you eat: `/log donut 1`
4. Get meal suggestions: `/suggest`

**Commands:**
• `/setgoal <calories> <protein> <carbs> <fat>` - Set daily targets
• `/log <food> <amount>` - Log food eaten today
• `/inventory add <food> <amount>` - Add food to inventory
• `/inventory list` - Show available foods
• `/suggest` - Get meal suggestion
• `/status` - Check your progress

Let's get started! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def setgoal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setgoal command"""
        chat_id = update.effective_chat.id
        
        if not context.args or len(context.args) != 4:
            await update.message.reply_text(
                "❌ Please provide all 4 macro targets!\n\n"
                "Usage: `/setgoal <calories> <protein> <carbs> <fat>`\n"
                "Example: `/setgoal 2000 150 160 60`",
                parse_mode='Markdown'
            )
            return
        
        try:
            calories = int(context.args[0])
            protein = float(context.args[1])
            carbs = float(context.args[2])
            fat = float(context.args[3])
            
            if calories <= 0 or protein < 0 or carbs < 0 or fat < 0:
                raise ValueError("Values must be positive")
            
            # Create or update user
            user = self.user_crud.create_or_update_user(
                chat_id, calories, protein, carbs, fat
            )
            
            await update.message.reply_text(
                f"✅ **Goals set successfully!**\n\n"
                f"📊 **Daily Targets:**\n"
                f"• Calories: {calories:,}\n"
                f"• Protein: {protein}g\n"
                f"• Carbs: {carbs}g\n"
                f"• Fat: {fat}g\n\n"
                f"Now add some foods to your inventory and start logging! 🍽️",
                parse_mode='Markdown'
            )
            
        except ValueError as e:
            await update.message.reply_text(
                "❌ Invalid values! Please use numbers only.\n\n"
                "Example: `/setgoal 2000 150 160 60`",
                parse_mode='Markdown'
            )
    
    async def log_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /log command"""
        chat_id = update.effective_chat.id
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Please provide food name and amount!\n\n"
                "Usage: `/log <food> <amount>`\n"
                "Example: `/log donut 1` or `/log chicken breast 150`",
                parse_mode='Markdown'
            )
            return
        
        # Parse food name and amount
        food_name = context.args[0].lower()
        try:
            amount = float(context.args[1])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount! Please use a number.\n\n"
                "Example: `/log donut 1` or `/log chicken breast 150`",
                parse_mode='Markdown'
            )
            return
        
        # Get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Please set your goals first with `/setgoal`!",
                parse_mode='Markdown'
            )
            return
        
        # Find food
        food = self.food_crud.get_food_by_name(food_name)
        if not food:
            # Try to find similar foods
            similar_foods = self.food_crud.search_foods(food_name)
            if similar_foods:
                suggestions = ", ".join([f.name for f in similar_foods[:5]])
                await update.message.reply_text(
                    f"❌ Food '{food_name}' not found!\n\n"
                    f"Did you mean: {suggestions}?\n\n"
                    f"Or add it to the database first.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ Food '{food_name}' not found!\n\n"
                    f"Try adding it to your inventory first with `/inventory add`",
                    parse_mode='Markdown'
                )
            return
        
        # Log the food
        self.log_crud.log_food(user.id, food.id, amount)
        
        # Calculate macros for this log
        macros = self.macro_calc.calculate_food_macros({
            'calories_per_100g': food.calories_per_100g,
            'protein_per_100g': food.protein_per_100g,
            'carbs_per_100g': food.carbs_per_100g,
            'fat_per_100g': food.fat_per_100g
        }, amount)
        
        await update.message.reply_text(
            f"✅ **Logged successfully!**\n\n"
            f"🍽️ **{food.name.title()}** ({amount}g)\n"
            f"• Calories: {macros.calories:.0f}\n"
            f"• Protein: {macros.protein:.1f}g\n"
            f"• Carbs: {macros.carbs:.1f}g\n"
            f"• Fat: {macros.fat:.1f}g\n\n"
            f"Check your progress with `/status`",
            parse_mode='Markdown'
        )
    
    async def inventory_add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inventory add command"""
        chat_id = update.effective_chat.id
        
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "❌ Please provide food name and amount!\n\n"
                "Usage: `/inventory add <food> <amount>`\n"
                "Example: `/inventory add eggs 500`",
                parse_mode='Markdown'
            )
            return
        
        # Parse food name and amount
        food_name = context.args[0].lower()
        try:
            amount = float(context.args[1])
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid amount! Please use a number.\n\n"
                "Example: `/inventory add eggs 500`",
                parse_mode='Markdown'
            )
            return
        
        # Get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            user = self.user_crud.create_or_update_user(chat_id)
        
        # Find food
        food = self.food_crud.get_food_by_name(food_name)
        if not food:
            # Try to find similar foods
            similar_foods = self.food_crud.search_foods(food_name)
            if similar_foods:
                suggestions = ", ".join([f.name for f in similar_foods[:5]])
                await update.message.reply_text(
                    f"❌ Food '{food_name}' not found!\n\n"
                    f"Did you mean: {suggestions}?",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ Food '{food_name}' not found!\n\n"
                    f"Available foods: Use `/inventory list` to see what's available",
                    parse_mode='Markdown'
                )
            return
        
        # Add to inventory
        self.inventory_crud.add_to_inventory(user.id, food.id, amount)
        
        await update.message.reply_text(
            f"✅ **Added to inventory!**\n\n"
            f"📦 **{food.name.title()}** (+{amount}g)\n\n"
            f"View inventory with `/inventory list`",
            parse_mode='Markdown'
        )
    
    async def inventory_list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inventory list command"""
        chat_id = update.effective_chat.id
        
        # Get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Please set your goals first with `/setgoal`!",
                parse_mode='Markdown'
            )
            return
        
        # Get inventory
        inventory = self.inventory_crud.get_user_inventory(user.id)
        
        if not inventory:
            await update.message.reply_text(
                "📦 **Your inventory is empty!**\n\n"
                "Add some foods with `/inventory add <food> <amount>`\n\n"
                "Available foods: chicken breast, salmon, eggs, rice, oats, bread, potatoes, olive oil, avocado, almonds, donut, luncheon meat, cheese, broccoli, spinach, carrots, banana, apple, milk, greek yogurt",
                parse_mode='Markdown'
            )
            return
        
        # Format inventory list
        message = "📦 **Your Inventory:**\n\n"
        for item in inventory:
            message += f"• **{item['food_name'].title()}**: {item['quantity_grams']:.0f}g\n"
        
        message += f"\nTotal items: {len(inventory)}\n"
        message += "Add more with `/inventory add <food> <amount>`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def suggest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /suggest command"""
        chat_id = update.effective_chat.id
        
        # Get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Please set your goals first with `/setgoal`!",
                parse_mode='Markdown'
            )
            return
        
        # Get today's logs
        logs = self.log_crud.get_user_logs_today(user.id)
        
        # Calculate consumed macros
        consumed = MacroConsumed(0, 0, 0, 0)
        for log in logs:
            food_macros = self.macro_calc.calculate_food_macros(log, log['amount_grams'])
            consumed.calories += food_macros.calories
            consumed.protein += food_macros.protein
            consumed.carbs += food_macros.carbs
            consumed.fat += food_macros.fat
        
        # Calculate remaining macros
        targets = MacroTargets(user.calories_goal, user.protein_goal, user.carbs_goal, user.fat_goal)
        remaining = self.macro_calc.calculate_remaining_macros(targets, consumed)
        
        # Get inventory
        inventory = self.inventory_crud.get_user_inventory(user.id)
        
        if not inventory:
            await update.message.reply_text(
                "❌ **No foods in inventory!**\n\n"
                "Add some foods first with `/inventory add <food> <amount>`",
                parse_mode='Markdown'
            )
            return
        
        # Generate suggestions
        suggestions = self.macro_calc.calculate_meal_suggestion(remaining, inventory)
        
        if not suggestions:
            await update.message.reply_text(
                "🎯 **You're all set for today!**\n\n"
                "Your remaining macros are too small for meaningful suggestions.\n"
                "Check your progress with `/status`",
                parse_mode='Markdown'
            )
            return
        
        # Format suggestions
        message = "🍽️ **Meal Suggestion:**\n\n"
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for suggestion in suggestions:
            message += f"• **{suggestion.food_name.title()}**: {suggestion.amount_grams:.0f}g\n"
            message += f"  └ {suggestion.calories:.0f} cal, {suggestion.protein:.1f}p, {suggestion.carbs:.1f}c, {suggestion.fat:.1f}f\n\n"
            
            total_calories += suggestion.calories
            total_protein += suggestion.protein
            total_carbs += suggestion.carbs
            total_fat += suggestion.fat
        
        message += f"📊 **Totals:**\n"
        message += f"• Calories: {total_calories:.0f}\n"
        message += f"• Protein: {total_protein:.1f}g\n"
        message += f"• Carbs: {total_carbs:.1f}g\n"
        message += f"• Fat: {total_fat:.1f}g\n\n"
        message += f"🎯 **Remaining after suggestion:**\n"
        message += f"• Calories: {remaining.calories - total_calories:.0f}\n"
        message += f"• Protein: {remaining.protein - total_protein:.1f}g\n"
        message += f"• Carbs: {remaining.carbs - total_carbs:.1f}g\n"
        message += f"• Fat: {remaining.fat - total_fat:.1f}g"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        chat_id = update.effective_chat.id
        
        # Get user
        user = self.user_crud.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Please set your goals first with `/setgoal`!",
                parse_mode='Markdown'
            )
            return
        
        # Get today's logs
        logs = self.log_crud.get_user_logs_today(user.id)
        
        # Calculate consumed macros
        consumed = MacroConsumed(0, 0, 0, 0)
        for log in logs:
            food_macros = self.macro_calc.calculate_food_macros(log, log['amount_grams'])
            consumed.calories += food_macros.calories
            consumed.protein += food_macros.protein
            consumed.carbs += food_macros.carbs
            consumed.fat += food_macros.fat
        
        # Calculate progress
        targets = MacroTargets(user.calories_goal, user.protein_goal, user.carbs_goal, user.fat_goal)
        progress = self.macro_calc.calculate_daily_progress(targets, consumed)
        
        # Format status message
        message = f"📊 **Daily Progress - {date.today().strftime('%B %d, %Y')}**\n\n"
        
        # Progress bars
        message += f"🔥 **Calories:** {self.macro_calc.format_progress_bar(progress['calories']['percentage'])}\n"
        message += f"   {progress['calories']['consumed']:.0f}/{progress['calories']['target']:.0f} cal\n\n"
        
        message += f"💪 **Protein:** {self.macro_calc.format_progress_bar(progress['protein']['percentage'])}\n"
        message += f"   {progress['protein']['consumed']:.1f}/{progress['protein']['target']:.1f}g\n\n"
        
        message += f"🍞 **Carbs:** {self.macro_calc.format_progress_bar(progress['carbs']['percentage'])}\n"
        message += f"   {progress['carbs']['consumed']:.1f}/{progress['carbs']['target']:.1f}g\n\n"
        
        message += f"🥑 **Fat:** {self.macro_calc.format_progress_bar(progress['fat']['percentage'])}\n"
        message += f"   {progress['fat']['consumed']:.1f}/{progress['fat']['target']:.1f}g\n\n"
        
        # Remaining macros
        message += f"🎯 **Remaining:**\n"
        message += f"• Calories: {progress['calories']['remaining']:.0f}\n"
        message += f"• Protein: {progress['protein']['remaining']:.1f}g\n"
        message += f"• Carbs: {progress['carbs']['remaining']:.1f}g\n"
        message += f"• Fat: {progress['fat']['remaining']:.1f}g\n\n"
        
        if logs:
            message += f"📝 **Today's Logs:**\n"
            for log in logs[:5]:  # Show last 5 logs
                message += f"• {log['food_name'].title()}: {log['amount_grams']:.0f}g\n"
            if len(logs) > 5:
                message += f"... and {len(logs) - 5} more\n"
        else:
            message += "📝 **No logs today yet**\n"
        
        message += f"\nGet suggestions with `/suggest`"
        
        await update.message.reply_text(message, parse_mode='Markdown')
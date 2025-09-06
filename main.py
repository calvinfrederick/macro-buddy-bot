#!/usr/bin/env python3
"""
Macro Buddy Bot - Telegram bot for nutrition and fitness tracking
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN
from database.init_db import init_database_with_seed_data
from database.models import Database
from bot.handlers import BotHandlers

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class MacroBuddyBot:
    def __init__(self):
        self.db = None
        self.handlers = None
        self.application = None
    
    def initialize(self):
        """Initialize database and bot handlers"""
        try:
            # Initialize database with seed data
            self.db = init_database_with_seed_data()
            logger.info("Database initialized successfully")
            
            # Initialize bot handlers
            self.handlers = BotHandlers(self.db)
            logger.info("Bot handlers initialized successfully")
            
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.handlers.start_command))
            self.application.add_handler(CommandHandler("setgoal", self.handlers.setgoal_command))
            self.application.add_handler(CommandHandler("log", self.handlers.log_command))
            self.application.add_handler(CommandHandler("inventory", self._inventory_command))
            self.application.add_handler(CommandHandler("suggest", self.handlers.suggest_command))
            self.application.add_handler(CommandHandler("status", self.handlers.status_command))
            
            logger.info("Bot application configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def _inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /inventory command with subcommands"""
        if not context.args:
            await update.message.reply_text(
                "📦 **Inventory Commands:**\n\n"
                "• `/inventory add <food> <amount>` - Add food to inventory\n"
                "• `/inventory list` - Show current inventory\n\n"
                "Example: `/inventory add eggs 500`",
                parse_mode='Markdown'
            )
            return
        
        subcommand = context.args[0].lower()
        
        if subcommand == "add":
            # Remove 'add' from args and pass to add handler
            context.args = context.args[1:]
            await self.handlers.inventory_add_command(update, context)
        elif subcommand == "list":
            await self.handlers.inventory_list_command(update, context)
        else:
            await update.message.reply_text(
                "❌ Unknown inventory command!\n\n"
                "Use `/inventory add` or `/inventory list`",
                parse_mode='Markdown'
            )
    
    async def start_bot(self):
        """Start the bot"""
        try:
            self.initialize()
            
            logger.info("Starting Macro Buddy Bot...")
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
            
        except Exception as e:
            logger.error(f"Bot failed to start: {e}")
            raise
    
    async def stop_bot(self):
        """Stop the bot gracefully"""
        if self.application and self.application.running:
            await self.application.stop()
        logger.info("Bot stopped")

def main():
    """Main entry point"""
    # Initialize database and bot handlers
    db = init_database_with_seed_data()
    logger.info("Database initialized successfully")
    
    handlers = BotHandlers(db)
    logger.info("Bot handlers initialized successfully")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", handlers.start_command))
    application.add_handler(CommandHandler("setgoal", handlers.setgoal_command))
    application.add_handler(CommandHandler("log", handlers.log_command))
    application.add_handler(CommandHandler("inventory", _inventory_command))
    application.add_handler(CommandHandler("suggest", handlers.suggest_command))
    application.add_handler(CommandHandler("status", handlers.status_command))
    
    logger.info("Bot application configured successfully")
    
    # Start the bot
    logger.info("Starting Macro Buddy Bot...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

async def _inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /inventory command with subcommands"""
    if not context.args:
        await update.message.reply_text(
            "📦 **Inventory Commands:**\n\n"
            "• `/inventory add <food> <amount>` - Add food to inventory\n"
            "• `/inventory list` - Show current inventory\n\n"
            "Example: `/inventory add eggs 500`",
            parse_mode='Markdown'
        )
        return
    
    subcommand = context.args[0].lower()
    
    # Get database and handlers
    db = init_database_with_seed_data()
    handlers = BotHandlers(db)
    
    if subcommand == "add":
        # Remove 'add' from args and pass to add handler
        context.args = context.args[1:]
        await handlers.inventory_add_command(update, context)
    elif subcommand == "list":
        await handlers.inventory_list_command(update, context)
    else:
        await update.message.reply_text(
            "❌ Unknown inventory command!\n\n"
            "Use `/inventory add` or `/inventory list`",
            parse_mode='Markdown'
        )

if __name__ == "__main__":
    main()
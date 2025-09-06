import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///macro_buddy.db')

# Bot settings
MAX_FOODS_PER_SUGGESTION = 3
DEFAULT_MACRO_TARGETS = {
    'calories': 2000,
    'protein': 150,
    'carbs': 160,
    'fat': 60
}
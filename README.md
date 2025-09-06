# Macro Buddy Bot 🥗

A Telegram bot that helps you hit your nutrition goals with what you already have in your kitchen. Instead of rigid meal plans, it lets you set macro targets, log what you eat, manage your food inventory, and get smart suggestions to close your macro gap.

## ✨ Features

- 🎯 **Set Daily Macro Targets** - Customize calories, protein, carbs, and fat goals
- 📝 **Log Food Consumption** - Track what you eat with simple commands
- 📦 **Inventory Management** - Keep track of available foods in your kitchen
- 🤖 **Smart Suggestions** - Get AI-curated meal suggestions from your inventory
- 📊 **Progress Tracking** - Visual progress bars and macro breakdowns
- 🍽️ **20+ Pre-loaded Foods** - Common foods with accurate macro data

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd macro-buddy-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp env.example .env
   # Edit .env and add your BOT_TOKEN
   ```

4. **Test the bot**
   ```bash
   python3 test_bot.py
   ```

5. **Run the bot**
   ```bash
   python3 main.py
   ```

## 🤖 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and help | `/start` |
| `/setgoal` | Set daily macro targets | `/setgoal 2000 150 160 60` |
| `/log` | Log food eaten today | `/log donut 1` |
| `/inventory add` | Add food to inventory | `/inventory add eggs 500` |
| `/inventory list` | Show available foods | `/inventory list` |
| `/suggest` | Get meal suggestion | `/suggest` |
| `/status` | Check daily progress | `/status` |

## 📊 Example Usage

```
User: /setgoal 2000 150 160 60
Bot: ✅ Goals set successfully!
     📊 Daily Targets:
     • Calories: 2,000
     • Protein: 150g
     • Carbs: 160g
     • Fat: 60g

User: /inventory add eggs 500
Bot: ✅ Added to inventory!
     📦 Eggs (+500g)

User: /log eggs 100
Bot: ✅ Logged successfully!
     🍽️ Eggs (100g)
     • Calories: 155
     • Protein: 13.0g
     • Carbs: 1.1g
     • Fat: 11.0g

User: /suggest
Bot: 🍽️ Meal Suggestion:
     • Rice: 150g
       └ 195 cal, 4.1p, 42.0c, 0.5f
     • Broccoli: 200g
       └ 68 cal, 5.6p, 14.0c, 0.8f
```

## 🏗️ Architecture

```
macro-buddy-bot/
├── main.py                 # Bot entry point
├── config.py              # Configuration management
├── database/
│   ├── models.py          # SQLite models
│   ├── crud.py            # Database operations
│   └── init_db.py         # Database initialization
├── bot/
│   └── handlers.py        # Command handlers
├── engine/
│   └── macro_calculator.py # Suggestion algorithm
└── data/
    └── foods.json         # Seed food data
```

## 🧮 Macro Calculation Engine

The bot uses a rule-based algorithm to suggest optimal meal combinations:

1. **Calculate remaining macros** needed for the day
2. **Analyze available foods** in user's inventory
3. **Use greedy algorithm** to find 2-3 foods that best fit remaining macros
4. **Prioritize protein and calories** for balanced suggestions
5. **Respect quantity limits** and reasonable portion sizes

## 🗄️ Database Schema

- **users**: chat_id, macro_targets
- **foods**: name, macros_per_100g
- **logs**: user_id, food_id, amount, date
- **inventory**: user_id, food_id, quantity_available

## 🚀 Deployment

### Railway
1. Connect your GitHub repository to Railway
2. Set `BOT_TOKEN` environment variable
3. Deploy automatically

### Render
1. Create new Web Service
2. Connect repository
3. Set environment variables
4. Deploy

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python3 test_bot.py
```

Tests include:
- Database operations
- Macro calculations
- Example user interactions
- Suggestion algorithm

## 📝 Tech Stack

- **Backend**: Python 3.8+
- **Bot Framework**: python-telegram-bot
- **Database**: SQLite
- **Deployment**: Railway/Render ready

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

---

**Ready to start your macro journey?** Get your bot token from [@BotFather](https://t.me/botfather) and start tracking! 🚀 

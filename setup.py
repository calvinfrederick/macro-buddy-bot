#!/usr/bin/env python3
"""
Setup script for Macro Buddy Bot
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Macro Buddy Bot...\n")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            run_command("cp env.example .env", "Creating .env file")
            print("📝 Please edit .env and add your BOT_TOKEN")
        else:
            print("⚠️  env.example not found, please create .env manually")
    
    # Test the bot
    if not run_command("python3 test_bot.py", "Running tests"):
        print("⚠️  Tests failed, but setup may still work")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Get a bot token from @BotFather on Telegram")
    print("2. Add BOT_TOKEN to your .env file")
    print("3. Run: python3 main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
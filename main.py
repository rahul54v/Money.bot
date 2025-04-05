# -*- coding: utf-8 -*-
"""
Enhanced Telegram Earning Bot Template

Features:
- Basic commands (/start, /help, /balance, /me)
- Simulated earning task system (/earn) with random rewards
- Simulated withdrawal system (/withdraw) with minimum balance check
- Placeholder referral link generation (/referral)
- Persistent user data using PicklePersistence (saves to a file)
- Basic error handling and logging

Requires: python-telegram-bot v20+
Install/Upgrade: pip install --upgrade python-telegram-bot
"""

import logging
import os
import random
import pickle  # Used by PicklePersistence

# Core telegram types
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# Extensions for application, handlers, context, persistence
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PicklePersistence, # Saves data to a file
)
from telegram.constants import ParseMode # For formatting messages

# --- Configuration ---

# !!!!!!!!!! EXTREMELY CRITICAL SECURITY WARNING !!!!!!!!!!
# THE TOKEN YOU PROVIDED (7696664813:AAH-gsi_k_HwpAEHA4MV4v0J8Doo_YpOfZo) IS COMPROMISED
# BECAUSE IT WAS SHARED PUBLICLY. ANYONE CAN CONTROL YOUR BOT WITH IT.
# ===> YOU MUST REVOKE IT IMMEDIATELY VIA @BotFather <===
# ===> THEN, GENERATE A NEW TOKEN AND KEEP IT SECRET <===
# Replace the placeholder below with your NEW, SECRET token.
# Using environment variables is the standard secure practice for production.
# Example: BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

BOT_TOKEN = "7696664813:AAH-gsi_k_HwpAEHA4MV4v0J8Doo_YpOfZo" # <-- REPLACE THIS WITH YOUR *NEW, SECRET* TOKEN

# Bot constants
MIN_WITHDRAWAL_AMOUNT = 5.00 # Example minimum withdrawal
PERSISTENCE_FILE = "user_bot_data.pkl" # File to store user data

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO # Set to logging.DEBUG for more detailed output
)
# Reduce noise from underlying HTTP library
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- Data Persistence Setup ---
# PicklePersistence saves bot_data, user_data, chat_data to a file.
# This makes user balances survive bot restarts.
persistence = PicklePersistence(filepath=PERSISTENCE_FILE)

# --- Helper Function for User Data ---
def get_user_data(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> dict:
    """
    Safely retrieves user data from context.user_data, initializing if necessary.
    context.user_data is managed by the Persistence layer.
    """
    # Initialize user_data for the user if it doesn't exist
    if user_id not in context.user_data:
        logger.info(f"Initializing data for new user: {user_id}")
        context.user_data[user_id] = {
            "balance": 0.0,
            "tasks_completed": 0,
            "referrals_made": 0, # Placeholder for future referral tracking
        }
    # Ensure all expected keys exist, adding defaults if needed (for users from older versions)
    context.user_data[user_id].setdefault("balance", 0.0)
    context.user_data[user_id].setdefault("tasks_completed", 0)
    context.user_data[user_id].setdefault("referrals_made", 0)
    return context.user_data[user_id]

# --- Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start. Welcomes user, initializes data, shows help."""
    user = update.effective_user
    user_id = user.id
    logger.info(f"User {user_id} ({user.username or 'NoUsername'}) started/restarted the bot.")
    # Ensure user data is initialized by accessing it via the helper
    get_user_data(context, user_id)

    welcome_message = (
        f"Hi {user.mention_html()}! 👋\n\n"
        "Welcome to the Enhanced Earning Bot!\n\n"
        "You can earn simulated currency by completing tasks. "
        "Use /help to see all available commands."
    )
    await update.message.reply_html(welcome_message)
    # Optionally, call help directly after start
    # await help_command(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /help. Displays available commands."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested help.")

    help_text = """
ℹ️ **Available Commands:**

/start - Welcome message & initialize
/help - Show this help message
/balance - Check your current balance
/me - Show your profile (balance & tasks)
/earn - Find a new task to earn
/withdraw - Request a (simulated) withdrawal
/referral - Get your referral link (placeholder)
    """
    await update.message.reply_html(help_text) # Use HTML for simple formatting

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /balance. Shows user's current simulated balance."""
    user_id = update.effective_user.id
    user_data = get_user_data(context, user_id)
    balance = user_data.get("balance", 0.0)
    logger.info(f"User {user_id} checked balance: ${balance:.2f}")

    await update.message.reply_text(f"💰 Your current balance is: **${balance:.2f}**")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /me. Shows user's profile info."""
    user_id = update.effective_user.id
    user_data = get_user_data(context, user_id)
    balance = user_data.get("balance", 0.0)
    tasks = user_data.get("tasks_completed", 0)
    referrals = user_data.get("referrals_made", 0) # Example usage
    logger.info(f"User {user_id} requested profile.")

    profile_text = (
        f"👤 **Your Profile**\n\n"
        f"💰 Balance: ${balance:.2f}\n"
        f"✅ Tasks Completed: {tasks}\n"
        # f"👥 Referrals: {referrals}" # Uncomment when referral tracking is implemented
    )
    await update.message.reply_text(profile_text)

async def earn_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /earn. Offers a simulated task with random reward."""
    user_id = update.effective_user.id
    logger.info(f"User {user_id} requested an earning task.")
    get_user_data(context, user_id) # Ensure user data exists

    # --- More Dynamic Placeholder Task Generation ---
    possible_rewards = [0.05, 0.10, 0.02, 0.15, 0.08]
    reward = random.choice(possible_rewards)
    task_descriptions = [
        f"Watch a quick ad video (+${reward:.2f}).",
        f"Join our partner news channel (+${reward:.2f}).",
        f"Answer a simple 2-question poll (+${reward:.2f}).",
        f"Visit a sponsor's link for 10s (+${reward:.2f}).",
    ]
    task_description = random.choice(task_descriptions)
    task_id = f"task_{random.randint(10000, 99999)}" # Example unique ID
    # --- End Placeholder ---

    keyboard = [
        [InlineKeyboardButton(f"✅ Accept Task (+${reward:.2f})", callback_data=f"earn_{task_id}_{reward}")],
        [InlineKeyboardButton("❌ Skip Task", callback_data="skip_task")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"👇 **New Task Available!**\n\n"
        # f"🆔 Task ID: `{task_id}`\n" # Optional: show task ID
        f"📝 Description: {task_description}",
        reply_markup=reply_markup
    )

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /withdraw. Simulates withdrawal if balance meets minimum."""
    user_id = update.effective_user.id
    user_data = get_user_data(context, user_id)
    balance = user_data.get("balance", 0.0)
    logger.info(f"User {user_id} initiated withdrawal command. Balance: ${balance:.2f}")

    if balance >= MIN_WITHDRAWAL_AMOUNT:
        # --- Placeholder Withdrawal Logic ---
        # In a real bot: Ask for payment details (use ConversationHandler), validate,
        # record in DB, process payment, update DB, notify user.
        await update.message.reply_text(
            f"💸 **Withdrawal Simulation**\n\n"
            f"Requesting withdrawal of: ${balance:.2f}\n"
            f"Minimum required: ${MIN_WITHDRAWAL_AMOUNT:.2f}\n\n"
            f"✅ Your request is eligible! In a real bot, we would now ask for your payment details (e.g., PayPal email, Crypto Address).\n\n"
            f"**(Simulation only - no funds are moved)**"
        )
        # Optional: Deduct balance for simulation
        # user_data["balance"] = 0.0
        # logger.info(f"Simulated withdrawal processed for user {user_id}. Balance reset for test.")
    else:
        await update.message.reply_text(
            f"⚠️ **Insufficient Balance**\n\n"
            f"You need at least **${MIN_WITHDRAWAL_AMOUNT:.2f}** to make a withdrawal.\n"
            f"Your current balance is ${balance:.2f}."
        )

async def referral_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /referral. Generates a placeholder referral link."""
    user = update.effective_user
    user_id = user.id
    bot_username = context.bot.username # Get the bot's username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    logger.info(f"User {user_id} requested referral link.")

    # Basic referral message (tracking needs more work)
    referral_text = (
        f"🎉 **Invite & Earn!** (Placeholder)\n\n"
        f"Share your unique link with friends:\n"
        f"`{referral_link}`\n\n"
        f"(Note: Referral tracking and rewards are not implemented in this template.)"
    )
    # Use MarkdownV2 for code formatting, requires escaping special chars in link if any
    await update.message.reply_markdown_v2(referral_text.replace('.', '\\.').replace('-', '\\-'))
    # Or simpler: await update.message.reply_text(referral_text) but without code formatting

# --- Callback Query Handler (Handles Button Presses) ---

async def button_press_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles inline keyboard button presses."""
    query = update.callback_query
    await query.answer() # Acknowledge the press

    user = query.from_user
    user_id = user.id
    callback_data = query.data
    user_data = get_user_data(context, user_id) # Ensure data exists

    logger.info(f"User {user_id} pressed button. Callback data: '{callback_data}'")

    # Task Acceptance Logic
    if callback_data.startswith("earn_"):
        try:
            parts = callback_data.split("_")
            if len(parts) != 3: raise ValueError("Incorrect earn callback format")
            task_id = parts[1]
            reward = float(parts[2])

            # --- Placeholder Task Completion (Real bot needs verification) ---
            user_data["balance"] += reward
            user_data["tasks_completed"] += 1
            new_balance = user_data["balance"]
            tasks_done = user_data["tasks_completed"]
            # --- End Placeholder ---

            await query.edit_message_text(
                text=f"✅ **Task Completed!**\n\n"
                     #f"🆔 Task ID: `{task_id}`\n" # Optional
                     f"🎉 You earned: +${reward:.2f}\n\n"
                     f"💰 New balance: **${new_balance:.2f}**\n"
                     f"📈 Total tasks completed: {tasks_done}"
            )
            logger.info(f"User {user_id} completed task {task_id}. Awarded ${reward:.2f}. New balance: ${new_balance:.2f}")

        except (IndexError, ValueError, KeyError, TypeError) as e:
            logger.error(f"Error processing 'earn' callback: Data='{callback_data}', User={user_id}, Error: {e}", exc_info=True)
            try:
                await query.edit_message_text(text="❌ Error processing task. Try `/earn` again.")
            except Exception as edit_error:
                logger.error(f"Failed to edit message after task error: {edit_error}")

    # Task Skipping Logic
    elif callback_data == "skip_task":
        logger.info(f"User {user_id} skipped task.")
        await query.edit_message_text(text="🗑️ Task skipped. Use `/earn` to find a new one.")

    # Handle Unknown Button Data
    else:
        logger.warning(f"Unknown callback data from user {user_id}: {callback_data}")
        try:
            await query.edit_message_text(text="❓ Unknown button action.")
        except Exception as edit_error:
             logger.error(f"Failed to edit message after unknown callback: {edit_error}")


# --- Fallback Handlers ---

async def unknown_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles unrecognized commands."""
    command = update.message.text
    user_id = update.effective_user.id
    logger.warning(f"User {user_id} sent unknown command: {command}")
    await update.message.reply_text(
        f"😕 Sorry, I don't understand the command `{command}`. "
        f"Use /help to see the list of available commands."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Logs errors encountered by the bot."""
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    # You could add more sophisticated error handling here, like notifying an admin


# --- Main Function ---

def main() -> None:
    """Sets up the bot, registers handlers, and starts polling."""
    # --- Essential Token Check ---
    if BOT_TOKEN == "YOUR_NEW_SECRET_BOT_TOKEN" or not BOT_TOKEN:
        print("\n" + "="*60)
        print(" FATAL ERROR: BOT TOKEN MISSING OR IS A PLACEHOLDER! ")
        print("="*60)
        print("1. GO TO @BotFather on Telegram.")
        print("2. REVOKE the token you shared publicly (ends in ...YpOfZo).")
        print("3. GENERATE a NEW API token.")
        print("4. PASTE the NEW token into the BOT_TOKEN variable in this script.")
        print("5. KEEP THE NEW TOKEN SECRET!")
        print("="*60 + "\n")
        return # Stop execution

    print("Starting bot...")
    logger.info(f"Using persistence file: {PERSISTENCE_FILE}")
    logger.info("Initializing Application...")

    # Build Application with token and persistence
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .persistence(persistence)
        .build()
    )

    # --- Register Handlers ---
    # Order matters for MessageHandlers vs CommandHandlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("balance", balance_command))
    application.add_handler(CommandHandler("me", profile_command)) # /me is common alias for profile
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("earn", earn_command))
    application.add_handler(CommandHandler("withdraw", withdraw_command))
    application.add_handler(CommandHandler("referral", referral_command))

    # CallbackQueryHandler for button presses
    application.add_handler(CallbackQueryHandler(button_press_handler))

    # MessageHandler for unknown commands (must be AFTER CommandHandlers)
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command_handler))

    # Error handler to log errors
    application.add_error_handler(error_handler)

    # --- Start Polling ---
    logger.info("Starting bot polling...")
    # run_polling fetches updates and dispatches them to handlers
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    logger.info("Bot polling stopped.")
    print("Bot stopped.")


# --- Script Execution ---
if __name__ == "__main__":
    main()

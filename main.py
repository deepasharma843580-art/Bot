import telebot
import requests
import os
import time
import threading

BOT_TOKEN  = os.getenv("BOT_TOKEN",  "7507385917:AAG3MmJO2VlzJAfvyjKeu_hqfQ0F3dCztow")
API_URL    = os.getenv("API_URL",    "https://nexo-wallet.vercel.app")
ADMIN_PASS = os.getenv("ADMIN_PASS", "8435")
ADMIN_TG   = os.getenv("ADMIN_TG",  "8509393869")

WEEKLY_URL = f"{API_URL}/weeklywithdrawals?admin_pass={ADMIN_PASS}"
TODAY_URL  = f"{API_URL}/todaywithdraws?admin_pass={ADMIN_PASS}"
LEADER_URL = f"{API_URL}/leaderboard/users"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True, num_threads=8)

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG = {
    "owner":    "@OWNERXNEXO",
    "channel":  "@NEXOWALLET_OFFICIAL",
    "website":  "https://nexo-wallet.vercel.app",
    "help_text": (
        "┌───────────────────┐\n"
        "     ❓ <b>NEXO HELP</b>\n"
        "└───────────────────┘\n\n"
        "💸 /tip [amt] — Reply karke tip do\n"
        "💰 /balance — Balance dekho\n"
        "🏆 /leaderboard — Top users\n"
        "📋 /txn [id] — Transaction dhundho\n"
        "📊 /weeklyw — Weekly withdrawals\n"
        "📅 /td — Aaj ki withdrawals\n"
        "✨ /features — Sab features\n"
        "🆔 /id — Apna TG ID dekho\n"
        "💼 /wallet — Wallet open karo\n\n"
        "👑 Owner: @OWNERXNEXO\n"
        "📢 Channel: @NEXOWALLET_OFFICIAL\n"
        "🌐 nexo-wallet.vercel.app\n\n"
        "🛡️ <b>NEXO WALLET</b>"
    )
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def main_keyboard(chat_id):
    if chat_id > 0:
        kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.row("💰 Wallet", "🏆 Leaderboard")
        kb.row("🔍 Find Txn", "❓ Help")
        return kb
    return None

def reply(msg, text, reply_markup=None, inline_markup=None):
    chat_id = msg.chat.id
    kb = inline_markup if inline_markup else main_keyboard(chat_id)
    try:
        bot.send_message(
            chat_id, text,
            reply_to_message_id=msg.message_id,
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Send error: {e}")

def api_get(url):
    try:
        r = requests.get(url, timeout=8)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ── /start ────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["start"])
def cmd_start(msg):
    name = msg.from_user.first_name or "User"
    uid  = msg.from_user.id
    reply(msg,
        f"┌─────────────────────┐\n"
        f"  👋 <b>NEXO WALLET</b>\n"
        f"└─────────────────────┘\n\n"
        f"🙋 Hey <b>{name}</b>!\n"
        f"🆔 Your ID: <code>{uid}</code>\n\n"
        f"👑 Owner: <b>{CONFIG['owner']}</b>\n"
        f"📢 Channel: <b>{CONFIG['channel']}</b>\n"
        f"🌐 <b>{CONFIG['website']}</b>\n\n"
        f"💎 <i>India ka #1 Digital Wallet</i>\n"
        f"🛡️ <b>NEXO WALLET</b>"
    )

# ── /id ───────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["id"])
def cmd_id(msg):
    reply(msg,
        f"🔵 <b>Telegram IDs</b>\n\n"
        f"👤 Your ID: <code>{msg.from_user.id}</code>\n"
        f"💬 Chat ID: <code>{msg.chat.id}</code>\n\n"
        f"🛡️ <b>NEXO WALLET</b>"
    )

# ── /balance ──────────────────────────────────────────────────────────────────
def do_balance(msg):
    tg_id = msg.from_user.id
    data  = api_get(f"{API_URL}/tgid?id={tg_id}&balance")
    if data.get("status") == "success":
        reply(msg,
            f"┌──────────────────┐\n"
            f"  💰 <b>BALANCE</b>\n"
            f"└──────────────────┘\n\n"
            f"👤 <b>{data['name']}</b>\n"
            f"💵 Balance: <b>₹{data['balance']}</b>\n\n"
            f"🛡️ <b>NEXO WALLET</b>"
        )
    else:
        reply(msg, f"❌ <b>Error:</b> {data.get('message', 'Unknown error')}")

@bot.message_handler(commands=["balance"])
def cmd_balance(msg): do_balance(msg)

@bot.message_handler(func=lambda m: m.text == "💰 Wallet")
def btn_wallet(msg): do_balance(msg)

# ── /tip ──────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["tip"])
def cmd_tip(msg):
    args = msg.text.split()

    if not msg.reply_to_message:
        return reply(msg,
            "⚠️ <b>Reply karke use karo!</b>\n\n"
            "Kisi ke message pe reply karo aur likho:\n"
            "<code>/tip 100</code>"
        )

    if msg.reply_to_message.from_user.is_bot:
        return reply(msg, "🤖 <b>Bot ko tip nahi de sakte!</b>")

    if len(args) < 2:
        return reply(msg, "❌ <b>Amount daalo!</b>\nExample: <code>/tip 100</code>")

    try:
        amount = float(args[1])
        if amount < 1:
            raise ValueError
    except ValueError:
        return reply(msg, "❌ <b>Sahi amount daalo!</b>\nExample: <code>/tip 100</code>")

    sender_id   = msg.from_user.id
    sender_name = msg.from_user.first_name or "User"
    recv_id     = msg.reply_to_message.from_user.id
    recv_name   = msg.reply_to_message.from_user.first_name or "User"

    if sender_id == recv_id:
        return reply(msg, "🙅 <b>Khud ko tip nahi de sakte!</b>")

    data = api_get(f"{API_URL}/tgid?id={sender_id}&sent={recv_id}&amount={amount}")

    if data.get("status") == "success":
        reply(msg,
            f"┌──────────────────────┐\n"
            f"  🎉 <b>TIP SUCCESSFUL!</b>\n"
            f"└──────────────────────┘\n\n"
            f"🟢 <b>{sender_name}</b> ➜ <b>{recv_name}</b>\n"
            f"💸 Amount: <b>₹{amount}</b>\n\n"
            f"Khush rahiye dono moj mein 😆\n\n"
            f"🧾 Txn: <code>{data['tx_id']}</code>\n"
            f"🛡️ <b>NEXO WALLET</b>"
        )
    elif data.get("status") == "fail":
        reply(msg,
            f"┌──────────────────┐\n"
            f"  ❌ <b>TIP FAILED!</b>\n"
            f"└──────────────────┘\n\n"
            f"🔴 Balance kam hai!\n"
            f"💵 Available: <b>₹{data.get('balance', '?')}</b>\n\n"
            f"🛡️ <b>NEXO WALLET</b>"
        )
    else:
        reply(msg, f"❌ <b>Error:</b> {data.get('message', 'Unknown error')}")

# ── /leaderboard ──────────────────────────────────────────────────────────────
def do_leaderboard(msg):
    data = api_get(LEADER_URL)
    if not isinstance(data, list) or not data:
        return reply(msg, "❌ <b>Leaderboard data nahi mila!</b>")

    medals = ["🥇", "🥈", "🥉"]
    text = (
        "┌──────────────────────┐\n"
        "  🏆 <b>NEXO LEADERBOARD</b>\n"
        "└──────────────────────┘\n\n"
    )
    for i, u in enumerate(data[:10]):
        m = medals[i] if i < 3 else f"🔹 {i+1}."
        text += f"{m} <b>{u['name']}</b> — ₹{u['balance']}\n"
    text += "\n🛡️ <b>NEXO WALLET</b>"
    reply(msg, text)

@bot.message_handler(commands=["leaderboard"])
def cmd_leaderboard(msg): do_leaderboard(msg)

@bot.message_handler(func=lambda m: m.text == "🏆 Leaderboard")
def btn_leaderboard(msg): do_leaderboard(msg)

# ── /txn ──────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["txn"])
def cmd_txn(msg):
    args = msg.text.split()
    if len(args) < 2:
        return reply(msg, "🔍 Transaction ID bhejo:\n<code>/txn NX12345</code>")

    txn_id = args[1].strip()
    data   = api_get(f"{API_URL}/transfer/txn/{txn_id}")

    if data.get("status") == "success":
        reply(msg,
            f"┌────────────────────┐\n"
            f"  🔍 <b>TRANSACTION</b>\n"
            f"└────────────────────┘\n\n"
            f"🧾 ID: <code>{data['tx_id']}</code>\n"
            f"🟢 From: <b>{data['sender']}</b>\n"
            f"🔵 To: <b>{data['receiver']}</b>\n"
            f"💵 Amount: <b>₹{data['amount']}</b>\n"
            f"📅 Date: <b>{data['date']}</b>\n\n"
            f"🛡️ <b>NEXO WALLET</b>"
        )
    else:
        reply(msg, f"❌ Transaction nahi mili: <b>{data.get('message')}</b>")

@bot.message_handler(func=lambda m: m.text == "🔍 Find Txn")
def btn_txn(msg):
    reply(msg, "🔍 Transaction ID bhejo:\n<code>/txn NX12345</code>")

# ── /weeklyw ──────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["weeklyw"])
def cmd_weeklyw(msg):
    data = api_get(WEEKLY_URL)
    if not isinstance(data, list) or not data:
        return reply(msg, "📊 <b>Is hafte koi withdrawal nahi hui!</b>")

    text = (
        "┌──────────────────────┐\n"
        "  📊 <b>WEEKLY WITHDRAWALS</b>\n"
        "└──────────────────────┘\n\n"
    )
    for i, w in enumerate(data[:15]):
        text += f"🔹 {i+1}. <b>{w['name']}</b> — ₹{w['amount']}\n"
    text += "\n🛡️ <b>NEXO WALLET</b>"
    reply(msg, text)

# ── /td ───────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["td"])
def cmd_td(msg):
    data = api_get(TODAY_URL)
    if not isinstance(data, list) or not data:
        return reply(msg, "📅 <b>Aaj koi withdrawal nahi hui!</b>")

    text = (
        "┌──────────────────────┐\n"
        "  📅 <b>TODAY WITHDRAWALS</b>\n"
        "└──────────────────────┘\n\n"
    )
    for i, w in enumerate(data[:15]):
        text += f"🔹 {i+1}. <b>{w['name']}</b> — ₹{w['amount']}\n"
    text += "\n🛡️ <b>NEXO WALLET</b>"
    reply(msg, text)

# ── /features ─────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["features"])
def cmd_features(msg):
    reply(msg,
        f"┌──────────────────────┐\n"
        f"  ✨ <b>NEXO FEATURES</b>\n"
        f"└──────────────────────┘\n\n"
        f"💸 P2P Transfer\n"
        f"🎁 Lifafa — Random envelope\n"
        f"🃏 Cards — Virtual cards\n"
        f"⭕ Circles — Group savings\n"
        f"🏆 Leaderboard\n"
        f"🤖 Telegram Bot\n"
        f"💰 Tip System\n\n"
        f"🌐 <b>{CONFIG['website']}</b>\n"
        f"📢 <b>{CONFIG['channel']}</b>\n\n"
        f"🛡️ <b>NEXO WALLET</b>"
    )

# ── /help ─────────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["help"])
def cmd_help(msg): reply(msg, CONFIG["help_text"])

@bot.message_handler(func=lambda m: m.text == "❓ Help")
def btn_help(msg): reply(msg, CONFIG["help_text"])

# ── /wallet ───────────────────────────────────────────────────────────────────
@bot.message_handler(commands=["wallet"])
def cmd_wallet(msg):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.add(telebot.types.InlineKeyboardButton(
        "🌐 Open Wallet",
        url=f"{CONFIG['website']}/dashboard"
    ))
    reply(msg,
        f"💼 <b>NEXO WALLET</b>\n\n"
        f"Apna wallet open karo 👇\n\n"
        f"📢 <b>{CONFIG['channel']}</b>\n"
        f"👑 <b>{CONFIG['owner']}</b>\n\n"
        f"🛡️ <b>NEXO WALLET</b>",
        inline_markup=kb
    )

# ── ADMIN PANEL ───────────────────────────────────────────────────────────────
@bot.message_handler(commands=["admin"])
def cmd_admin(msg):
    if str(msg.from_user.id) != ADMIN_TG:
        return reply(msg, "❌ <b>Access denied!</b>")
    reply(msg,
        f"⚙️ <b>NEXO Admin Panel</b>\n\n"
        f"/setowner [text]\n"
        f"/setchannel [text]\n"
        f"/setwebsite [url]\n"
        f"/sethelp [text]\n\n"
        f"<b>Current:</b>\n"
        f"Owner: {CONFIG['owner']}\n"
        f"Channel: {CONFIG['channel']}\n"
        f"Website: {CONFIG['website']}"
    )

@bot.message_handler(commands=["setowner"])
def cmd_setowner(msg):
    if str(msg.from_user.id) != ADMIN_TG: return
    val = msg.text.split(None, 1)
    if len(val) < 2: return
    CONFIG["owner"] = val[1].strip()
    reply(msg, f"✅ Owner updated: <b>{CONFIG['owner']}</b>")

@bot.message_handler(commands=["setchannel"])
def cmd_setchannel(msg):
    if str(msg.from_user.id) != ADMIN_TG: return
    val = msg.text.split(None, 1)
    if len(val) < 2: return
    CONFIG["channel"] = val[1].strip()
    reply(msg, f"✅ Channel updated: <b>{CONFIG['channel']}</b>")

@bot.message_handler(commands=["setwebsite"])
def cmd_setwebsite(msg):
    if str(msg.from_user.id) != ADMIN_TG: return
    val = msg.text.split(None, 1)
    if len(val) < 2: return
    CONFIG["website"] = val[1].strip()
    reply(msg, f"✅ Website updated: <b>{CONFIG['website']}</b>")

@bot.message_handler(commands=["sethelp"])
def cmd_sethelp(msg):
    if str(msg.from_user.id) != ADMIN_TG: return
    val = msg.text.split(None, 1)
    if len(val) < 2: return
    CONFIG["help_text"] = val[1].strip()
    reply(msg, "✅ <b>Help text updated!</b>")

# ── Start polling ─────────────────────────────────────────────────────────────
print("🤖 NEXO Wallet Bot running...")

while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)

import telebot
from telebot import types
import random
import datetime
import json
import os

# === Bot Token ===
BOT_TOKEN = ""
bot = telebot.TeleBot(BOT_TOKEN)

# === Contact username ===
CONTACT_USERNAME = "rana_editz_00"

# === Save data JSON ===
DATA_FILE = "data.json"

# === Sample Mosque/Namaz Images ===
IMAGES = [
    "https://i.ibb.co/n0L1v2h/mosque1.jpg",
    "https://i.ibb.co/bmJNYvV/mosque2.jpg",
    "https://i.ibb.co/p4Vj5zN/mosque3.jpg",
    "https://i.ibb.co/dj2s7mz/mosque4.jpg",
    "https://i.ibb.co/3zNw1X3/mosque5.jpg"
]

# === Namaz Times (example fixed times for Dhaka) ===
NAMAZ_TIMES = {
    "Fajr": "04:10",
    "Dhuhr": "1:00",
    "Asr": "16:00",
    "Maghrib": "18:15",
    "Isha": "19:45"
}

# === Load/Save Functions ===
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"groups": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# === Create Buttons ===
def get_main_buttons():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    # Button 1: Join Me Your Group
    join_button = types.InlineKeyboardButton("Join Me Your Group", callback_data="join_group")

    # Button 2: Select City
    city_button = types.InlineKeyboardButton("Select City", callback_data="select_city")

    # Button 3: Contact Me
    contact_button = types.InlineKeyboardButton("Contact Me", url=f"https://t.me/{CONTACT_USERNAME}")

    keyboard.add(join_button, city_button, contact_button)
    return keyboard

# === Start Command ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 আসসালামু আলাইকুম!\n\nএই বট আপনাকে ৫ ওয়াক্ত নামাজের সময় মনে করিয়ে দিবে।",
        reply_markup=get_main_buttons()
    )

# === Handle Button Clicks ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "join_group":
        bot.answer_callback_query(call.id, "➡️ Add this bot to your group manually via Telegram ‘Add Members’.")
        bot.send_message(call.message.chat.id, "ℹ️ আমাকে আপনার গ্রুপে অ্যাড করুন, তাহলেই আমি কাজ শুরু করবো।")

    # 64 জেলা
DISTRICTS = [
    "Bagerhat", "Bandarban", "Barguna", "Barisal", "Bhola", "Bogura", "Brahmanbaria",
    "Chandpur", "Chattogram", "Chuadanga", "Comilla", "Cox's Bazar", "Dhaka", "Dinajpur",
    "Faridpur", "Feni", "Gaibandha", "Gazipur", "Gopalganj", "Habiganj", "Jamalpur",
    "Jashore", "Jhalokathi", "Jhenaidah", "Joypurhat", "Khagrachhari", "Khulna", "Kishoreganj",
    "Kurigram", "Kushtia", "Lakshmipur", "Lalmonirhat", "Madaripur", "Magura", "Manikganj",
    "Meherpur", "Moulvibazar", "Munshiganj", "Mymensingh", "Naogaon", "Narail", "Narayanganj",
    "Narsingdi", "Natore", "Netrokona", "Nilphamari", "Noakhali", "Pabna", "Panchagarh",
    "Patuakhali", "Pirojpur", "Rajbari", "Rajshahi", "Rangamati", "Rangpur", "Satkhira",
    "Shariatpur", "Sherpur", "Sirajganj", "Sunamganj", "Sylhet", "Tangail", "Thakurgaon",
    "Chandpur"
]

# Select City Button
elif call.data == "select_city":
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for district in DISTRICTS:
        keyboard.add(types.InlineKeyboardButton(district, callback_data=f"city_{district}"))
    bot.send_message(call.message.chat.id, "🏙 আপনার জেলা সিলেক্ট করুন:", reply_markup=keyboard)

    elif call.data.startswith("city_"):
        city = call.data.split("_")[1]
        group_id = str(call.message.chat.id)

        if group_id not in data["groups"]:
            data["groups"][group_id] = {}

        data["groups"][group_id]["city"] = city
        save_data(data)

        bot.send_message(call.message.chat.id, f"✅ শহর সেট হয়েছে: {city}")

# === Send Random Namaz Message ===
def send_namaz_message(group_id, namaz, after=False):
    text = ""
    if after:
        text = f"✅ {namaz} নামাজ শেষ হয়েছে। সবাই দোয়া করতে ভুলবেন না।"
    else:
        text = f"🕌 এখন {namaz} নামাজের আযান হচ্ছে। সবাই নামাজে যান।"

    photo = random.choice(IMAGES)
    bot.send_photo(group_id, photo, caption=text, reply_markup=get_main_buttons())

# === Scheduler Loop (Railway/VPS এ লাগবে) ===
import threading, time

def scheduler():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for namaz, t in NAMAZ_TIMES.items():
            if now == t:
                for group_id in data["groups"]:
                    send_namaz_message(group_id, namaz, after=False)
            # নামাজের ২০ মিনিট পর "after" মেসেজ দিবে
            namaz_end = (datetime.datetime.strptime(t, "%H:%M") + datetime.timedelta(minutes=20)).strftime("%H:%M")
            if now == namaz_end:
                for group_id in data["groups"]:
                    send_namaz_message(group_id, namaz, after=True)
        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

# === Run Bot ===
print("🤖 Bot is running...")
bot.infinity_polling()

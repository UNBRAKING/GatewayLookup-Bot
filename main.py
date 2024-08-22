from telethon import TelegramClient, events, Button
from telethon.tl.types import Channel, Chat, User
from telethon.tl.functions.messages import GetFullChat
from collections import defaultdict
import os
import random
import string
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

api_id = '26614080'  # Keep this as it is
api_hash = '7d2c9a5628814e1430b30a1f0dc0165b'  # same here
client_token = '7198617195:AAERy67YMdCs7J2-kiJMzvl291oJ0H9_oNk'

# Admin IDs and other initial configurations
admin_ids = [5606990991]  # Example admin IDs
vip = [6822280712]
pre_id = []
r_us = []
site_checking = {}
credits = {}
generated_codes = []

def is_user_admin(user_id):
    return user_id in admin_ids

message_counts = defaultdict(lambda: 0)
last_message_time = defaultdict(lambda: datetime.min)
time_window = timedelta(seconds=15)
pre_window = timedelta(seconds=10)
credit = {}

def normalize_url(url):
    parsed_url = urllib.parse.urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return normalized_url

def generate_redeem_code():
    code = '-'.join(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)) for _ in range(4))
    return code

premium = "premium.txt"
if not os.path.exists(premium):
    open(premium, 'a').close()

def read_premium():
    with open(premium, 'r') as file:
        premium_ids = file.readlines()
        return [int(user_id.strip()) for user_id in premium_ids if user_id.strip().isdigit()]

def add_to_premium(user_id):
    with open(premium, 'a') as file:
        file.write(f"{user_id}\n")

client = TelegramClient('session_name', api_id, api_hash).start(bot_token=client_token)

def read_user_credit(user_id):
    user_credit_file = f"{user_id}_credit.txt"
    if os.path.exists(user_credit_file):
        with open(user_credit_file, "r") as file:
            return int(file.read())
    return 0

@client.on(events.NewMessage(pattern='/refresh'))
async def handle_refresh(event):
    user_id = event.sender_id
    user_credit_file = f"{user_id}_credit.txt"
    credit_value = read_user_credit(user_id)
    
    if user_id in pre_id:
        if user_id in r_us:
            await event.respond('Already refreshing done!')
        else:
            credit_value += 25
            await event.respond('💫')
            r_us.append(user_id)
    elif user_id in vip:
        if user_id in r_us:
            await event.respond('Already refreshing done!')
        else:
            credit_value += 50000
            await event.respond('💫')
    else:
        if user_id in r_us:
            await event.respond('Already refreshing done!')
        else:
            credit_value += 5
        await event.respond('💫')
        r_us.append(user_id)
    
    with open(user_credit_file, "w") as file:
        file.write(str(credit_value))

@client.on(events.NewMessage(pattern='/info'))
async def handle_info(event):
    user_id = event.sender_id
    user_credit = read_user_credit(user_id)
    
    if user_id in vip:
        user = event.sender
        fn = f"[{user.first_name}](tg://user?id={user.id})"
        await event.respond(f"""**Your Details** 🔐
Welcome {fn}
**See your account status:**

👨🏻‍💼 Plan: `VIP 👑`
💳 Credits: `♾️`

🔥 Status:
⊛ Account ID: `{event.sender.id}`
⊛ Name: {fn}""", reply_to=event)
    elif user_id in pre_id:
        user = event.sender
        fn = f"[{user.first_name}](tg://user?id={user.id})"
        await event.respond(f"""**Your Details** 🔐
Welcome {fn}
**See your account status:**

👨🏻‍💼 Plan: `Premium`
💳 Credits: `{user_credit}`

🔥 Status:
⊛ Account ID: `{event.sender.id}`
⊛ Name: {fn}""", reply_to=event)
    else:
        user = event.sender
        fn = f"[{user.first_name}](tg://user?id={user.id})"
        await event.respond(f"""**Your Details** 🔐
Welcome {fn}
**See your account status:**

👨🏻‍💼 Plan: `Free`
💳 Credits: `{user_credit}`

🔥 Status:
⊛ Account ID: `{event.sender.id}`
⊛ Name: {fn}""", reply_to=event)

@client.on(events.NewMessage(pattern='/codes'))
async def handle_codes(event):
    user_id = event.sender_id
    if user_id in vip:
        await event.respond('🔹These are the Codes which were generated and not used yet:\n\n' + str(generated_codes))

@client.on(events.NewMessage(pattern='/create'))
async def handle_create(event):
    user_id = event.sender_id
    if user_id in vip:
        try:
            _, num_codes = event.raw_text.split()
            num_codes = int(num_codes)
            codes = [generate_redeem_code() for _ in range(num_codes)]
            generated_codes.extend(codes)
            code_message = ' ┏━━━━━━━⍟\n┃ Here is your Redeem codes ✅\n┗━━━━━━━━━━━⊛\n\n⊙ ' + '\n⊙ '.join(f'`{code}`' for code in codes) + ' \n\n━━━━━━━━━━━━━━━━\nPlease note that `02` credits each. You can redeem them using the command \n`/redeem`'
            await event.respond(code_message, parse_mode='Markdown')
        except (ValueError, TypeError):
            await event.respond("Usage: /create <number_of_codes>")

@client.on(events.NewMessage(pattern='/redeem'))
async def handle_redeem(event):
    redeem_code = event.raw_text.split()[-1].strip()
    if redeem_code in generated_codes:
        generated_codes.remove(redeem_code)
        user_id = event.sender.id
        credit_value = read_user_credit(user_id)
        new_credit_value = credit_value + 2
        
        with open(f"{user_id}_credit.txt", "w") as file:
            file.write(str(new_credit_value))
        
        msg = (f"""New user Redeemed ✅

__User Details__ :
⊛ **Username** : @{event.sender.username}
⊛ **User ID** : `{event.sender.id}`
⊛ **Code** : `{redeem_code}`
⊛ **Bot** : @GatewayLookup_Robot""")
        await client.send_message(-1002239204465, msg)
        
        await event.respond(f"Redeemed Successfully ✅\n\n__Details__ :\n**⊛ Credits Added** : `02` \n**User ID** : `{event.sender_id}`\n\n❛ ━━━━･━━━━･━━━━ ❜", parse_mode='Markdown', reply_to=event)
    else:
        await event.respond('⚠️ The provided redeem code is invalid or has already been redeemed. Please provide a valid code.', reply_to=event)

@client.on(events.NewMessage(pattern='/approve'))
async def approve_user(event):
    if event.sender_id in vip:
        try:
            user_id = int(event.text.split(" ")[1])
            add_to_premium(user_id)
            pre_id.append(user_id)
            
            await event.respond(f"**Added** {user_id} to **Premium** list. ✅")
        except (IndexError, ValueError):
            await event.respond("Invalid usage. The correct format is: /approve <user_id>")

def find_payment_gateways(response_text):
    detected_gateways = []
    keywords = [
        "paypal", "stripe", "braintree", "square", "cybersource", "authorize.net", "2checkout",
        "adyen", "worldpay", "sagepay", "checkout.com", "shopify", "razorpay", "bolt", "paytm",
        "venmo", "pay.google.com", "revolut", "eway", "woocommerce", "upi", "apple.com", "payflow",
        "payeezy", "paddle", "payoneer", "recurly", "klarna", "paysafe", "webmoney", "payeer", "payu", "skrill"
    ]
    for keyword in keywords:
        if keyword in response_text.lower():
            detected_gateways.append(keyword.title())
    
    if not detected_gateways:
        detected_gateways.append("Unknown")
    
    return ', '.join(detected_gateways)

@client.on(events.NewMessage(pattern='/check'))
async def check_website(event):
    url = event.raw_text.split(maxsplit=1)[1] if len(event.raw_text.split()) > 1 else None
    if url:
        normalized_url = normalize_url(url)
        try:
            response = requests.get(normalized_url, timeout=10)
            detected_gateways = find_payment_gateways(response.text)
            await event.respond(f"Payment gateways detected: {detected_gateways}")
        except requests.RequestException as e:
            await event.respond(f"Error checking URL: {str(e)}")
    else:
        await event.respond("Usage: /check <url>")

@client.on(events.NewMessage(pattern='/ban'))
async def handle_ban(event):
    if is_user_admin(event.sender_id):
        try:
            _, user_id = event.raw_text.split()
            user_id = int(user_id)
            user = await client.get_entity(user_id)
            chat = await client.get_chat(user_id)
            await chat.kick_participant(user_id)
            await event.respond(f"User {user_id} has been banned.")
        except Exception as e:
            await event.respond(f"Error banning user: {str(e)}")
    else:
        await event.respond("You do not have permission to use this command.")

if __name__ == "__main__":
    client.start()
    client.run_until_disconnected()

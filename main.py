import asyncio
import mimetypes

# PyHost Cloud के /etc/mime.types परमिशन एरर को बाईपास करने के लिए
mimetypes.init(files=[])

from telethon import TelegramClient, events

API_ID = 32731558
API_HASH = "e59a439ffd53247f5ab1766aa098cc09"

client = TelegramClient("vimal_session", API_ID, API_HASH)

# =============================================================
# [ यहाँ अपने मैसेज लिखें ]
# जितने चाहें उतने मैसेज नीचे जोड़ें या बदलें:
# =============================================================
MESSAGES_LIST = [
    "नमस्ते भाई!",
    "कैसे हो आप?",
    "यह ऑटोमेटेड मैसेज टेस्टिंग है।"
]
# =============================================================

DELAY_SECONDS = 5  # हर मैसेज के बीच का गैप (सेकंड में)
running_task = None
target_chat = None
mention_user = None

async def sender_loop():
    global target_chat, mention_user
    index = 0
    try:
        while True:
            base_msg = MESSAGES_LIST[index % len(MESSAGES_LIST)]
            
            # अगर किसी को मेंशन करना है तो आगे @ जोड़कर हाईलाइट करेगा
            if mention_user:
                final_msg = f"{mention_user} {base_msg}"
            else:
                final_msg = base_msg
                
            await client.send_message(target_chat, final_msg)
            print(f"[SENT] -> {final_msg}")
            index += 1
            await asyncio.sleep(DELAY_SECONDS)
    except asyncio.CancelledError:
        pass

@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    global running_task, target_chat, mention_user
    text = event.raw_text.strip()

    # उपयोग करने के तरीके:
    # 1. सीधे यूज़र के डीएम में: .start @username
    # 2. ग्रुप में बिना मेंशन के: .start -100123456789
    # 3. ग्रुप में किसी को टैग करके: .start -100123456789 @username
    if text.startswith(".start"):
        parts = text.split()
        if len(parts) < 2:
            await event.reply("⚠️ सही फॉर्मेट डालें:\n`.start @username`\nया\n`.start <Chat_ID> [@mention]`")
            return

        chat_input = parts[1]
        
        # चैट आईडी या यूज़रनेम पहचानना
        if chat_input.startswith("-") or chat_input.isdigit():
            target_chat = int(chat_input)
        else:
            target_chat = chat_input

        # अगर तीसरे शब्द में मेंशन दिया है
        if len(parts) >= 3:
            mention_user = parts[2]
        else:
            mention_user = None

        if running_task and not running_task.done():
            running_task.cancel()

        running_task = asyncio.create_task(sender_loop())
        tag_info = f" (टैग: {mention_user})" if mention_user else ""
        await event.reply(f"✅ ऑटोमेशन शुरू हो गया!\nटारगेट: `{target_chat}`{tag_info}")

    elif text == ".stop":
        if running_task and not running_task.done():
            running_task.cancel()
            running_task = None
            mention_user = None
            await event.reply("🛑 ऑटोमेशन रोक दिया गया।")
        else:
            await event.reply("⚠️ अभी कोई टास्क नहीं चल रहा है।")

print("⚡ बॉट एक्टिव है...")
client.start()
client.run_until_disconnected()

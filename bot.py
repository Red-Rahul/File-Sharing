import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.idle import idle

# Configs
API_HASH = os.getenv('API_HASH', 'b33ae6134914c512d7f4246048af4a9c')
APP_ID = int(os.getenv('APP_ID', '25075806'))
BOT_TOKEN = os.getenv('BOT_TOKEN', '7151281361:AAGsXDCAyq2GPL5FlbC5kB8WYmbuLQpbRxg')
TRACK_CHANNEL = os.getenv('TRACK_CHANNEL', 'filedatabase07')
OWNER_ID = os.getenv('OWNER_ID', 'all')

# Bot client
xbot = Client('File-Sharing', api_id=APP_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
xbot_username = None
media_group_id = 0

# Buttons
START_BUTTONS = [
    [
        InlineKeyboardButton('Source', url='https://github.com/X-Gorn/File-Sharing'),
        InlineKeyboardButton('Project Channel', url='https://t.me/xTeamBots'),
    ],
    [InlineKeyboardButton('Author', url="https://t.me/xgorn")],
]

# /start command
@xbot.on_message(filters.command('start') & filters.private)
async def start_handler(bot, message):
    global xbot_username
    if not xbot_username:
        xbot_username = (await bot.get_me()).username

    if message.text == '/start':
        await message.reply_text(
            "I'm File-Sharing!\nYou can share any telegram files and get the sharing link using this bot!\n\n/help for more details...",
            reply_markup=InlineKeyboardMarkup(START_BUTTONS)
        )
        return

    if len(message.command) != 2:
        return

    code = message.command[1]
    if '-' in code:
        msg_id = code.split('-')[-1]
        unique_id = '-'.join(code.split('-')[:-1])
        if not msg_id.isdigit():
            return

        try:
            check_media_group = await bot.get_media_group(TRACK_CHANNEL, int(msg_id))
            check = check_media_group[0]
        except Exception:
            check = await bot.get_messages(TRACK_CHANNEL, int(msg_id))

        if check.empty:
            await message.reply_text('Error: [Message does not exist]')
            return

        file = (
            check.video or check.photo or check.audio or
            check.document or check.sticker or check.animation or
            check.voice or check.video_note
        )
        if not file:
            return

        unique_idx = file.file_unique_id
        if unique_id != unique_idx.lower():
            return

        try:
            await bot.copy_media_group(message.from_user.id, TRACK_CHANNEL, int(msg_id))
        except Exception:
            await check.copy(message.from_user.id)


# /help
@xbot.on_message(filters.command('help') & filters.private)
async def help_handler(bot, message):
    await message.reply_text(
        "Supported file types:\n\n- Video\n- Audio\n- Photo\n- Document\n- Sticker\n- GIF\n- Voice note\n- Video note\n\nIf bot didn't respond, contact @xgorn",
        quote=True
    )


# Send reply with link
async def __reply(update, copied):
    global xbot_username
    if not xbot_username:
        xbot_username = (await xbot.get_me()).username

    file = (
        copied.video or copied.photo or copied.audio or
        copied.document or copied.sticker or copied.animation or
        copied.voice or copied.video_note
    )
    if not file:
        await copied.delete()
        return

    unique_idx = file.file_unique_id
    msg_id = copied.message_id

    await update.reply_text(
        'Here is Your Sharing Link:',
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Sharing Link',
                                  url=f'https://t.me/{xbot_username}?start={unique_idx.lower()}-{msg_id}')]
        ])
    )
    await asyncio.sleep(0.5)


# Media group handler
@xbot.on_message(filters.media & filters.private & filters.media_group)
async def group_handler(bot, update):
    global media_group_id
    if OWNER_ID != 'all' and int(OWNER_ID) != update.from_user.id:
        return

    if int(media_group_id) != int(update.media_group_id):
        media_group_id = update.media_group_id
        copied = (await bot.copy_media_group(TRACK_CHANNEL, update.from_user.id, update.message_id))[0]
        await __reply(update, copied)


# Single media handler
@xbot.on_message(filters.media & filters.private & ~filters.media_group)
async def media_handler(bot, update):
    if OWNER_ID != 'all' and int(OWNER_ID) != update.from_user.id:
        return

    copied = await update.copy(TRACK_CHANNEL)
    await __reply(update, copied)


# Startup
async def startup():
    global xbot_username
    await xbot.start()
    xbot_username = (await xbot.get_me()).username
    print(f"✅ Bot started as @{xbot_username}")
    if OWNER_ID != 'all':
        await xbot.send_message(int(OWNER_ID), "✅ Bot has started and is running!")
    await idle()

if __name__ == '__main__':
    asyncio.run(startup())

xbot.run()

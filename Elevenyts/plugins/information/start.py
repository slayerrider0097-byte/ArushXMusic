# # ==========================================================
# Copyright (c) 2026 Arush
# All Rights Reserved.
#
# Project      : Arush API Telegram Music Bot
# Powered By   : Arush
# Type         : API Based Telegram Music Bot
#
# Bot          : @ArushApibot
# Channel      : https://t.me/arush
# GitHub       : https://github.com/Arush
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================

import asyncio

from pyrogram import enums, errors, filters, types

from Elevenyts import app, config, db, lang
from Elevenyts.helpers import buttons, utils


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats - shows help menu with image."""
    try:
        await m.delete()
    except Exception:
        pass
    
    try:
        await m.reply_photo(
            photo=config.START_IMG,
            caption=m.lang["help_menu"],
            reply_markup=buttons.help_markup(m.lang),
            quote=True,
        )
    except Exception:
        await m.reply_text(
            text=m.lang["help_menu"],
            reply_markup=buttons.help_markup(m.lang),
            quote=True,
        )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """
    Handle /start command - welcome message for users.

    - In private chat: Shows animation (heart reaction, 4 text messages
      that vanish one by one, sticker that stays 4 sec then vanishes,
      then main welcome)
    - In group chat: Shows short welcome message
    - Adds new users to database
    - Sends log to logger group for new users
    """
    # Auto-delete command message in group chats
    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass
    
    if not message.from_user:
        return

    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE

    # ------------------- PRIVATE CHAT ANIMATION -------------------
    if private:
        try:
            # 1. React with 鉂わ笍 to the /start message
            await message.react("鉂わ笍")

            # 2. Four animated text messages with different styles
            msgs = [
                "馃専 <b>Welcome to Arush X Music</b> 馃専",
                "馃挅 <b>Welcome to the Ultimate Music Experience</b>",
                "馃幍 <b>High Quality 鈥� Fast 鈥� Smooth Streaming</b>",
                "鉁� Powered by <a href='https://t.me/innocentpapaboltee'>Arush X Music</a> 鉁�"
            ]

            # Send each with a 1鈥憇econd pause and delete
            for text in msgs:
                msg = await message.reply_text(text, quote=True)
                await asyncio.sleep(1.5)
                await msg.delete()

            # 3. Send the sticker (provided ID)
            sticker_msg = await message.reply_sticker(
                "CAACAgQAAxkBAAEfyZlqP18UrjI4J46VayG5TkwWGiDdOQACfBIAAs37OFEtwgAB7hLz92k8BA"
            )

            # Wait 4 seconds, then delete the sticker
            await asyncio.sleep(4)
            await sticker_msg.delete()

        except Exception as e:
            # Log error but continue to main message
            print(f"Start animation error: {e}")

    # ------------------- MAIN WELCOME MESSAGE -------------------
    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    key = buttons.start_key(message.lang, private)
    try:
        await message.reply_photo(
            photo=config.START_IMG,
            caption=_text,
            reply_markup=key,
            quote=not private,
        )
    except errors.ChatSendPhotosForbidden:
        await message.reply_text(
            text=_text,
            reply_markup=key,
            quote=not private,
        )

    # For private chats, add user to database if new
    if private:
        if await db.is_user(message.from_user.id):
            return
        await utils.send_log(message)
        return await db.add_user(message.from_user.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    """Handle /playmode or /settings command - show group settings."""
    try:
        await message.delete()
    except Exception:
        pass
    
    admin_only = await db.get_play_mode(message.chat.id)
    _language = "en"
    await utils.safe_text(
        message,
        message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):
    """Handle new member events - detect when bot is added to groups."""
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    for member in message.new_chat_members:
        if member.id == app.id:
            if await db.is_chat(message.chat.id):
                return
            await db.add_chat(message.chat.id)


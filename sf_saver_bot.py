#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simple telegram bot that save everything that you push into him
# Written by Snownoise
# Snownoise@gmail.com
# 1.0
# 2020-03-09

import sf_bot_config as cfg
import telebot
#from telebot import types
import os
#from time import strftime
from datetime import datetime
import urllib.request as urllib_req

bot = telebot.TeleBot(cfg.token)

def handle_forwarders(message, for_filename=False):
    """
    This will check if message is forwarded from someone and changes titles accordingly
    """
    # If message is forwarded from user, use different notification in log
    if "forward_sender_name" in message.json:
        if for_filename:
            fwd_timestamp = datetime.fromtimestamp(message.json["forward_date"]).strftime("%Y-%m-%d-%H%M%S")
            msg_username = '{} at {}'.format(message.json["forward_sender_name"], fwd_timestamp)
        else:
            fwd_timestamp = datetime.fromtimestamp(message.json["forward_date"]).strftime("%Y-%m-%d %H:%M:%S")
            msg_username = 'FRWD> @{} at {}'.format(message.json["forward_sender_name"], fwd_timestamp)

    # If message is forwarded from channel, use different notification in log
    elif "forward_from_chat" in message.json:

        if for_filename:
            fwd_timestamp = datetime.fromtimestamp(message.json["forward_date"]).strftime("%Y-%m-%d-%H%M%S")
            msg_username = '{} at {}'.format(message.json["forward_from_chat"]["title"], fwd_timestamp)
        else:
            fwd_timestamp = datetime.fromtimestamp(message.json["forward_date"]).strftime("%Y-%m-%d %H:%M:%S")
            msg_username = 'CHNL> {} aka {} at {}'.format(message.json["forward_from_chat"]["title"],
                message.json["forward_from_chat"]["username"], fwd_timestamp)

    # Normal messages
    else:
        if for_filename:
            msg_username = '{}'.format(message.from_user.username)
        else:
            msg_username = '@{}'.format(message.from_user.username)

    return msg_username


# Default handler for /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, cfg.help_msg)


# Handler for text messages
@bot.message_handler(content_types=["text"])
def handle_message(message):
    if message.chat.username in cfg.userlist:

        currDate = datetime
        logname = os.path.join(cfg.log_dir, 'tglog_{}_{}.txt'.format(currDate.now().strftime("%Y-%m-%d"), str(message.chat.username)))
        msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d %H:%M:%S")
        msg_username = handle_forwarders(message)

        log_text = '{}\t{}\n{}\n\n'.format(msg_timestamp, msg_username, message.text)

        with open(logname, 'a+') as logfile:
            logfile.write(log_text)


# Handler for pictures
@bot.message_handler(content_types=["photo"])
def handle_message(message):
    if message.chat.username in cfg.userlist:

        currDate = datetime
        logname = os.path.join(cfg.log_dir, 'tglog_{}_{}.txt'.format(currDate.now().strftime("%Y-%m-%d"), str(message.chat.username)))
        msg_username = handle_forwarders(message, True)
        msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d_%H%M%S")

        remote_filename = str(bot.get_file(message.json["photo"][-1]["file_id"]).file_path)
        pict_url = "https://api.telegram.org/file/bot{}/{}".format(cfg.token, remote_filename)

        local_filename = os.path.join(cfg.log_dir,'{}_{}_{}'.format(msg_timestamp, msg_username, remote_filename[remote_filename.rfind('/')+1:]))
        urllib_req.urlretrieve (pict_url, local_filename)


# Infinite bot polling
bot.polling(none_stop=True)

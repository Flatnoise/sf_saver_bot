#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simple telegram bot that save everything that you push into him
# Written by Snownoise
# Snownoise@gmail.com
# 1.1
# 2020-03-14

import sf_bot_config as cfg
import telebot
import os
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

def get_unique_filename(filename):
    """
    Check if file is alredy exists;
    If yes - add number(s) to filename until unique filename is found
    """
    counter = 0
    extension = None
    short_name = None
    while os.path.isfile(filename):
        if counter == 0:
            if filename.find('.') == -1:
                extension = ''
                short_name = filename
            else:
                extension = filename[filename.rfind('.') + 1:]
                short_name = filename[:filename.rfind('.')]
        counter += 1
        filename = '{} ({}).{}'.format(short_name, counter, extension)

    return filename

def generate_logname(username):
    """
    Generate filename for writing text massages.
    """
    currDate = datetime
    logname = os.path.join(cfg.log_dir, 'tglog_{}_{}.txt'.format(currDate.now().strftime("%Y-%m-%d"), str(username)))
    return logname



# Default handler for /start and /help commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, cfg.help_msg)


# Handler for text messages
@bot.message_handler(content_types=["text"])
def handle_message(message):
    if message.chat.username in cfg.userlist:

        # creating text message
        msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d %H:%M:%S")
        msg_username = handle_forwarders(message)
        log_text = '{}\t{}\n{}\n\n'.format(msg_timestamp, msg_username, message.text)

        # writing text in file (with append)
        logname = generate_logname(message.chat.username)
        with open(logname, 'a+') as logfile:
            logfile.write(log_text)


# Handler for pictures
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if message.chat.username in cfg.userlist:

        # getting username and datetime for writing them in picture's filename
        msg_username = handle_forwarders(message, True)
        msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d_%H%M%S")

        remote_filename = str(bot.get_file(message.json["photo"][-1]["file_id"]).file_path)     # filename on TG server
        pict_url = "https://api.telegram.org/file/bot{}/{}".format(cfg.token, remote_filename)  # full link for file on TG server

        # generating local filename and download file
        local_filename = os.path.join(cfg.log_dir, '{}_{}_{}'.format(msg_timestamp,
            msg_username, remote_filename[remote_filename.rfind('/') + 1:]))
        urllib_req.urlretrieve(pict_url, local_filename)

        # if file have a text with picture - write it to log
        if "caption" in message.json:
            logname = generate_logname(message.chat.username)
            log_text = '{}\t{}\tMessage attached to the picture: {}\n{}\n\n'.format(msg_timestamp, msg_username,
                local_filename, message.json["caption"])

            with open(logname, 'a+') as logfile:
                if log_text: logfile.write(log_text)



# Handler for videos
@bot.message_handler(content_types=["video"])
def handle_video(message):
    if message.chat.username in cfg.userlist:

        # getting username and datetime for writing them in video's filename
        msg_username = handle_forwarders(message, True)
        msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d_%H%M%S")

        remote_filename = str(bot.get_file(message.json["video"]["file_id"]).file_path)             # filename on TG server
        video_url = "https://api.telegram.org/file/bot{}/{}".format(cfg.token, remote_filename)     # full link for file on TG server

        # generating local filename and download file
        local_filename = os.path.join(cfg.log_dir, '{}_{}_{}'.format(msg_timestamp, msg_username,
            remote_filename[remote_filename.rfind('/') + 1:]))
        urllib_req.urlretrieve(video_url, local_filename)

        # if file have a text with video - write it to log
        if "caption" in message.json:
            logname = generate_logname(message.chat.username)
            log_text = '{}\t{}\tMessage attached to the video: {}\n{}\n\n'.format(msg_timestamp, msg_username,
                local_filename, message.json["caption"])

            with open(logname, 'a+') as logfile:
                if log_text: logfile.write(log_text)

# Handler for documents
@bot.message_handler(content_types=["document"])
def handle_document(message):
    if message.chat.username in cfg.userlist:

        remote_filename = str(bot.get_file(message.json["document"]["file_id"]).file_path)      # filename on TG server
        file_url = "https://api.telegram.org/file/bot{}/{}".format(cfg.token, remote_filename)  # full link for file on TG server

        # check if local filename is unique and if it's not - generate new filename
        local_filename = get_unique_filename(os.path.join(cfg.log_dir, message.json["document"]["file_name"]))

        # if file have a text with it - write it to log
        if "caption" in message.json:
            logname = generate_logname(message.chat.username)
            msg_username = handle_forwarders(message, True)
            msg_timestamp = datetime.fromtimestamp(message.date).strftime("%Y-%m-%d_%H%M%S")
            log_text = '{}\t{}\tMessage attached to file: {}\n{}\n\n'.format(msg_timestamp, msg_username,
                message.json["document"]["file_name"], message.json["caption"])

            with open(logname, 'a+') as logfile:
                if log_text: logfile.write(log_text)

        # file download
        urllib_req.urlretrieve(file_url, local_filename)


# Infinite bot polling
bot.polling(none_stop=True)

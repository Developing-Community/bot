import datetime
import json
import os

import requests
import telepot
from flask import Flask, request
from flask.json import jsonify
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from config import TOKEN, BOT_API_HOST_URL, PROXY

application = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def logadd(text):
    f = open(os.path.join(BASE_DIR, "bot.log"), "a")
    f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + text + '\n')
    f.close()


def keyboard_maker(keyboard_texts):
    mykb = []
    for x in keyboard_texts:
        l = []
        for y in x:
            l.append(KeyboardButton(text=y))
        mykb.append(l)
    return mykb


@application.route('/send-message/', methods=['POST'])
def send_message():
    data = json.loads(request.get_json(force=True))
    keyboard = keyboard_maker(data['keyboard'])
    for chat_id in data['chat_ids']:
        bot.sendMessage(chat_id,
                        data['message'],
                        'Markdown',
                        reply_markup=ReplyKeyboardMarkup(
                            keyboard=keyboard
                        ),
                        )
    response = {
        'status': 'success'
    }
    return jsonify(response)


def handle_pv(msg):
    data = json.dumps({
        'msg': msg
    })
    response = requests.post(url=BOT_API_HOST_URL + '/api/bot/handle-pv/',
                             headers={"Content-type": "application/json"},
                             data=data).json()

    keyboard = keyboard_maker(response['keyboard'])
    bot.sendMessage(response['chat_id'],
                    response['message'],
                    'Markdown',
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=keyboard
                    ))


def handle_gp(msg):
    data = json.dumps({
        'msg': msg
    })
    response = requests.post(url=BOT_API_HOST_URL + '/api/bot/handle-gp/',
                             headers={"Content-type": "application/json"},
                             data=data).json()


def handle(msg):
    global start_msg, users
    content_type, chat_type, chat_id = telepot.glance(msg)
    if chat_type == u'private' and content_type == 'text':
        handle_pv(msg)

    elif chat_type in [u'group', u'supergroup']:
        if msg['from']['is_bot'] or 'left_chat_member' in msg or 'new_chat_member' in msg or 'new_chat_members' in msg:
            bot.deleteMessage((chat_id, msg['message_id']))
        if 'new_chat_member' in msg:
            if msg['new_chat_member']['is_bot']:
                try:
                    bot.kickChatMember(chat_id, msg['new_chat_member']['id'])
                    bot.kickChatMember(chat_id, msg['from']['id'])
                except:  # admin did it !
                    pass  # so it's OK !
        handle_gp(msg)


if PROXY:
    telepot.api.set_proxy(PROXY)

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
if __name__ == "__main__":
    application.run(host='localhost')

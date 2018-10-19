import requests
import telepot
from telepot.loop import MessageLoop
import time
import datetime
import json
from pprint import pprint
from config import TOKEN, BOT_API_HOST_URL, HOST_URL
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import os
from flask import Flask
application = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
class User :
    def __init__(self) :
        self.sw = ''
    def set_fn(self) :
        self.sw = 'fn'
    def set_ln(self) :
        self.sw = 'ln'
    def set_b(self) :
        self.sw = 'b'
    def clr(self) :
        self.sw = ''
    def set_what(self) :
        return self.sw

def logadd(text):

    f = open(os.path.join(BASE_DIR, "bot.log"), "a")
    f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + text + '\n')
    f.close()

@application.route('/<int:user_id>/confirmed/')
def hello_world(user_id):
    try:
        bot.sendMessage(user_id, "تلگرام شما با موفقیت متصل شد")
    except Exception as e:
        logadd(str(e))
    return ''

start_msg = '''
خوش آمدید 🙂✋️
برای اتصال بات به پروفایلتان در سایت، دکمه زیر را فشار دهید. 👇
'''

def creatToken(user_id) :
    data = json.dumps({
    'telegram_user_id': user_id
    })
    response = requests.post(url=BOT_API_HOST_URL + '/api/bot/create-token/',
                             headers={"Content-type": "application/json"},
                             data = data)
    return str(response.json()['verify_token'])

def findProfile(chat_id, user_id) :
    logadd(str(user_id))
    response = requests.get(BOT_API_HOST_URL+'/api/bot/%d/get-profile'%user_id)
    if response.status_code == 200 :
        link = response.json()['link']
        bot.sendMessage(chat_id, link)
    elif response.status_code == 404 :
        bot.sendMessage(chat_id, 'پروفایل مورد نظر پیدا نشد')
    else :
        logadd('response.status_code == ' + str(response.status_code))

users = {}
def handle(msg) :
    global start_msg, users
    content_type, chat_type, chat_id = telepot.glance(msg)
    #pprint(msg)
    if chat_type == u'private' :
        if 'forward_from' in msg :
            findProfile(chat_id, msg['forward_from']['id'])
        elif content_type == 'text' :
            if msg['text'] in ['/start', '/start start'] :
                try:
                    token = creatToken(msg['from']['id'])
                    url = HOST_URL + '/verify-token?token=' + token
                    bot.sendMessage(chat_id, start_msg, 'Markdown', reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ اتصال به سایت', url=url)]]))
                except Exception as e:
                    logadd(str(e))
                    bot.sendMessage(chat_id, 'خطایی پیش آمده. لطفا دقایقی دیگر مجددا سعی کنید')
            elif msg['text'] == '/suchawow' :
                if msg['from']['id'] not in users :
                    this_user = User()
                    users.update({msg['from']['id'] : this_user})
                bot.sendMessage(chat_id, 'such a wow !!', reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='set First Name'), KeyboardButton(text='set Last Name')],
                                                                                                       [KeyboardButton(text='set Bio')]]))
            elif msg['text'] == 'set First Name' :
                users[msg['from']['id']].set_fn()
                bot.sendMessage(chat_id, 'Enter your first name :')
            elif msg['text'] == 'set Last Name' :
                users[msg['from']['id']].set_ln()
                bot.sendMessage(chat_id, 'Enter your last name :')
            elif msg['text'] == 'set Bio' :
                users[msg['from']['id']].set_b()
                bot.sendMessage(chat_id, 'Add a few lines about yourself :')
            try :
                if users[msg['from']['id']].set_what() == 'fn' :
                    logadd('%d -> fn : %s'%(msg['from']['id'], msg['text']))
                    users[msg['from']['id']].clr()
                elif users[msg['from']['id']].set_what() == 'ln' :
                    logadd('%d -> ln : %s'%(msg['from']['id'], msg['text']))
                    users[msg['from']['id']].clr()
                elif users[msg['from']['id']].set_what() == 'b' :
                    logadd('%d -> bio : %s'%(msg['from']['id'], msg['text']))
                    users[msg['from']['id']].clr()
            except KeyError :
                this_user = User()
                users.update({msg['from']['id'] : this_user})

    elif chat_type in [u'group', u'supergroup'] :
        if 'left_chat_member' in msg or 'new_chat_member' in msg or 'new_chat_members' in msg :
            bot.deleteMessage((chat_id, msg['message_id']))
        if 'new_chat_member' in msg :
            if msg['new_chat_member']['is_bot'] :
                try :
                    bot.kickChatMember(chat_id, msg['from']['id'])
                except : # admin did it !
                    return # so it's OK !
                bot.kickChatMember(chat_id, msg['new_chat_member']['id'])

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

if __name__ == "__main__":
    application.run(host='localhost')


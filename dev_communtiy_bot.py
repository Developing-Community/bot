import requests
import telepot
from telepot.loop import MessageLoop
import time
import datetime
import json
from pprint import pprint
from config import TOKEN, BOT_API_HOST_URL, HOST_URL
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
start_msg = '''
خوش آمدید 🙂✋️
برای اتصال بات به پروفایلتان در سایت، دکمه زیر را فشار دهید. 👇
'''

def logadd(text):
    f = open("bot.log", "a")
    f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + text + '\n')
    f.close()

def creatToken(user_id) :
    data = json.dumps({
    'telegram_user_id': user_id
    })
    response = requests.post(url=BOT_API_HOST_URL + '/api/bot/create-token/',
                             headers={"Content-type": "application/json"},
                             data = data)
    return str(response.json()['verify_token'])

def findProfile(chat_id, user_id) :
    response = requests.get(BOT_API_HOST_URL+'/apt/bot/%d/get-profile'%user_id)
    if response.status_code == 200 :
        link = response.json()['link']
        bot.sendMessage(chat_id, link)
    elif response.status_code == 404 :
        bot.sendMessage(chat_id, 'چنین پروفایلی وجود ندارد!')
    else :
        logadd('response.status_code == ' + str(response.status_code))

def handle(msg) :
    global start_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    #pprint(msg)
    if chat_type == u'private' :
        if 'forward_from' in msg :
            findProfile(chat_id, msg['forward_from']['id'])
        elif content_type == 'text' :
            if msg['text'] == '/start' :
                try:
                    token = creatToken(msg['from']['id'])
                    url = HOST_URL + '/verify-token?token=' + token
                    bot.sendMessage(chat_id, start_msg, 'Markdown', reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='✅ اتصال به سایت', url=url)]]))
                except Exception as e:
                    logadd(str(e))
                    bot.sendMessage(chat_id, 'خطایی پیش آمده. لطفا دقایقی دیگر مجددا سعی کنید')
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

print('Ready...')
while 1 :
    time.sleep(10)


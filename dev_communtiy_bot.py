import requests
import telepot
from telepot.loop import MessageLoop
import time
import datetime
import json
from pprint import pprint
from config import TOKEN
start_msg = '''
خوش آمدید 🙂✋️

برای اتصال بات به پروفایلتان در سایت از  /login استفاده کنید.
'''

def logadd(text):
    f = open("bot.log", "a")
    f.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ") + text + '\n')
    f.close()

def handle(msg) :
    global start_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    #pprint(msg)
    if chat_type == u'private' :
        if 'forward_from' in msg :
            logadd(str(msg['forward_from']['id']))
        elif content_type == 'text' :

            if msg['text'] == '/start':
                bot.sendMessage(chat_id, start_msg, 'Markdown')
            elif msg['text'] == '/login':
                try:
                    data = json.dumps({
                    'telegram_user_id': msg['from']['id']
                    })
                    response = requests.post('http://localhost/api/bot/create-token/',
                                             headers={"Content-type": "application/json"},
                                             data = data)
                    bot.sendMessage(chat_id, 'https://dev-community.ir/verify-bot?token=' + str(response.json()['verify_token']))
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

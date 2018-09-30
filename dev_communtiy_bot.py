import requests
import telepot
from telepot.loop import MessageLoop
import time
from pprint import pprint
from config import TOKEN
start_msg = '''
خوش آمدید 🙂✋️

برای اتصال بات به پروفایلتان در سایت از  /login استفاده کنید.
'''

def handle(msg) :
    global start_msg
    content_type, chat_type, chat_id = telepot.glance(msg)
    #pprint(msg)
    if chat_type == u'private' :
        if content_type == 'text' :
            if msg['text'] == '/start':
                bot.sendMessage(chat_id, start_msg, 'Markdown')
            elif msg['text'] == '/login':
                user_id = msg['from']['id']
                verify_token = requests.post('localhost/api/bot/get_token', user_id)
                bot.sendMessage(chat_id, 'https://dev-community.ir/verify-bot?token=' + verify_token)
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

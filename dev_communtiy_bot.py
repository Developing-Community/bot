import telepot
from telepot.loop import MessageLoop
import time
from pprint import pprint
from config import TOKEN
def handle(msg) :
    content_type, chat_type, chat_id = telepot.glance(msg)
    #pprint(msg)
    if 'left_chat_member' in msg or 'new_chat_member' in msg or 'new_chat_members' in msg :
        bot.deleteMessage((chat_id, msg['message_id']))
    if 'new_chat_member' in msg :
        if msg['new_chat_member']['is_bot'] :
            try :
                bot.kickChatMember(chat_id, msg['from']['id'])
            except : # admin did it !
                return # so it's OK !
            bot.kickChatMember(chat_id, msg['new_chat_member']['id'])
    return

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

print('Ready...')
while 1 :
    time.sleep(10)

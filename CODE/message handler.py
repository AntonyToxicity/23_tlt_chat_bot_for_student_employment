import random
import vk_api
import os
from vk_api.longpoll import VkLongPoll, VkEventType

a = os.path.basename(__file__)
dir = os.path.abspath(__file__).replace(a, '')

def get_random_id():
   return random.getrandbits(31) * random.choice([-1, 1])


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, "random_id":get_random_id()})

token = "311b05cafb4ba7002cd5ec05a2f8b6052e79a46e4add3b48a07f6ad8e728b991077ae63019d36a19c0b7b"
vk = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk)
print("bot is started...")
for event in longpoll.listen():
	if event.type == VkEventType.MESSAGE_NEW:
		if event.to_me:
			request = event.text #приведение к общему формату соощений (нижний регистр, крайние пробелы, ...) Алкусандр Приб
			os.system("python3 '"+dir+"/databasehandler.py' " + str(event.user_id)+" '"+request + "'&")
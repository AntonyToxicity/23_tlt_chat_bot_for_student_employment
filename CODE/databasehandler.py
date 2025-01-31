import pymysql.cursors
import configparser as CfPs
import sys
import os
import random
import vk_api
import keyboardlib as kbl
from vk_api.longpoll import VkLongPoll, VkEventType

#......................................................
####### SEND FUNCTIONS ################################
#......................................................
def get_random_id():
   return random.getrandbits(31) * random.choice([-1, 1])

mykeyboard = kbl.create_keyboard()
def write_msg_to_user(user_id, text):
	token = "311b05cafb4ba7002cd5ec05a2f8b6052e79a46e4add3b48a07f6ad8e728b991077ae63019d36a19c0b7b"

	vk = vk_api.VkApi(token=token)
	vk.method('messages.send', {'user_id': user_id,
                                'random_id': get_random_id(),
                                 'message': text,
                                 'attachment': None,
                                 'keyboard': mykeyboard})

#......................................................
####### Get Settings ##################################
#......................................................
#a1 = os.path.basename(__file__)
#dir_h = os.path.abspath(__file__).replace(a1, '')

config = CfPs.ConfigParser()
config.read("settings.ini") #config.read("'"+dir_h+"settings.ini'")
#print("'"+dir_h+"settings.ini'")
#print(config.items())
user_host = config["DB settings"]["user_host"]
user_name = config["DB settings"]["user_name"]
user_password = config["DB settings"]["user_password"]
user_db = config["DB settings"]["user_db"]
user_db_charset = config["DB settings"]["user_db_charset"]


#......................................................
####### AUTARISATION ##################################
#......................................................

#print ("Conecting...")
try:
	connection = pymysql.connect(
		host=user_host,
		user=user_name,
		password=user_password,
		db=user_db,
		charset=user_db_charset,
		cursorclass=pymysql.cursors.DictCursor
		)
	#print ("conected!")
except Exception as ex:
	#print("don't conected...")
	print(ex)

def disassemble(rows):
	result = ""
	for row in rows:
		for key, val in row.items():
			if (val!=None):
				result += str(key) + " " + str(val)
		result += "\n"
	return result
		

#......................................................
####### WORK ##########################################
#......................................................

id = sys.argv[1]
text = sys.argv[2]

msg = "каково-либо ответа, на данную комманду получено небыло, рекомендуем свериться с списком комманд"

try:
	if text=="?":
		msg = "доступные комманды:\n	"
		for i in config["buttens"]:
			msg = msg + str(i) + "\n	"
		write_msg_to_user(id, str(msg))

	with connection.cursor() as cursor:
		cursor.callproc("GetByCompany", (id, text))
		tbl = cursor.fetchall()

		if not("null" in tbl[0]):
			msg = disassemble(tbl)
		else:
			func = "select "+config["signals"]["AddInfo"]+"(%s, %s) as second"
			proc = config["buttens"]["вакансии"]
			cursor.execute(func, (id, text))
			connection.commit()
			all_ok = cursor.fetchall()[0]["second"]
			if all_ok == config["signals"]["OkSugnall"]:
				if text in config["buttens"]:
					proc = config["buttens"][text]
					cursor.callproc(proc, (id, text))
					msg = disassemble(cursor.fetchall())
			else:
				msg = all_ok
		connection.commit()
		cursor.close()
except Exception as ex:
	msg = "достижение 'тестировщик' - вам удалось найти ошибку, просим вас подробно ее описать тех. поддержке"
	print("пользователь "+str(id)+" получил ошибку - ")
	print(ex)
	#отредактировать
if ((str(msg)=="Приветствую, укажите ваш институт или специальность") or (str(msg)=="Укажите ваш институт или специальность")):
	mykeyboard = kbl.create_keyboard_inst()
else:
	mykeyboard = kbl.create_keyboard()
write_msg_to_user(id, str(msg))
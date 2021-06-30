import time, threading, telebot, datetime
from user import User

with open("pass.txt",'r') as file:
	API_TOKEN = file.read()

bot = telebot.TeleBot(API_TOKEN)

def email_valid(email):
	'Verifica se email eh valido. Se nao tiver espacos, "@usp.br" e algum dos cantos obrigatorios estiver vazio, retorna False. Caso o contrario, retorna True.'
	email = email.strip()
	if not('@usp.br' in email):
		return False

	dados = email.split('@usp.br')
	if not(dados[0]) or dados[1]:
		return False

	return True

def email_check(email):
	# A fazer
	'Verifica Database de Emails. Se tiver Email ja registrado, retorna False, Caso Contrario, true'
	return True

@bot.message_handler(commands=['start','register','registrar'])
def register(message):
	'Registra usuario na Database. So funciona se o mesmo estiver em um chat privado e nao for registrado.'
	if message.chat.type != 'private':
		bot.reply_to(message,f"{message.from_user.first_name}, Utilize de um chat privado para cadastrar-se!")
		return False
	
@bot.message_handler(commands=['unregister','clear','delregistro'])
def del_register(message):
	"Deleta o registro feito pelo usuario na database.So funciona se o mesmo for registrado."
	pass

@bot.message_handler(commands=['alertas'])
def get_alertas(message):
	"Delvolve uma lista com todos alertas criados pelo user."
	pass

@bot.message_handler(commands=['materias'])
def get_materias(message):
	""" Returns a list with all courses defined by the user.
	Delvolve uma lista com todas materias definidas pelo user."""
	pass

@bot.message_handler(commands=['del_alerta'])
def del_alerta(message):
	"Deleta um alerta criado pelo usuario na database."
	pass

@bot.message_handler(commands=['del_materia'])
def del_materia(message):
	"Remove uma materia programada pelo usuario na database."
	pass


@bot.message_handler(commands=['reset'])
def reset(message):
	"Reinicia todas materias e alertas do usuario, removendo suas atribuicoes ao usuario. Nao remove usuario."
	pass

@bot.message_handler(commands=['help','ajuda','?'])
def bot_help(message):
	"Delvolve uma lista com todos alertas criados pelo user."
	pass

print(help(get_materias))

while True:
	try:
		bot.polling()
	except Exception:
		time.sleep(3)


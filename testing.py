import time, threading, telebot, datetime
from user import User

with open("pass.txt",'r') as file:
	API_TOKEN = file.read()

bot = telebot.TeleBot(API_TOKEN)

def email_valid(email):
	'''
	Verifies if the given email is valid. If it doesn't have spaces, '@usp.br' and any of the required fields is missing, returns False. Otherwise, returns True.
	Verifica se email eh valido. Se nao tiver espacos, "@usp.br" e algum dos cantos obrigatorios estiver vazio, retorna False. Caso o contrario, retorna True.'''
	email = email.strip()
	if not('@usp.br' in email):
		return False

	dados = email.split('@usp.br')
	if not(dados[0]) or dados[1]:
		return False

	return True

def email_check(email):
	# A fazer
	'''
	Verifies the email Database. If the email is already registered, returns False. Otherwise, returns True.
	Verifica Database de Emails. Se tiver Email ja registrado, retorna False, Caso Contrario, true'''
	return True

@bot.message_handler(commands=['register','registrar'])
def register(message):
	'''
	Register the user in the Database. Only works if the user is not registered.
	Registra usuario na Database. So funciona se o mesmo nao for registrado.'''
	if message.chat.type != 'private':
		bot.reply_to(message,f"{message.from_user.first_name}, Utilize de um chat privado para cadastrar-se!")
		return False
	
@bot.message_handler(commands=['unregister','clear','delregistro'])
def del_register(message):
	'''
	Deletes the User from the Database. Only works if the user is registered.
	Deleta o registro feito pelo usuario na database.So funciona se o mesmo for registrado.'''
	pass

@bot.message_handler(commands=['alertas'])
def get_alertas(message):
	'''
	Returns a list with all the alerts the user curently have.
	Delvolve uma lista com todos alertas definidos ao user.'''
	pass

@bot.message_handler(commands=['materias'])
def get_materias(message):
	""" 
	Returns a list with all courses defined by the user.
	Delvolve uma lista com todas materias definidas pelo user."""
	pass

@bot.message_handler(commands=['del_alerta'])
def del_alerta(message):
	'''
	Delets an alert created by the user.
	Deleta um alerta criado pelo usuario na database.'''
	pass

@bot.message_handler(commands=['del_materia'])
def del_materia(message):
	'''
	Removes a course defined for the user from the database
	Remove uma materia programada pelo usuario na database.'''
	pass


@bot.message_handler(commands=['reset'])
def reset(message):
	'''
	Restarts all courses and alerts related to the user. Doesn't remove the user. 
	Reinicia todas materias e alertas do usuario, removendo suas atribuicoes ao usuario. Nao remove usuario.'''
	pass

@bot.message_handler(commands=['help','ajuda','?'])
def bot_help(message):
	'''
	Returns information and comands of the bot.
	Retorna informacao e comandos do bot.
	'''
	pass

def materias_number_to_lista(num):
    #Transforma um numero em uma lista das potencias de 2 que o compoem
    lista = [];
    i = 1;
    while num/i >= 1:
        i=i*2;
        resto = num%i;
        if resto != 0:
            lista.append(resto)
        num = num-resto
    return lista




print(help(materias_number_to_lista))

while True:
	try:
		bot.polling()
	except Exception:
		time.sleep(3)


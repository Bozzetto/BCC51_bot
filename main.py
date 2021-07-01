#Importacao de modulos
import telebot
import time
import datetime
import threading
import mariadb
import sys

import user



def inicializar():
    #Resolve todas as pendencias iniciais do programa
    us = get_user().rstrip()
    passwd = get_passwd().rstrip()
    try:
        conn = mariadb.connect(
            user = us,
            password = passwd,
            host = "localhost",
            port = 3306,
            database="mydb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to Mariadb:{e}")
        sys.exit(-1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM Users WHERE admin= true")
    except mariadb.ProgrammingError:
        print("User table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE IF NOT EXISTS Users( userID int UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(30) NOT NULL, email varchar(50) NOT NULL, telegram varchar(15) NOT NULL, materias int, admin int NOT NULL, rc int NOT NULL)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Users:{e}")
        sys.exit(-1)
    try:
        cur.execute("SELECT code FROM Courses")
    except mariadb.ProgrammingError:
        print("Courses table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE IF NOT EXISTS Courses( courseID int NOT NULL UNIQUE PRIMARY KEY, name varchar(7) NOT NULL, professor varchar(50), code int NOT NULL)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Courses:{e}")
        sys.exit(1)
    try:
        cur.execute("SELECT date FROM Warnings")
    except mariadb.ProgrammingError:
        print("Warnings table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE IF NOT EXISTS Warnings(warningID int UNIQUE AUTO_INCREMENT PRIMARY KEY,name varchar(40) NOT NULL, course int, type int NOT NULL,date datetime, repeatable tinyint, CONSTRAINT fk_warning_course FOREIGN KEY (course) REFERENCES Courses(courseID) ON DELETE CASCADE)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Warnings:{e}")
        sys.exit(1)

    cur.close()

def get_token():
    with open("token.txt","r") as file:
        return file.read()

def get_user():
    with open("user.txt","r") as file:
        return file.read()

def get_passwd():
    with open("passwd.txt","r") as file:
        return file.read()


def get_courses():
    return ['Palestrinha','Calculo I','Fumac','Vetores','Algebool','IntroComp']

def get_poll_results(poll_results,user,atribute):
    list = []
    for item in poll_results:
        list.append(item.voter_count)
    if atribute == "1":
        user.courses = list
    elif atribute == "2":
        user.warnings = list
    return user

def get_connect():
    us = get_user().rstrip()
    passwd = get_passwd().rstrip()
    try:
        conn = mariadb.connect(
            user = us,
            password = passwd,
            host = "localhost",
            port = 3306,
            database="mydb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to Mariadb:{e}")
        sys.exit(-1)

    return conn


def materias_number_to_lista(num):
    '''
    Transforms a number into a list with all the powers of two needed to create that number.
    Transforma um numero em uma lista das potencias de 2 que o compoem'''
    lista = [];
    i = 1;
    while num/i >= 1:
        i=i*2;
        resto = num%i;
        if resto != 0:
            lista.append(resto)
        num = num-resto
    return lista

def materias_lista_to_number(lista):
    '''
    Transforms a list with powers of 2 in a number adding its elements.
    Transforma uma lista de potencias de 2 em um numero somando seus elementos.'''
    sum = 0
    for i in lista:
        sum = sum + i
    return sum


def check_type_chat(message,bot):
    #Recebe uma mensagem e detecta se o grupo e privado ou publico
    if message.chat.type != 'private':
        bot.leave_chat(message.chat.id)
        return True
    else:
        return False

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

def gen_markup_confirm():
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row_width = 1
    markup.add(telebot.types.KeyboardButton("Sim"), telebot.types.KeyboardButton("Não"))

    return markup

def main():
    inicializar()
    token = get_token()
    bot = telebot.TeleBot(token.rstrip())

    def process_email_step(message,user,bot):
        if email_valid(message.text):
            user.email = message.text
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            itembtn1 = telebot.types.KeyboardButton('Sim')
            itembtn2 = telebot.types.KeyboardButton('Não')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id,"Podemos utilizar da suas informacoes do Telegram ",reply_markup = markup)
            bot.register_next_step_handler(message,process_information_step,user,bot)
        else:
            bot.send_message(message.chat.id,"E-mail invalido, por favor digite novamente")
            bot.register_next_step_handler(message,process_email_step,user,bot)

    def process_information_step(message,user,bot):
        if message.text == 'Sim':
            markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
            itembtn1 = telebot.types.KeyboardButton('Sim')
            itembtn2 = telebot.types.KeyboardButton('Não')
            markup.add(itembtn1, itembtn2)
            if type(message.from_user.first_name) == type("a"):
                user.name = message.from_user.first_name;
            if type(message.from_user.last_name) == type("a"):
                user.name = user.name + ' ' + message.from_user.last_name
            user.id = message.chat.id
            bot.send_message(message.chat.id,"Voce e um RC?",reply_markup=markup)
            bot.register_next_step_handler(message,process_final_step,user,bot)
        else:
            bot.send_message(message.chat.id,"Nao foi possivel realizar o cadastro")
            exit()

    def process_final_step(message,user,bot):
        if message.text == 'Sim':
            user.rc = 1
        elif message.text =='Não':
            user.rc = 0
        else:
            bot.send_message(message.chat.id,"Não foi possivel realizar o cadastro")
            exit()
        courses = get_courses
        poll=bot.send_poll(message.chat.id,"Quais materias voce esta fazendo?",get_courses(),allows_multiple_answers = True)
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        user = get_poll_results(poll_results.options,user,"1")

        poll=bot.send_poll(message.chat.id,"Quais tipos de avisos voce quer?",['1-Provas(1 semana antes e no dia)','2-EPs','3-Trabalhos','4-Aulas'],allows_multiple_answers = True)
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        user = get_poll_results(poll_results.options,user,"2")
        print(user)


    @bot.message_handler(commands=['start'])
    def start(message):
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Bem-vindo ao bot do BCC 51")
            bot.send_message(message.chat.id,"Para mais informacoes sobre o bot visite: https://github.com/Bozzetto/BCC51_bot", disable_web_page_preview = True)
            bot.send_message(message.chat.id,"Para acessar os comandos do bot, digite '/help'")


    @bot.message_handler(commands=['register'])
    def register(message):
        #Novo objeto user para o novo usuario
        newuser = user.User()
        #Checa se esta em um grupo
        if check_type_chat(message,bot):
            return -1
        bot.send_message(message.chat.id,"Vamos comecar o seu processo de registro")
        bot.send_message(message.chat.id,"Qual o seu e-mail (@usp.br)?")
        bot.register_next_step_handler(message,process_email_step, newuser,bot)

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

        if check_type_chat(message,bot):
            exit()

        msg = bot.send_message(message.chat.id,'''
            Tem certeza que deseja continuar? Todos os dados de matérias e alertas serão apagados''',reply_markup= gen_markup_confirm())

        bot.register_next_step_handler(msg, reset_s1)

    def reset_s1(message):
        if message.text == 'Não':
            bot.send_message(message.chat.id,'''Operação cancelada!''')
        elif message.text == 'Sim':
            bot.send_message(message.chat.id,'''Deletando todas materias e alertas do usuario ...''')
            cur = get_connect().cursor()
            cur.close()
        else:
            bot.send_message(message.chat.id,'''Operação abortada. Por favor, utilize os Botões para responder a mensagem. ''')


    @bot.message_handler(commands=['help','ajuda','?'])
    def bot_help(message):
        '''
        Returns information and comands of the bot.
        Retorna informacao e comandos do bot.
        '''
        pass

    bot.polling()




if __name__ == '__main__':
    main()

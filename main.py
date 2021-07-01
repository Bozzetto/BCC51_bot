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

    @bot.message_handler(commands=['start'])
    def start(message):
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Bem-vindo ao bot do BCC 51")
            bot.send_message(message.chat.id,"Para mais informacoes sobre o bot visite: https://github.com/Bozzetto/BCC51_bot", disable_web_page_preview = True)
            bot.send_message(message.chat.id,"Para acessar os comandos do bot, digite '/help'")


    @bot.message_handler(commands=['register'])
    def register(message):
        Finished = 0
        #Novo objeto user para o novo usuario
        newuser = user.User()
        #Checa se esta em um grupo
        if check_type_chat(message,bot):
            exit()

        #Teclados customizados para responder as entradas
        markup1 = telebot.types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = telebot.types.KeyboardButton('/S Sim')
        itembtn2 = telebot.types.KeyboardButton('/N Nao')
        markup1.add(itembtn1, itembtn2)
        markup2 = telebot.types.ReplyKeyboardMarkup(row_width=1)
        itembtn1 = telebot.types.KeyboardButton('/Sim , sou RC')
        itembtn2 = telebot.types.KeyboardButton('/Nao , nao sou RC')
        markup2.add(itembtn1, itembtn2)


        @bot.message_handler(commands=['cancel'])
        def fechar(message):
            newuser.id = 0
            newuser.email = ""
            newuser.name = ""
            newuser.rc = 0
            #Operacao de registro
        @bot.message_handler(func=lambda message: message.text.endswith('@usp.br'))
        def email(message):
            @bot.message_handler(commands=['S'])
            def S (message):
                newuser.id = message.chat.id
                newuser.name = message.from_user.first_name + message.from_user.last_name
                bot.send_message(message.chat.id,"Você é RC?",reply_markup=markup2)

                @bot.message_handler(commands=['Sim'])
                def S2(message):
                    newuser.rc = 1
                    bot.send_message(message.chat.id,"Registro feito com sucesso")
                    print(newuser)
                    return 1
                @bot.message_handler(commands= ['Não'])
                def N2(message):
                    newuser.rc =0
                    print(newuser)
                    bot.send_message(message.chat.id,"Registro feito com sucesso")

            @bot.message_handler(commands=['N'])
            def N (message):
                    bot.send_message(message.chat.id,"Não foi possível realizar o cadastro")
            newuser.email = message.text
            bot.send_message(message.chat.id,"Podemos usar as suas informações do Telegram para realizar o registro?",reply_markup=markup1)
            return 1
        if Finished == 1:
            commit()
        else:
            bot.send_message(message.chat.id,"Vamos começar o seu processo de registro")
            bot.send_message(message.chat.id,"Qual o seu e-mail (@usp.br)?")


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

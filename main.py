#Importacao de modulos
import telebot
import datetime
import threading
import mariadb
import sys

def inicializar():
    '''
    Resolve all initial pendencies for program startup.
    Resolve todas pendencias iniciais para inicio de programa.
    '''
    try:
        conn = mariadb.connect(
            user = "anon",
            password = "teste",
            host = "localhost",
            port = 3306,
            database="mydb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to Mariadb:{e}")
        sys.exit(1)

    cur = conn.cursor()
    try:
        cur.execute("SELECT name FROM Users WHERE admin= true")
    except mariadb.ProgrammingError:
        print("User table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE IF NOT EXISTS Users( userID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(30) NOT NULL, email varchar(50) NOT NULL, telegram varchar(20), materias int, admin int NOT NULL)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Users:{e}")
        sys.exit(1)
    try:
        cur.execute("SELECT code FROM Courses")
    except mariadb.ProgrammingError:
        print("Courses table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE IF NOT EXISTS Courses( courseID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(7) NOT NULL, professor varchar(20), code int NOT NULL)")
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
                cur.execute("CREATE TABLE IF NOT EXISTS Warnings(warningID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY,name varchar(40) NOT NULL, course int, type int NOT NULL,date datetime, repeatable tinyint, CONSTRAINT fk_warning_course FOREIGN KEY (course) REFERENCES Courses(courseID) ON DELETE CASCADE)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Warnings:{e}")
        sys.exit(1)

    cur.close()

def getToken():
    '''
    Get token for bot use.
    Consegue a token para uso do bot.
    '''
    file = open("token.txt","r")
    return file.read()

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
    '''
    Recieves a message and detects if the chat is private or public. If public, returns True. Otherwise, false.
    Recebe uma mensagem e detecta se o grupo e privado ou publico. Se o chat for publico, retorna True. Caso o contrario, retorna False'''
    if message.chat.type == 'group' or message.chat.type == 'supergroup' or message.chat.type == 'channel':
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

def main():
    inicializar()
    token = getToken()
    bot = telebot.TeleBot(token.rstrip())

    @bot.message_handler(commands=['start'])
    def start(message):
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Bem-vindo ao bot do BCC 51")
            bot.send_message(message.chat.id,"Para mais informacoes sobre o bot visite:https://github.com/Bozzetto/BCC51_bot", disable_web_page_preview = True)
            bot.send_message(message.chat.id,"Para acessar os comandos do bot, digite '/help'")

    @bot.message_handler(commands=['register','registrar'])
    def register(message):
        # a fazer
        '''
        Register the user in the Database. Only works if the user is not registered.
        Registra usuario na Database. So funciona se o mesmo nao for registrado.'''
        if check_type_chat(message,bot):
            bot.reply_to(message,f"{message.from_user.first_name}, Utilize de um chat privado para cadastrar-se!")
            return False
        else:
            pass

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

    bot.polling()





if __name__ == '__main__':
    main()

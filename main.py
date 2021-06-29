#Importacao de modulos
import telebot
import datetime
import threading
import mariadb
import sys

def inicializar():
    #Resolve todas as pendencias iniciais do programa
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
    file = open("token.txt","r")
    return file.read()

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



def materias_lista_to_number(lista):
    #Transforma uma lista de potencias de 2 em um numero
    sum = 0
    for i in lista:
        sum = sum + i
    return sum

def check_type_chat(message,bot):
    #Recebe uma mensagem e detecta se o grupo e privado ou publico
    if message.chat.type == 'group' or message.chat.type == 'supergroup' or message.chat.type == 'channel':
        bot.leave_chat(message.chat.id)
        return True
    else:
        return False

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

    bot.polling()





if __name__ == '__main__':
    main()

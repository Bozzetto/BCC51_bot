#Importacao de modulos
import telebot
import datetime
import threading
import mariadb
import sys

def inicializar():
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
        cur.execute("SELECT name from users where admin= true")
    except mariadb.ProgrammingError:
        print("user table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE users( userID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(30) NOT NULL, email varchar(50) NOT NULL, telegram varchar(20), materias int, admin int NOT NULL)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding users:{e}")
        sys.exit(1)
    try:
        cur.execute("SELECT code FROM courses")
    except mariadb.ProgrammingError:
        print("courses table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE courses( courseID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(7) NOT NULL, professor varchar(20), code int NOT NULL)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding users:{e}")
        sys.exit(1)
    try:
        cur.execute("SELECT hour FROM warnings")
    except mariadb.ProgrammingError:
        print("warnings table not found")
        answer = ""
        while answer != "Y" and answer != "N" and answer != "NO" and answer != "YES":
            answer = input("Create a new one?(Y/N)").upper()
            if answer == "Y" or answer == "YES":
                cur.execute("CREATE TABLE warnings(warningID int NOT NULL UNIQUE AUTO_INCREMENT PRIMARY KEY,name varchar(40) NOT NULL, course int, type int NOT NULL, CONSTRAINT fk_warning_course FOREIGN KEY (course) REFERENCES courses(courseID) ON DELETE CASCADE)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding users:{e}")
        sys.exit(1)















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

def main():

    inicializar()





if __name__ == '__main__':
    main()
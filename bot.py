#Importacao de modulos
import telebot
import datetime
import threading
import mariadb
import sys

#Transforma um numero em uma lista das potencias de 2 que o compoem
def materias_number_to_lista(num):
    lista = [];
    i = 1;
    while num/i >= 1:
        i=i*2;
        resto = num%i;
        if resto != 0:
            lista.append(resto)
        num = num-resto
    return lista

#Transforma uma lista de potencias de 2 em um numero
def materias_lista_to_number(lista):
    sum = 0
    for i in lista:
        sum = sum + i
    return sum

def main():
    try:
        conn = mariadb.connect(
            user = "anon",
            password = "teste",
            host = "localhost",
            port = 3306,
            database = "mydb"
        )
    except mariadb.Error as e:
        print(f"Error connecting to Mariadb:{e}")
        sys.exit(1)

    cur = conn.cursor()
    





if __name__ == '__main__':
    main()

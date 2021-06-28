import telebot
import datetime
import threading
import mysql.connector

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

def materias_lista_to_number(lista):
    sum = 0
    for i in lista:
        sum = sum + i
    return sum

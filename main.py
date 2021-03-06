#Importacao de modulos
import telebot
import time
import datetime
import mariadb
import sys
import math
import threading

import classes

def inicializar():
    #Resolve todas as pendencias iniciais do programa
    us = get_user(1).rstrip()
    passwd = get_passwd(1).rstrip()
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
                cur.execute("CREATE TABLE IF NOT EXISTS Users( userID int UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(30) NOT NULL, email varchar(50) NOT NULL, telegram varchar(15) NOT NULL, materias int,types int, admin int NOT NULL, rc int NOT NULL)")
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
                cur.execute("CREATE TABLE IF NOT EXISTS Courses( courseID int UNIQUE AUTO_INCREMENT, name varchar(7) NOT NULL ,name_materias varchar(40) NOT NULL PRIMARY KEY, professor varchar(50), code int NOT NULL)")
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
                cur.execute("CREATE TABLE IF NOT EXISTS Warnings(warningID int UNIQUE AUTO_INCREMENT PRIMARY KEY,name varchar(40) NOT NULL, course int, type int NOT NULL,creator varchar(15),date datetime, repeatable tinyint)")
            elif answer == "NO" or answer == "N":
                print("Program couldn't initialize. Not all tables were found");
            else:
                print("Not a valid answer")
    except mariadb.Error as e:
        print(f"Error finding Warnings:{e}")
        sys.exit(1)
    conn.close()

def get_token():
    with open("token.txt","r") as file:
        return file.read()

def get_user(number):
    with open("user.txt","r") as file:
        users = file.read().split("\n")
    if number == 1:
        return users[0]
    elif number == 2:
        return users[1]
    elif number == 3:
        return users[2]

def get_passwd(number):
    with open("passwd.txt","r") as file:
        passwds = file.read().split("\n")
    if number == 1:
        return passwds[0]
    elif number == 2:
        return passwds[1]
    elif number == 3:
        return passwds[2]

def get_courses():
    list = []
    conn = get_connect(3)
    cur = conn.cursor()
    cur.execute("SELECT name_materias FROM Courses")
    for i in cur:
        list.append(i[0])
    conn.close()
    return list

def get_poll_results(poll_results,user,atribute):
    list = []
    for item in poll_results:
        list.append(item.voter_count)
    if atribute == "1":
        user.courses = list
    elif atribute == "2":
        user.warnings = list
    return user

def get_connect(number):
    us = get_user(number).rstrip()
    passwd = get_passwd(number).rstrip()
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

def is_admin(user_id):
    conn = get_connect(3)
    cur = conn.cursor()
    cur.execute(f"SELECT admin FROM Users WHERE telegram= {user_id}")

    for i in cur:
        if i == (0,):
            conn.close()
            return False
        else:
            conn.close()
            return True

def is_rc(user_id):
    conn = get_connect(3)
    cur = conn.cursor()
    cur.execute(f"SELECT rc FROM Users WHERE telegram= {user_id}")

    for i in cur:
        if i == (0,):
            conn.close()
            return False
        else:
            conn.close()
            return True

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
    Transforms a list with 0s or 1s in a number by adding its equivalents in powers of 2.
    Transforma uma lista de 0s e 1s em um numero somando suas potencias de dois equivalentes.'''
    sum = 0
    j=0
    for i in lista:
        sum = sum + (i*(math.pow(2,j)))
        j = j+1
    return int(sum)

def user_check(user):
    '''
    Verifies the users Database. If the user is already registered, returns False. Otherwise, returns True.
    Verifica Database de Usuarios. Se tiver Usuario ja registrado, retorna False, Caso Contrario, true'''
    conn = get_connect(3)
    cur = conn.cursor()
    cur.execute(f"SELECT telegram FROM Users WHERE telegram = {user}")
    for i in cur:
        conn.close()
        return False
    conn.close()
    return True

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
    '''
    Verifies the email Database. If the email is already registered, returns False. Otherwise, returns True.
    Verifica Database de Emails. Se tiver Email ja registrado, retorna False, Caso Contrario, true'''
    conn = get_connect(3)
    cur = conn.cursor()
    cur.execute(f"SELECT email FROM Users WHERE email = '{email}'")
    for i in cur:
        conn.close()
        return False
    conn.close()
    return True

def check_course(course):
    conn = get_connect(2)
    cur = conn.cursor()
    cur.execute("SELECT name FROM Courses")

    for name in cur:
        if name == (course,):
            conn.close()
            return False
    conn.close()
    return True

def get_next_code():
    conn = get_connect(2)
    cur = conn.cursor()
    cur.execute("SELECT code FROM Courses")

    code = 1
    for c in cur:
        code = code*2
    conn.close()
    return code

def gen_markup_confirm():
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard = True)
    markup.row_width = 1
    markup.add(telebot.types.KeyboardButton("Sim"), telebot.types.KeyboardButton("N??o"))

    return markup






def main():
    inicializar()
    token = get_token()
    bot = telebot.TeleBot(token.rstrip())

    def check_warnings():
        while True:
            epoch = time.time()
            curtime = time.localtime(epoch)
            if curtime.tm_min%15 == 0:
                conn = get_connect(3)
                cur1 = conn.cursor()
                conn2 = get_connect(3)
                cur2 = conn2.cursor()
                conn3 = get_connect(2)
                cur3 = conn3.cursor()
                cur2.execute(f"SELECT name,type,course,repeatable FROM Warnings WHERE date = '{curtime.tm_year}-{curtime.tm_mon}-{curtime.tm_mday} {curtime.tm_hour}:{curtime.tm_min}'")
                cur1.execute(f"SELECT name,telegram,materias,types FROM Users")
                for i in cur2:
                    for user in cur1:
                        materias = materias_number_to_lista(user[2])
                        types = materias_number_to_lista(user[3])
                        if i[1] in types:
                            if i[2] in materias:
                                bot.send_message(user[1],i[0])
                    if i[3] == 1:
                        new_epoch = epoch + 604800
                        future_time = time.localtime(new_epoch)
                        cur3.execute(f"INSERT INTO Warnings (name,type,course,date,repeatable) VALUES ('{i[0]}',{i[1]},{i[2]},'{future_time.tm_year}-{future_time.tm_mon}-{future_time.tm_mday} {future_time.tm_hour}:{future_time.tm_min}',1)")
                    cur3.execute(f"DELETE FROM Warnings WHERE name = '{i[0]}' and date = '{curtime.tm_year}-{curtime.tm_mon}-{curtime.tm_mday} {curtime.tm_hour}:{curtime.tm_min}'")
                    conn3.commit()
                    conn3.close()
                conn.close()
                conn2.close()
            time.sleep(60)

    #Funcao que envia os dados iniciais para o usuario
    @bot.message_handler(commands=['start'])
    def start(message):
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Bem-vindo ao bot do BCC 51")
            bot.send_message(message.chat.id,"Para mais informa????es sobre o bot visite: https://github.com/Bozzetto/BCC51_bot", disable_web_page_preview = True)
            bot.send_message(message.chat.id,"Para acessar os comandos do bot, digite '/help'")


    #Sequencia de funcoes que lidam com um pedido de registro
    @bot.message_handler(commands=['register'])
    def register(message):
        #Novo objeto user para o novo usuario
        newuser = classes.User()
        #Checa se esta em um grupo
        if check_type_chat(message,bot):
            return -1
        if not user_check(message.chat.id):
            bot.send_message(message.chat.id,"Voce ja esta registrado")
            return -1
        bot.send_message(message.chat.id,"Vamos come??ar o seu processo de registro")
        bot.send_message(message.chat.id,"Qual o seu e-mail (@usp.br)?")
        bot.register_next_step_handler(message,process_email_step, newuser,bot)

    def process_email_step(message,user,bot):
        if email_valid(message.text)and email_check(message.text):
            user.email = message.text
            markup = gen_markup_confirm()
            bot.send_message(message.chat.id,"Podemos utilizar suas informa????es do Telegram? ",reply_markup = markup)
            bot.register_next_step_handler(message,process_information_step,user,bot)
        elif message.text == "/cancel":
            return -1
        else:
            bot.send_message(message.chat.id,"E-mail inv??lido. Por favor, digite novamente")
            bot.register_next_step_handler(message,process_email_step,user,bot)

    def process_information_step(message,user,bot):
        if message.text == 'Sim':
            markup = gen_markup_confirm()
            if type(message.from_user.first_name) == type("a"):
                user.name = message.from_user.first_name;
            if type(message.from_user.last_name) == type("a"):
                user.name = user.name +" "+ message.from_user.last_name;
            user.id = message.chat.id
            bot.send_message(message.chat.id,"Voc?? ?? um RC?",reply_markup=markup)
            bot.register_next_step_handler(message,process_final_step,user,bot)
        else:
            bot.send_message(message.chat.id,"Nao foi possivel realizar o cadastro")
            return -1

    def process_final_step(message,user,bot):
        if message.text == 'Sim':
            user.rc = 1
        elif message.text =='N??o':
            user.rc = 0
        else:
            bot.send_message(message.chat.id,"N??o foi possivel realizar o cadastro")
            return -1

        courses = get_courses()

        poll=bot.send_poll(message.chat.id,"Quais tipos de avisos voc?? quer?",['1-Provas(1 semana antes e no dia)','2-EPs','3-Trabalhos','4-Aulas'],allows_multiple_answers = True)
        time.sleep(10)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        user = get_poll_results(poll_results.options,user,"2")

        poll=bot.send_poll(message.chat.id,"Quais mat??rias voc?? est?? fazendo?",get_courses(),allows_multiple_answers = True)
        time.sleep(10)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        user = get_poll_results(poll_results.options,user,"1")


        if insert_user_step(message,user):
            bot.send_message(message.chat.id,"Usuario registrado com sucesso")
        else:
            bot.send_message(message.chat.id,"Ocorreu um problema durante seu registro, por favor tente novamente")

    def insert_user_step(message,user):
        conn = get_connect(2)
        cur = conn.cursor()
        sql = f"INSERT INTO Users (name,email,telegram,materias,types,admin,rc) VALUES ('{user.name}','{user.email}',{user.id},{materias_lista_to_number(user.courses)},{materias_lista_to_number(user.warnings)},0,{user.rc});"
        try:
            if user_check(message.chat.id):
                cur.execute(sql)
                cur.execute("COMMIT;")
            else:
                bot.send_message(message.chat.id,"Usuario ja registrado")
                return False
            conn.close()
            return True
        except mariadb.Error as e:
            print(e)
            conn.close()
            return False


    #Funcoes que lidam com o pedido de deletar conta do usuario
    @bot.message_handler(commands=['unregister','clear','delregistro'])
    def del_register(message):
        '''
        Deletes the User from the Database. Only works if the user is registered.
        Deleta o registro feito pelo usuario na database.So funciona se o mesmo for registrado.'''
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Tem certeza disso?",reply_markup = gen_markup_confirm())
            bot.register_next_step_handler(message,del_register_final_step)

    def del_register_final_step(message):
        sql = f"DELETE FROM Users WHERE telegram = {message.chat.id};"
        try:
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(sql)
            cur.execute("COMMIT;")
            conn.close()
            bot.send_message(message.chat.id,"Registro deletado com sucesso")
        except:
            conn.close()
            bot.send_message(message.chat.id,"Nao foi possivel deletar o registro, tente novamente ou contate um admin")


    #Funcoes que resetam as materias e tipos de alertas para o usuario
    @bot.message_handler(commands=['reset'])
    def reset(message):
        '''
        Restarts all courses and alerts related to the user. Doesn't remove the user.
        Reinicia todas materias e alertas do usuario, removendo suas atribuicoes ao usuario. Nao remove usuario.'''

        if check_type_chat(message,bot):
            exit()
        msg = bot.send_message(message.chat.id,'''
        Tem certeza que deseja continuar? Todos os dados de mat??rias e alertas ser??o apagados''',reply_markup= gen_markup_confirm())
        bot.register_next_step_handler(msg, reset_s1)

    def reset_s1(message):
        if message.text == 'N??o':
            bot.send_message(message.chat.id,'''Opera????o cancelada!''')
            return -1
        elif message.text == 'Sim':
            bot.send_message(message.chat.id,'''Deletando todas materias e alertas do usuario ...''')
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(f"UPDATE Users SET materias = 0,types = 0 WHERE telegram = {message.chat.id};")
            cur.execute("COMMIT;")
            conn.close()
            bot.send_message(message.chat.id,"Voce quer reconfigurar as materias?",reply_markup = gen_markup_confirm())
            bot.register_next_step_handler(message,reset_s2)
        else:
            bot.send_message(message.chat.id,'''Opera????o abortada. Por favor, utilize os Bot??es para responder a mensagem. ''')
            return -1

    def reset_s2(message):
        if message.text == "Sim":
            reconfiguser = classes.User()
            courses = get_courses()

            poll=bot.send_poll(message.chat.id,"Quais tipos de avisos voc?? quer?",['1-Provas(1 semana antes e no dia)','2-EPs','3-Trabalhos','4-Aulas'],allows_multiple_answers = True)
            time.sleep(10)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            reconfiguser = get_poll_results(poll_results.options,reconfiguser,"2")

            poll=bot.send_poll(message.chat.id,"Quais mat??rias voc?? est?? fazendo?",get_courses(),allows_multiple_answers = True)
            time.sleep(10)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            reconfiguser = get_poll_results(poll_results.options,user,"1")

            sql = f"UPDATE Users SET materias ={materias_lista_to_number(reconfiguser.courses)}, types = {materias_lista_to_number(reconfiguser.warnings)} WHERE telegram = {message.chat.id};"
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(sql)
            cur.execute("COMMIT")
            conn.close()
            bot.send_message(message.chat.id,"O seu usuario foi reconfigurado!")
        elif message.text == "N??o":
            bot.send_message(message.chat.id,"Okay")
        else:
            bot.send_message(message.chat.id,"Por favor responda com 'Sim' ou 'N??o'")


    #Funcoes que atualizam informacoes do usuario
    @bot.message_handler(commands=['update'])
    def update(message):
        if check_type_chat(message,bot):
            return -1
        poll = bot.send_poll(message.chat.id,"Que informac??o voce gostaria de alterar?",['E-mail','Nome','Telegram'],allows_multiple_answers = False)
        time.sleep(10)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        if poll_results.options[0].voter_count == 1:
            bot.send_message(message.chat.id,"Qual o seu novo e-mail(@usp.br)?")
            bot.register_next_step_handler(message,email_update)
        elif poll_results.options[1].voter_count == 1:
            bot.send_message(message.chat.id,"Podemos utilizar o seu novo nome do Telegram?",reply_markup = gen_markup_confirm())
            bot.register_next_step_handler(message,name_update)
        elif poll_results.options[2].voter_count == 1:
            bot.send_message(message.chat.id,"Qual o seu nome e-mail(@usp.br)?")
            bot.register_next_step_handler(message,telegram_update)

    def email_update(message):
        if email_valid(message.text) and  email_check(message.text):
            sql = f"UPDATE Users SET email = '{message.text}' WHERE telegram = {message.chat.id};"
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(sql)
            cur.execute("COMMIT")
            conn.close()
            bot.send_message(message.chat.id,"E-mail registrado com sucesso")
        else:
            bot.send_message(message.chat.id,"E-mail invalido ou ja usado!")
            bot.send_message(message.chat.id,"Qual o seu novo e-mail(@usp.br)?")
            bot.register_next_step_handler

    def name_update(message):
        name = ""
        if message.text == "Sim":
            if type(message.from_user.first_name) == type("a"):
                name = message.from_user.first_name
            if type(message.from_user.last_name)== type("a"):
                name = name + " " + message.from_user.last_name
            if name == "":
                bot.send_message(message.chat.id,"Nome invalido")
                return -1
            else:
                sql = f"UPDATE Users SET name = '{name}' WHERE telegram = {message.chat.id};"
                conn = get_connect(2)
                cur = conn.cursor()
                cur.execute(sql)
                cur.execute("COMMIT")
                conn.close()
                bot.send_message(message.chat.id,"Nome alterado com sucesso!")
        elif message.text == "N??o":
            bot.send_message(message.chat.id,"N??o conseguimos alterar seu nome!")
        else:
            bot.send_message(message.chat.id,"Resposta invalida, por favor responda com 'Sim' ou 'N??o'")
            bot.register_next_step_handler(message,name_update)

    def telegram_update(message):
        if (not email_check(message.text)) and email_valid(message.text):
            bot.send_message(message.chat.id,"Qual o seu nome no Telegram antigo?")
            bot.register_next_step_handler(message,telegram_update2,message.text)
        else:
            bot.send_message(message.chat.id,"E-mail invalido ou n??o encontrado!")
            bot.send_message(message.chat.id,"Qual o seu e-mail(@usp.br)?")
            bot.register_next_step_handler(message,telegram_update)

    def telegram_update2(message,email):
        sql = f"SELECT name, admin FROM Users WHERE email = '{email}'"
        conn = get_connect(1)
        cur = conn.cursor()
        cur.execute(sql)
        for name,admin in cur:
            if (name,admin) ==(message.text,0)and user_check(message.chat.id):
                conn2 = get_connect(2)
                cur = conn2.cursor()
                cur.execute(f"UPDATE Users SET telegram = {message.chat.id} WHERE email = '{email}'")
                conn2.commit()
                conn2.close()
                bot.send_message(message.chat.id,"Telegram atualizado")
            else:
                bot.send_message(message.chat.id,"Nome invalido ou disposito ja registrado, tente seu nome completo")
                bot.register_next_step_handler(message,telegram_update2,email)
        conn.close()


    #Funcoes que criam uma materia
    @bot.message_handler(commands=['create_course'])
    def create_course(message):
        if check_type_chat(message,bot):
            return -1
        if not is_admin(message.chat.id):
            bot.send_message(message.chat.id,"Voce precisa ser admin para acessar esse comando")
            return -1
        bot.send_message(message.chat.id,"Qual a sigla da disciplina?")
        bot.register_next_step_handler(message,create_course_st)

    def create_course_st(message):
        newcourse = classes.Course()
        if len(message.text)==7 and check_course(message.text.upper()):
            newcourse.set_name(message.text.upper())
            bot.send_message(message.chat.id,"Qual o nome da materia?")
            bot.register_next_step_handler(message,create_course_st2,newcourse)
        else:
            bot.send_message(message.chat.id,"Curso ja criado ou nome errado, tente novamente!")
            bot.register_next_step_handler(message,create_course_st)

    def create_course_st2(message,newcourse):
        newcourse.set_course_name(message.text)
        bot.send_message(message.chat.id,"Qual o nome do Professor?")
        bot.register_next_step_handler(message,create_course_st3,newcourse)

    def create_course_st3(message,newcourse):
        newcourse.set_professor(message.text)
        newcourse.set_code(get_next_code())
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO Courses (name,name_materias,professor,code) VALUES ('{newcourse.get_name()}','{newcourse.get_course_name()}','{newcourse.get_professor()}',{newcourse.get_code()})")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Curso criado com sucesso!")


    #Funcao que deleta uma materia
    @bot.message_handler(commands=['delete_course'])
    def delete_course(message):
        '''
        Delets a course created by an admin.
        Deleta um curso criado por um admin na database.'''
        if check_type_chat(message,bot):
            return -1
        if is_admin(message.chat.id) and not user_check(message.chat.id):
            bot.send_message(message.chat.id,"Qual o nome do curso que voce deseja deletar?")
            bot.register_next_step_handler(message,delete_course_st)
        else:
            bot.send_message(message.chat.id,"Voce nao tem permissao para realizar esse comando")

    def delete_course_st(message):
        try:
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(f"DELETE FROM Courses WHERE Telegram = {message.text}")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id,"Materia deletada com sucesso")
        except:
            bot.send_message(message.chat.id,"Materia nao foi deletada com sucesso")


    #Funcao que atualiza os dados de uma materia
    @bot.message_handler(commands=['update_course'])
    def update_course(message):
        if is_admin(message.chat.id):
            poll = bot.send_poll(message.chat.id,"Qual a materia que voce quer alterar?",get_courses())
            time.sleep(7)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            for i in poll_results.options:
                if i.voter_count == 1:
                    poll = bot.send_poll(message.chat.id,f"Qual atributo de {i.text} voce quer alterar?",['Professor','Nome'])
                    time.sleep(7)
                    poll_results = bot.stop_poll(message.chat.id,poll.message_id)
                    if poll_results.options[0].voter_count == 1:
                        bot.send_message(message.chat.id,"Qual o novo nome do Professor?")
                        bot.register_next_step_handler(message,update_course_st_professor,i)
                    elif poll_results.options[1].voter_count == 1:
                        bot.send_message(message.chat.id,"Qual o novo nome da disciplina?")
                        bot.register_next_step_handler(message,update_course_st_nome,i)
                    else:
                        return -1

        else:
            bot.send_message(message.chat.id,"Voce nao tem autorizacao para realizar esse comando")

    def update_course_st_professor(message,i):
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Courses SET professor = '{message.text}' WHERE name_materias = '{i.text}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Curso atualizado")

    def update_course_st_nome(message,i):
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Courses SET name_materias = '{message.text}' WHERE name_materias = '{i.text}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Curso atualizado")


    #Funcao que cria um alerta de uma materia
    @bot.message_handler(commands=['set_warning'])
    def set_warning(message):
        if check_type_chat(message,bot):
            return -1
        if is_rc(message.chat.id)or is_admin(message.chat.id):
            bot.send_message(message.chat.id,"Qual o assunto do alerta?")
            bot.register_next_step_handler(message,set_warning_st)
        else:
            bot.send_message(message.chat.id,"Voce nao tem permissao para acessar este comando")

    def set_warning_st(message):
        new_warning = classes.Warning()
        new_warning.name = message.text
        poll = bot.send_poll(message.chat.id,"Qual o curso?",get_courses())
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        for i in poll_results.options:
            if i.voter_count == 1:
                new_warning.course = 2**poll_results.options.index(i)
        poll = bot.send_poll(message.chat.id,"Qual o tipo?",['Prova','EP','Trabalho','Aula'])
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        for i in poll_results.options:
            if i.voter_count == 1:
                if i.text == 'Prova':
                    new_warning.type = 1
                elif i.text == 'EP':
                    new_warning.type = 2
                elif i.text == 'Trabalho':
                    new_warning.type = 4
                elif i.text == 'Aula':
                    new_warning.type = 8
        bot.send_message(message.chat.id,"Repete toda semana?",reply_markup = gen_markup_confirm())
        bot.register_next_step_handler(message,set_warning_st2,new_warning)

    def set_warning_st2(message,warning):
        if message.text == 'Sim':
            warning.repeatable = 1
        elif message.text == 'N??o':
            warning.repeatable = 0
        else:
            bot.send_message(message.chat.id,"Mensagem invalida, responda Sim ou N??o")
            bot.register_next_step_handler(message,set_warning_st2,warning)
        bot.send_message(message.chat.id,"Qual a data do alerta? Formato: 'YYYY-MM-DD HH:MIN'")
        bot.register_next_step_handler(message,set_warning_st_final,warning)

    def set_warning_st_final(message,warning):
        warning.date = message.text;
        warning.creator = message.chat.id
        try:
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(f"INSERT INTO Warnings (name,course,type,creator,date,repeatable) VALUES ('{warning.name}','{warning.course}',{warning.type},'{warning.creator}','{warning.date}',{warning.repeatable})")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id,"Alerta criado com sucesso!")
        except mariadb.Error as e:
            print(e)
            bot.send_message(message.chat.id,"Data invalida, tente novamente! Formato: 'YYYY-MM-DD HH:MIN'")
            bot.register_next_step_handler(message,set_warning_st_final,warning)


    #Funcao que deleta um alerta de materia
    @bot.message_handler(commands=['del_warning'])
    def del_warning(message):
        poll = bot.send_poll(message.chat.id,"Qual a materia?",get_courses())
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        for i in poll_results.options:
            if i.voter_count == 1:
                conn = get_connect(3)
                cur = conn.cursor()
                cur.execute(f"SELECT name FROM Warnings WHERE course = {2**poll_results.options.index(i)}")

        list = []
        for i in cur:
            list.append(i[0])
        conn.close()
        try:
            poll = bot.send_poll(message.chat.id,"Qual o alerta?",list)
            time.sleep(7)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            for i in poll_results.options:
                if i.voter_count == 1:
                    conn = get_connect(2)
                    cur = conn.cursor()
                    cur.execute(f"DELETE FROM Warnings WHERE name = '{i.text}'")
                    conn.commit()
                    conn.close()
                    bot.send_message(message.chat.id,"Alerta deletado")
        except:
            if len(list) == 1:
                bot.send_message(message.chat.id,f"Somente um alerta para excluir: {list[0]}, tem certeza que quer deletar?",reply_markup = gen_markup_confirm())
                bot.register_next_step_handler(message,del_warning_1,list[0])
            elif len(list) == 0:
                bot.send_message(message.chat.id,"Nenhum alerta para excluir")

    def del_warning_1(message,name):
        if message.text == 'Sim':
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(f"DELETE FROM Warnings WHERE name = '{name}'")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id,"Alerta deletado")
        elif message.text == 'N??o':
            bot.send_message(message.chat.id,"Nenhum alerta deletado")


    #Funcao que altera um atributo de um alerta
    @bot.message_handler(commands = ['update_warning'])
    def update_warning(message):
        poll = bot.send_poll(message.chat.id,"Qual a materia?",get_courses())
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        for result in poll_results.options:
            if result.voter_count == 1:
                update_warning_st(message,2**poll_results.options.index(result))

    def update_warning_st(message,text):
        warnings = []
        conn = get_connect(3)
        cur = conn.cursor()
        cur.execute(f"SELECT name FROM Warnings WHERE course = {text}")
        for i in cur:
            warnings.append(i[0])
        conn.close()
        if len(warnings) >= 2:
            poll = bot.send_poll(message.chat.id,"Qual o alerta?",warnings)
            time.sleep(7)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            for i in poll_results.options:
                if i.voter_count == 1:
                    warning = i.text
        elif len(warnings) == 1:
            bot.send_message(message.chat.id,f"Somente o alerta {warnings[0]}")
            warning = warnings[0]
        else:
            bot.send_message(message.chat.id,"Nenhum alerta para deletar")
            return -1
        poll = bot.send_poll(message.chat.id,"Qual a mudanca?",['Nome','Tipo','Curso','Dia/Hora','Repetitivo'])
        time.sleep(7)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        if poll_results.options[0].voter_count == 1:
            bot.send_message(message.chat.id,"Qual o novo nome?")
            bot.register_next_step_handler(message,update_warning_st_name,warning)
        elif poll_results.options[1].voter_count == 1:
            poll = bot.send_poll(message.chat.id,"Qual o tipo?",['Prova','EP','Trabalho','Aula'])
            time.sleep(7)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            for i in poll_results.options:
                if i.voter_count == 1:
                    update_warning_st_type(message,warning,poll_results.options.index(i))
        elif poll_results.options[2].voter_count == 1:
            poll = bot.send_poll(message.chat.id,"Qual o curso?",get_courses())
            time.sleep(7)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            for i in poll_results.options:
                if i.voter_count == 1:
                    update_warning_st_course(message,warning,2**poll_results.options.index(i))
        elif poll_results.options[3].voter_count == 1:
            bot.send_message(message.chat.id,"Qual a nova data? Formato: 'YYYY-MM-DD HH:MM'")
            bot.register_next_step_handler(message,update_warning_st_date,warning)
        elif poll_results.options[4].voter_count == 1:
            bot.send_message(message.chat.id,"E repetitivo?",reply_markup = gen_markup_confirm())
            bot.register_next_step_handler(message,update_warning_st_repeatable,warning)

    def update_warning_st_name(message,warning):
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Warnings SET name = '{message.text}', creator = {message.chat.id} WHERE name = '{warning}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Nome alterado com sucesso!")

    def update_warning_st_type(message,warning,type):
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Warnings SET type = {2**type}, creator = {message.chat.id} WHERE name = '{warning}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Tipo alterado com sucesso!")

    def update_warning_st_course(message,warning,course):
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Warnings SET course = {course}, creator = {message.chat.id} WHERE name = '{warning}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Curso alterado com sucesso!")

    def update_warning_st_date(message,warning):
        try:
            conn = get_connect(2)
            cur = conn.cursor()
            cur.execute(f"UPDATE Warnings SET date = '{message.text}', creator = {message.chat.id} WHERE name = '{warning}'")
            conn.commit()
            conn.close()
            bot.send_message(message.chat.id,"Data alterada com sucesso!")
        except:
            bot.send_message(message.chat.id,"Data invalida, tente novamente! Formato: 'YYYY-MM-DD HH:MM'")
            bot.register_next_step_handler(message,update_warning_st_date,warning)

    def update_warning_st_repeatable(message,warning):
        if message.text == "Sim":
            repeatable = 1
        elif message.text == "N??o":
            repeatable = 0
        else:
            bot.send_message(message.chat.id,"Mensagem invalida, digite 'Sim' ou 'N??o'")
            return -1
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"UPDATE Warnings SET repeatable = {repeatable}, creator = {message.chat.id} WHERE name = '{warning}'")
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id,"Repeticao alterada com sucesso!")




    @bot.message_handler(commands=['alertas'])
    def get_alertas(message):
        '''
        Returns a list with all the alerts the user curently has.
        Delvolve uma lista com todos alertas definidos ao user.'''
        conn = get_connect(3)
        cur1 = conn.cursor()
        conn2 = get_connect(3)
        cur2 = conn2.cursor()
        cur1.execute(f"SELECT types,materias FROM Users WHERE telegram = {message.chat.id}")
        for i in cur1:
            types = materias_number_to_lista(i[0])
            courses = materias_number_to_lista(i[1])
        bot.send_message(message.chat.id,"Voce tem os seguintes alertas: ")
        for course in courses:
            for type in types:
                cur2.execute(f"SELECT name,date FROM Warnings WHERE course = {course} AND type = {type}")
                for i in cur2:
                    bot.send_message(message.chat.id,f"{i[0]}({i[1]})")
        conn.close()
        conn2.close()



    @bot.message_handler(commands=['materias'])
    def get_materias(message):
        """
        Returns a list with all courses defined by the user.
        Delvolve uma lista com todas materias definidas pelo user."""
        conn = get_connect(3)
        cur1 = conn.cursor()
        conn2 = get_connect(3)
        cur2 = conn2.cursor()
        cur1.execute(f"SELECT materias FROM Users WHERE telegram = {message.chat.id}")
        for i in cur1:
            courses = materias_number_to_lista(i[0])
        bot.send_message(message.chat.id,"Voce tem as seguintes materias: ")
        for course in courses:
            cur2.execute(f"SELECT name_materias FROM Courses WHERE code = {course}")
            for i in cur2:
                bot.send_message(message.chat.id,f"{i[0]}")
        conn.close()
        conn2.close()


    #Envia uma lista de comandos conforme a sua funcao no bot
    @bot.message_handler(commands=['help','ajuda','?'])
    def bot_help(message):
        '''
        Returns information and comands of the bot.
        Retorna informacao e comandos do bot.
        '''
        pass
        bot.send_message(message.chat.id,"Para usuarios comuns:\n /register : Para se registrar no banco de dados\n /unregister : Para retirar seu registro do banco de dados")
        bot.send_message(message.chat.id,"/reset : Para deletar os registros de materias e alertas e reconfigura-los\n /update : Para atualizar seus dados no banco de dados")
        bot.send_message(message.chat.id,"/alertas : Te devolve todos")
        if is_rc(message.chat.id):
            bot.send_message(message.chat.id,"Para RCs: \n /set_warning : Para criar um alerta para a turma \n /del_warning : Para deletar um alerta ja criado")
            bot.send_message(message.chat.id,"/")
        if is_admin(message.chat.id):
            bot.send_message(message.chat.id,"Para admins: \n /create_course : Para criar uma disciplina \n /delete_course : Para deletar uma disciplina")
            bot.send_message(message.chat.id,"/update_course : Atualiza uma informacao de um curso")

    t1 = threading.Thread(target=check_warnings)
    t1.start()




    bot.polling()




if __name__ == '__main__':
    main()

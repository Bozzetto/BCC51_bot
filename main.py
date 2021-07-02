#Importacao de modulos
import telebot
import time
import datetime
import mariadb
import sys
import math

import user
import course
import warning

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
                cur.execute("CREATE TABLE IF NOT EXISTS Courses( courseID int UNIQUE AUTO_INCREMENT PRIMARY KEY, name varchar(7) NOT NULL,name_materias varchar(40) NOT NULL, professor varchar(50), code int NOT NULL)")
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
    markup.add(telebot.types.KeyboardButton("Sim"), telebot.types.KeyboardButton("Não"))

    return markup

def main():
    inicializar()
    token = get_token()
    bot = telebot.TeleBot(token.rstrip())

    #Funcao que envia os dados iniciais para o usuario
    @bot.message_handler(commands=['start'])
    def start(message):
        if not check_type_chat(message,bot):
            bot.send_message(message.chat.id,"Bem-vindo ao bot do BCC 51")
            bot.send_message(message.chat.id,"Para mais informações sobre o bot visite: https://github.com/Bozzetto/BCC51_bot", disable_web_page_preview = True)
            bot.send_message(message.chat.id,"Para acessar os comandos do bot, digite '/help'")


    #Sequencia de funcoes que lidam com um pedido de registro
    @bot.message_handler(commands=['register'])
    def register(message):
        #Novo objeto user para o novo usuario
        newuser = user.User()
        #Checa se esta em um grupo
        if check_type_chat(message,bot):
            return -1
        if not user_check(message.chat.id):
            bot.send_message(message.chat.id,"Voce ja esta registrado")
            return -1
        bot.send_message(message.chat.id,"Vamos começar o seu processo de registro")
        bot.send_message(message.chat.id,"Qual o seu e-mail (@usp.br)?")
        bot.register_next_step_handler(message,process_email_step, newuser,bot)

    def process_email_step(message,user,bot):
        if email_valid(message.text)and email_check(message.text):
            user.email = message.text
            markup = gen_markup_confirm()
            bot.send_message(message.chat.id,"Podemos utilizar suas informações do Telegram? ",reply_markup = markup)
            bot.register_next_step_handler(message,process_information_step,user,bot)
        elif message.text == "/cancel":
            return -1
        else:
            bot.send_message(message.chat.id,"E-mail inválido. Por favor, digite novamente")
            bot.register_next_step_handler(message,process_email_step,user,bot)

    def process_information_step(message,user,bot):
        if message.text == 'Sim':
            markup = gen_markup_confirm()
            if type(message.from_user.first_name) == type("a"):
                user.name = message.from_user.first_name;
            if type(message.from_user.last_name) == type("a"):
                user.name = user.name +" "+ message.from_user.last_name;
            user.id = message.chat.id
            bot.send_message(message.chat.id,"Você é um RC?",reply_markup=markup)
            bot.register_next_step_handler(message,process_final_step,user,bot)
        else:
            bot.send_message(message.chat.id,"Nao foi possivel realizar o cadastro")
            return -1

    def process_final_step(message,user,bot):
        if message.text == 'Sim':
            user.rc = 1
        elif message.text =='Não':
            user.rc = 0
        else:
            bot.send_message(message.chat.id,"Não foi possivel realizar o cadastro")
            return -1

        courses = get_courses()

        poll=bot.send_poll(message.chat.id,"Quais tipos de avisos você quer?",['1-Provas(1 semana antes e no dia)','2-EPs','3-Trabalhos','4-Aulas'],allows_multiple_answers = True)
        time.sleep(10)
        poll_results = bot.stop_poll(message.chat.id,poll.message_id)
        user = get_poll_results(poll_results.options,user,"2")

        poll=bot.send_poll(message.chat.id,"Quais matérias você está fazendo?",get_courses(),allows_multiple_answers = True)
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
        Tem certeza que deseja continuar? Todos os dados de matérias e alertas serão apagados''',reply_markup= gen_markup_confirm())
        bot.register_next_step_handler(msg, reset_s1)

    def reset_s1(message):
        if message.text == 'Não':
            bot.send_message(message.chat.id,'''Operação cancelada!''')
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
            bot.send_message(message.chat.id,'''Operação abortada. Por favor, utilize os Botões para responder a mensagem. ''')
            return -1

    def reset_s2(message):
        if message.text == "Sim":
            reconfiguser = user.User()
            courses = get_courses()

            poll=bot.send_poll(message.chat.id,"Quais tipos de avisos você quer?",['1-Provas(1 semana antes e no dia)','2-EPs','3-Trabalhos','4-Aulas'],allows_multiple_answers = True)
            time.sleep(10)
            poll_results = bot.stop_poll(message.chat.id,poll.message_id)
            reconfiguser = get_poll_results(poll_results.options,user,"2")

            poll=bot.send_poll(message.chat.id,"Quais matérias você está fazendo?",get_courses(),allows_multiple_answers = True)
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
        elif message.text == "Não":
            bot.send_message(message.chat.id,"Okay")
        else:
            bot.send_message(message.chat.id,"Por favor responda com 'Sim' ou 'Não'")


    #Funcoes que atualizam informacoes do usuario
    @bot.message_handler(commands=['update'])
    def update(message):
        if check_type_chat(message,bot):
            return -1
        poll = bot.send_poll(message.chat.id,"Que informacão voce gostaria de alterar?",['E-mail','Nome','Telegram'],allows_multiple_answers = False)
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
        elif message.text == "Não":
            bot.send_message(message.chat.id,"Não conseguimos alterar seu nome!")
        else:
            bot.send_message(message.chat.id,"Resposta invalida, por favor responda com 'Sim' ou 'Não'")
            bot.register_next_step_handler(message,name_update)

    def telegram_update(message):
        if (not email_check(message.text)) and email_valid(message.text):
            bot.send_message(message.chat.id,"Qual o seu nome no Telegram antigo?")
            bot.register_next_step_handler(message,telegram_update2,message.text)
        else:
            bot.send_message(message.chat.id,"E-mail invalido ou não encontrado!")
            bot.send_message(message.chat.id,"Qual o seu e-mail(@usp.br)?")
            bot.register_next_step_handler(message,telegram_update)

    def telegram_update2(message,email):
        sql = f"SELECT name, admin FROM Users WHERE email = '{email}'"
        conn = get_connect(1)
        cur = conn.cursor()
        cur.execute(sql)
        for name in cur:
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
        newcourse = course.Course()
        if len(message.text)==7 and check_course(message.text.upper()):
            newcourse.name = message.text.upper()
            bot.send_message(message.chat.id,"Qual o nome da materia?")
            bot.register_next_step_handler(message,create_course_st2,newcourse)
        else:
            bot.send_message(message.chat.id,"Curso ja criado ou nome errado, tente novamente!")
            bot.register_next_step_handler(message,create_course_st)

    def create_course_st2(message,newcourse):
        newcourse.courseName = message.text
        bot.send_message(message.chat.id,"Qual o nome do Professor?")
        bot.register_next_step_handler(message,create_course_st3,newcourse)

    def create_course_st3(message,newcourse):
        newcourse.professor = message.text
        newcourse.code = get_next_code()
        conn = get_connect(2)
        cur = conn.cursor()
        cur.execute(f"INSERT INTO Courses (name,name_materias,professor,code) VALUES ('{newcourse.name}','{newcourse.courseName}','{newcourse.professor}',{newcourse.code})")
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
        if is_admin(message.chat.id) and user_check(message.chat.id):
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



                #
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
        if is_rc(message.chat.id):
            bot.send_message(message.chat.id,"Para RCs:")
            bot.send_message(message.chat.id,"/")
        if is_admin(message.chat.id):
            bot.send_message(message.chat.id,"Para admins: \n /create_course : Para criar uma disciplina \n /delete_course : Para deletar uma disciplina")
            bot.send_message(message.chat.id,"/update_course : Atualiza uma informacao de um curso")







    bot.polling()




if __name__ == '__main__':
    main()

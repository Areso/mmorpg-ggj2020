from flask import Flask, jsonify
from flask import request
from flask_sockets import Sockets
import json
from datetime import datetime, date
import mysql.connector
import hashlib
from datetime import datetime
import time
import asyncio
import threading
import sys


app = Flask(__name__)
sockets = Sockets(app)
mydb = {}
salt = ""
#token, login_id, token_age, char_id
open_sessions = []
players = []
race1_locx = 0
race1_locy = 5
race2_locx = 0
race2_locy = 4
pl_orders = []
gmap = [[2, 2, 2, 2, 2],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
        [2, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],]
gobj = [[0, 0, 0, 0, 0],
        [0, 0, 0, 0, 40],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [30, 0, 0, 0, 0]]
mapsize = 5
turn_status = 0 #0 - playes' turn; 1 - server's turn
turn_time = 30 #300 for big big server with multiply mechanics


class Player:
    def __init__(self, token):
        global mydb
        self.token = token
        char_id = get_char_id(token)
        self.char_id = char_id
        mycursor = mydb.cursor()
        mycursor.execute('SELECT * FROM chars WHERE id = %(char_id)s',
                         {'char_id': char_id})
        myresult = mycursor.fetchall()
        charname = myresult[0][2]
        race = myresult[0][3]
        portrait = myresult[0][4]
        guild_id = myresult[0][5]
        level = myresult[0][6]
        locx = myresult[0][7]
        locy = myresult[0][8]
        city = myresult[0][9]
        gold = myresult[0][10]
        ship = myresult[0][11]
        hp_cur = myresult[0][12]
        hp_max = myresult[0][13]
        team_cur = myresult[0][14]
        team_max = myresult[0][15]
        tutor = myresult[0][16]
        # TODO MAKE A QUERY TO GUILD TABLE TO OBTAIN GUILD NAME
        self.charname = charname
        self.race = race
        self.portrait = portrait
        self.guild_id = guild_id
        self.level = level
        self.locx = locx
        self.locy = locy
        self.city = city
        self.gold = gold
        self.ship = ship
        self.hp_cur = hp_cur
        self.hp_max = hp_max
        self.team_cur = team_cur
        self.team_max = team_max
        self.tutor = tutor


def myloading():
    cfgpath = "mysql-config.txt"
    fconf = open(cfgpath, 'r')
    tconf = fconf.read()
    fconf.close()
    conf_list = tconf.split('\n')
    return conf_list


def opencon(myconfig):
    global mydb
    mydb = mysql.connector.connect(
        host=myconfig[2],
        user=myconfig[0],
        passwd=myconfig[1],
        database=myconfig[4]
    )
    global salt
    salt = myconfig[5]
    print("open db connection")


def servers_turn():
    global turn_time
    global turn_status
    global pl_orders
    for each_order in pl_orders:
        print(each_order)
    pl_orders = []
    turn_time = 30
    turn_status = 0
    return 0


def server_routine():
    global turn_time
    global turn_status
    if turn_time > 0:
        turn_time = turn_time-1
    else:
        turn_status = 1
        servers_turn()
    time.sleep(1)
    return 0


def get_start_position(race):
    if race == 1:
        locx = 0
        locy = 4
    if race == 2:
        locx = 4
        locy = 1
    return [locx, locy]


def create_token(login, login_id):
    time_salt = str(datetime.now())
    to_token = login+time_salt
    to_token = to_token.encode('utf-8')
    token = hashlib.sha512(to_token).hexdigest()
    open_sessions.append([token, login_id, 0, ""])
    print([token, login_id, 0, ""])
    return token


#check if the token is exists?
def check_token(token):
    for each_session in open_sessions:
        session_token = each_session[0]
        if session_token == token:
            return True
            break
    return False


def get_login_id(token):
    for each_session in open_sessions:
        session_token = each_session[0]
        if session_token == token:
            session_login = each_session[1]
            return session_login
            break
    return ""


def get_char_id(token):
    for each_session in open_sessions:
        session_token = each_session[0]
        if session_token == token:
            session_char_id = each_session[3]
            return session_char_id
            break
    return ""


def get_login_pass_from_post():
    data_to_parse = str(request.get_data())
    data_to_parse = data_to_parse[2:-1]
    data_to_parse = json.loads(data_to_parse)
    login = data_to_parse['login']
    password = data_to_parse['password']
    return [login, password]


def get_token_from_post():
    data_to_parse = str(request.get_data())
    data_to_parse = data_to_parse[2:-1]
    data_to_parse = json.loads(data_to_parse)
    token = data_to_parse['token']
    return token


def get_json_from_post():
    data_to_parse = str(request.get_data())
    data_to_parse = data_to_parse[2:-1]
    myjson = json.loads(data_to_parse)
    return myjson


#get hash for inputted password
def get_hpassword(login_pass):
    global salt
    spassword = login_pass[1] + salt
    spassword = spassword.encode('utf-8')
    hpassword = hashlib.sha512(spassword).hexdigest()
    return hpassword


#get stored login_id, hashed password
def get_creds(login_pass):
    global mydb
    login = login_pass[0]
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id, login, pass FROM accounts WHERE login = %(login)s',
                     {'login': login})
    myresult = mycursor.fetchall()
    login_id = ""
    spassword = ""
    if len(myresult) > 0:
        for x in myresult:
            login_id = x[0]
            spassword = x[2]
    return [login_id, spassword]


#@sockets.route('/echo')
#def echo_socket(ws):
#    while not ws.closed:
#        message = ws.receive()
#        ws.send(message)


@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    login_pass = get_login_pass_from_post()
    hpassword = get_hpassword(login_pass)
    screds = get_creds(login_pass)
    slogin_id = screds[0]
    spassword = screds[1]
    token = ""
    if slogin_id != "":
        if spassword == hpassword:
            token = create_token(login_pass[0], slogin_id)
            content = "login_success"
            code = 200
        else:
            content = "error_the_login_is_in_use"
            code = 400
    else:
        mycursor = mydb.cursor()
        mycursor.execute("INSERT INTO accounts(login, pass) VALUES (%(login)s, %(hpassword)s)"
                         , {'login':login_pass[0], 'hpassword':hpassword})
        mydb.commit()
        #SELECT LAST_INSERT_ID(); BUT FOR GOD'S SAKE BECAUSE THERE IS ONLY ONE CONNECTION FOR THE WHOLE SERVER
        mycursor = mydb.cursor()
        mycursor.execute('SELECT id FROM accounts WHERE login = %(login)s',
                         {'login': login_pass[0]})
        myresult = mycursor.fetchall()
        login_id = myresult[0][0]#the first row, the first value
        token = create_token(login_pass[0], login_id)
        content = "register_success"
        code = 200
    return {"status": content, "token": token}, code, {"Access-Control-Allow-Origin": "*",
                                       "Content-type": "application/json",
                                       "Access-Control-Allow-Methods": "POST"}


@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    login_pass = get_login_pass_from_post()
    hpassword = get_hpassword(login_pass)
    screds = get_creds(login_pass)
    slogin_id = screds[0]
    spassword = screds[1]
    token = ""
    if spassword == hpassword:
        token = create_token(login_pass[0], slogin_id)
        content = "login_success"
        code = 200
    else:
        content = "no_user_with_this_email_pass"
        code = 400
    return {"status": content, "token": token}, code, {"Access-Control-Allow-Origin": "*",
                                                       "Content-type": "application/json",
                                                       "Access-Control-Allow-Methods": "POST"}


def get_chars():
    global mydb
    token = get_token_from_post()
    login_id = get_login_id(token)
    chars = []
    if token != "":
        if check_token(token):
            mycursor = mydb.cursor()
            mycursor.execute('SELECT id, charname FROM chars WHERE acc_id = %(login_id)s',
                             {'login_id': login_id})
            myresult = mycursor.fetchall()
            if len(myresult) > 0:
                for each_char in myresult:
                    chars.append([each_char[0], each_char[1]])
    return chars


@app.route('/char_list', methods=['POST', 'OPTIONS'])
def char_load():
    chars = get_chars()
    content = chars
    code = 200
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                       "Content-type": "application/json",
                                                       "Access-Control-Allow-Methods": "POST"}


def check_portrait(race, portrait):
    imagesRace1Length = 2
    imagesRace2Length = 2
    if race == 1:
        if portrait>race*1000 and portrait<=race*1000+imagesRace1Length:
            return True
        else:
            return False
    if race == 2:
        if portrait>race*1000 and portrait<=race*1000+imagesRace2Length:
            return True
        else:
            return False


def char_exists(charname):
    global mydb
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id FROM chars WHERE charname = %(charname)s',
                     {'charname': charname})
    myresult = mycursor.fetchall()
    if len(myresult) != 0:
        return True
    else:
        return False


def add_char_id_to_session(token, char_id):
    for each_session in open_sessions:
        session_token = each_session[0]
        if session_token == token:
            each_session[3] = int(char_id)
            print(each_session)
            break


@app.route('/char_create', methods=['POST', 'OPTIONS'])
def char_create():
    global mydb
    token = get_token_from_post()
    login_id = get_login_id(token)
    params = get_json_from_post()
    content = ""
    code = 200
    if login_id != "":
        chars = get_chars()
        if len(chars)==0:
            # create char
            if params['race'] == 1 or params['race'] == 2:
                if check_portrait(params['race'], params['portrait']) is True:
                    print(params['charname'])
                    if char_exists(params['charname']) is False:
                        mycursor = mydb.cursor()
                        start_pos = get_start_position(params['race'])
                        mycursor.execute("""INSERT INTO chars(acc_id, charname, race_id, portrait_id, locx, locy)
                                          VALUES (%(acc_id)s, %(charname)s, %(race_id)s, 
                                          %(portrait_id)s, %(locx)s, %(locy)s)""",
                                            {'acc_id': login_id,
                                             'charname': params['charname'],
                                             'race_id': params['race'],
                                             'portrait_id': params['portrait'],
                                             'locx': start_pos[0],
                                             'locy': start_pos[1]})
                        mydb.commit()
                        mycursor = mydb.cursor()
                        mycursor.execute('SELECT id FROM chars WHERE charname = %(charname)s',
                                         {'charname': params['charname']})
                        myresult = mycursor.fetchall()
                        char_id = myresult[0][0]  # the first row, the first value
                        add_char_id_to_session(token, char_id)
                        content = "OK"
                        code = 200
                    else:
                        content = "charnameTaken"
                        code = 400
                else:
                    # the portrait isn't right
                    content = "otherError-badPortrait"
                    code = 400
            else:
                # there is no such race
                content = "otherError-noSuchRace"
                code = 400
        else:
            # you already have maximum allowed chars (1)
            content = "otherError-maxChars"
            code = 400
    else:
        # provided token doesn't found in runtime
        content = "otherError-noTokenFound"
        code = 400
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                       "Content-type": "application/json",
                                                       "Access-Control-Allow-Methods": "POST"}


@app.route('/char_select', methods=['POST', 'OPTIONS'])
def char_select():
    params = get_json_from_post()
    token = get_token_from_post()
    login_id = get_login_id(token)
    # check whether this character actually belongs to this user
    mycursor = mydb.cursor()
    mycursor.execute('SELECT id FROM chars WHERE id = %(char_id)s AND acc_id = %(acc_id)s',
                     {'char_id': params['char_id'],
                      'acc_id': login_id})
    myresult = mycursor.fetchall()
    if len(myresult) > 0:
        add_char_id_to_session(token, params['char_id'])
        content = "OK"
        code = 200
    else:
        content = "char_select_error"
        code = 400
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                       "Content-type": "application/json",
                                                       "Access-Control-Allow-Methods": "POST"}


@app.route('/char_get', methods=['POST', 'OPTIONS'])
def char_get():
    token = get_token_from_post()
    if check_token(token):
        cur_player = get_cur_player(token)
        if cur_player is None:
            player = Player(token)
            players.append(player)
        else:
            player = cur_player
        content = player.__dict__
        code = 200
    else:
        content = "bad-token"
        code = 400
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                       "Content-type": "application/json",
                                       "Access-Control-Allow-Methods": "POST"}


@app.route('/env_get', methods=['POST', 'OPTIONS'])
def env_get():
    token = get_token_from_post()
    lgobj = gobj
    for each_player in players:
        race=each_player.race
        ship=each_player.ship
        locx=each_player.locx
        locy=each_player.locy
        print("len of players in lgobj "+str(len(players)))
        #if race==1:
        if ship == 11:
            lgobj[locx][locy] = 11
        if ship == 12:
            lgobj[locx][locy] = 12
        if ship == 21:
            lgobj[locx][locy] = 21
        if ship == 22:
            lgobj[locx][locy] = 22
    if check_token(token):
        code = 200
        content = "OK"
    else:
        code = 400
        content = "bad-token"
    return {"status": content, "gmap": gmap, "gobj": lgobj}, code, {"Access-Control-Allow-Origin": "*",
                                       "Content-type": "application/json",
                                       "Access-Control-Allow-Methods": "POST"}


def get_cur_loc(token):
    for each_player in players:
        ptoken = each_player.token
        if token == ptoken:
            cur_locx = each_player.locx
            cur_locy = each_player.locy
            return [cur_locx, cur_locy]
            break
    return ""


def gen_path_map(start, size, travelable):
    # neighbor_offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    neighbor_offsets = [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (1, -1), (1, 1), (-1, 1)]
    # score = 0
    #path_map = [[None for _ in range(size)] for _ in range(size)]
    path_map = [[0 for x in range(0, size)] for y in range(0, size)]
    node_list = [start]
    # print("blank path map")
    path_map[start[0]][start[1]] = 1
    for node in node_list:
        # print("---new-node---")
        score = path_map[node[0]][node[1]]
        # print(score)
        for neighbor_offset in neighbor_offsets:
            # print("run over neighbor offsets")
            neighbor_x = node[0]+neighbor_offset[0]
            neighbor_y = node[1]+neighbor_offset[1]
            if (neighbor_x < 0 or
               neighbor_y < 0 or
               neighbor_x >= size or
               neighbor_y >= size):
                # print("out of borders - we can not move here "+str(neighbor_x)+";"+str(neighbor_y))
                continue
            if travelable[neighbor_x][neighbor_y] == 0:
                # print("not travelable - we can not move here "+str(neighbor_x)+";"+str(neighbor_y))
                continue
            if travelable[neighbor_x][neighbor_y] == 1:
                # print("travelable - we could move there " + str(neighbor_x) + ";" + str(neighbor_y))
                if neighbor_x == start[0] and neighbor_y == start[1]:
                    #print("we found the target!")
                    path_map[neighbor_x][neighbor_y] = score + 1
                else:
                    if path_map[neighbor_x][neighbor_y] == 0:
                        #print("can move here "+str(neighbor_x)+";"+str(neighbor_y))
                        node_list.append([neighbor_x, neighbor_y])
                        path_map[neighbor_x][neighbor_y] = score + 1
                        continue
                    else:
                        #print("we already have been here " + str(neighbor_x) + ";" + str(neighbor_y))
                        continue
    print("-----")
    return path_map


def prepare_map_for_pf():
    prepared_map = []
    for i in range(0, mapsize):
        prepared_map.append([])
        for j in range(0, mapsize):
            if gmap[i][j] == 0:
                cellv = 1
                if cellv == 1:
                    if gobj[i][j] == 0:
                        cellv = 1
                    else:
                        cellv = 0
            else:
                cellv = 0
            prepared_map[i].append(cellv)
    return prepared_map


def get_path(wave_map, target, token):
    if (wave_map[target[0]][target[1]] != 0 and
       wave_map[target[0]][target[1]] != -1):
        print("try to get_path")
        print(wave_map[target[0]][target[1]])
        # neighbor_offsets = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbor_offsets = [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, -1), (1, -1), (1, 1), (-1, 1)]
        node_list = [target]
        score = wave_map[target[0]][target[1]]
        # print("blank path map")
        size = 4
        for node in node_list:
            for neighbor_offset in neighbor_offsets:
                neighbor_x = node[0]+neighbor_offset[0]
                neighbor_y = node[1]+neighbor_offset[1]
                if (neighbor_x < 0 or
                   neighbor_y < 0 or
                   neighbor_x >= size or
                   neighbor_y >= size):
                    # print("out of borders - we can not move here "+str(neighbor_x)+";"+str(neighbor_y))
                    continue
                if wave_map[neighbor_x][neighbor_y] < score and wave_map[neighbor_x][neighbor_y] != 0:
                    score = wave_map[neighbor_x][neighbor_y]
                    node_list.append([neighbor_x, neighbor_y])
        print(node_list)
        player = get_cur_player(token)
        player.locx = target[1]
        player.locy = target[0]
        print("before we remove the player"+str(len(players)))
        players.remove(player)  # NOT DEBUG
        print("after we remove the player" + str(len(players)))
        players.append(player)  # NOT DEBUG
        print("after we add the player" + str(len(players)))
        res = upd_cur_player_db(token)
        #if res == "good":
        #    code = 200
        #    content = "passed_to_next_part_tutor"
        #else:
        #    code = 400
        #    content = "database_update_went_wrong"
        return node_list
    else:
        return "no way!"


@app.route('/path_find', methods=['POST', 'OPTIONS'])
def path_find():
    token = get_token_from_post()
    params = get_json_from_post()
    points = []
    if check_token(token):
        pfmap = prepare_map_for_pf()
        target = params['target']
        print("we want to go there")
        print(target)
        source = get_cur_loc(token)
        print("and we are here")
        print(source)
        path_map = gen_path_map(source, mapsize, pfmap)
        path_array = get_path(path_map, target, token)
        for i in range(0, mapsize):
            print(path_map[i])
        code = 200
        content = path_array
    else:
        code = 400
        content = "bad-token"
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                                   "Content-type": "application/json",
                                                                   "Access-Control-Allow-Methods": "POST"}


def get_cur_tutor(token):
    for each_player in players:
        ptoken = each_player.token
        if token == ptoken:
            tutor_fact = each_player.tutor
            return tutor_fact
            break
    return ""


def get_cur_player(token):
    cur_player = None
    for each_player in players:
        ptoken = each_player.token
        if token == ptoken:
            cur_player = each_player
            break
    return cur_player


def upd_cur_player_db(token):#INSTEAD OF TOKEN GET PLAYER TO WRITE HIM TO DB
    char_id = None
    for each_player in players:
        ptoken = each_player.token
        if token == ptoken:
            char_id = each_player.char_id
            player_upd = each_player
            #break
            print("found the player object")
    if char_id is not None:
        mycursor = mydb.cursor()
        mycursor.execute("""UPDATE chars SET guild_id=%(guild_id)s, level=%(level)s, locx=%(locx)s,
                            locy=%(locy)s, city=%(city)s, gold=%(gold)s, ship=%(ship)s,
                            hp_cur=%(hp_cur)s, hp_max=%(hp_max)s, team_cur=%(team_cur)s,
                            team_max=%(team_max)s, tutor = %(tutor)s
                            WHERE id=%(char_id)s""",
                         {'char_id': char_id,
                          'guild_id': player_upd.guild_id,
                          'level': player_upd.level,
                          'locx': player_upd.locx,
                          'locy': player_upd.locy,
                          'city': player_upd.city,
                          'gold': player_upd.gold,
                          'ship': player_upd.ship,
                          'hp_cur': player_upd.hp_cur,
                          'hp_max': player_upd.hp_max,
                          'team_cur': player_upd.team_cur,
                          'team_max': player_upd.team_max,
                          'tutor': player_upd.tutor})
        mydb.commit()
        result_of_update = "good"
    else:
        result_of_update = "bad"
    return result_of_update


@app.route('/next_tutor', methods=['POST', 'OPTIONS'])
def next_tutor():
    token = get_token_from_post()
    params = get_json_from_post()
    if check_token(token):
        cur_tutor_fact = get_cur_tutor(token)
        if (cur_tutor_fact >=0 and cur_tutor_fact <=3):
            player = get_cur_player(token)
            if cur_tutor_fact == 0:
                player.tutor = 1
                players.remove(player)  # NOT DEBUG
                players.append(player)  # NOT DEBUG
                res = upd_cur_player_db(token)
                if res == "good":
                    code = 200
                    content = "passed_to_next_part_tutor"
                else:
                    code = 400
                    content = "database_update_went_wrong"
            if cur_tutor_fact == 1:
                player = get_cur_player(token)
                player.tutor = 2
                player.gold = player.gold + 120
                players.remove(player)  # NOT DEBUG
                players.append(player)  # NOT DEBUG
                res = upd_cur_player_db(token)
                if res == "good":
                    code = 200
                    content = "passed_to_next_part_tutor"
                else:
                    code = 400
                    content = "database_update_went_wrong"
            if cur_tutor_fact == 2:
                player = get_cur_player(token)
                if player.gold >= 50:
                    player.tutor = 3
                    player.gold = player.gold - 50
                    print("trying to buy a ship")
                    # TODO CHECK THIS CODE HAS BUG
                    local_ship = int(params['ship'])
                    print(params)
                    print(params['ship'])
                    print(type(params['ship']))
                    if player.race == 1:
                        if local_ship == 1:
                            player.ship = 11
                        if local_ship == 2:
                            player.ship = 12
                    if player.race == 2:
                        if local_ship == 1:
                            player.ship = 21
                        if local_ship == 2:
                            player.ship = 22
                    player.hp_cur = 500
                    player.hp_max = 500
                    player.team_cur = 0
                    player.team_max = 10
                    players.remove(player)  # NOT DEBUG
                    players.append(player)  # NOT DEBUG
                    res = upd_cur_player_db(token)
                    if res == "good":
                        code = 200
                        content = "passed_to_next_part_tutor"
                    else:
                        code = 400
                        content = "database_update_went_wrong"
                else:
                    code = 400
                    content = "dont_enough_money"
            if cur_tutor_fact == 3:
                player = get_cur_player(token)
                if player.gold >= 50:
                    player.tutor = 4
                    player.gold = player.gold - 50
                    player.team_cur = player.team_max
                    players.remove(player)  # NOT DEBUG
                    players.append(player)  # NOT DEBUG
                    res = upd_cur_player_db(token)
                    if res == "good":
                        code = 200
                        content = "passed_to_next_part_tutor"
                    else:
                        code = 400
                        content = "database_update_went_wrong"
                else:
                    code = 400
                    content = "dont_enough_money"
        else:
            code = 400
            content = "you_passed_the_tutorial_already"
    else:
        code = 400
        content = "bad-token"
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                                   "Content-type": "application/json",
                                                                   "Access-Control-Allow-Methods": "POST"}


@app.route('/town_leave', methods=['POST', 'OPTIONS'])
def town_leave():
    token = get_token_from_post()
    params = get_json_from_post()
    if check_token(token):
        player = get_cur_player(token)
        if player.city == 1:
            player.city = 0
            if player.race == 1:
                player.locx = 1
                player.locy = 4
            if player.race == 2:
                player.locx = 4
                player.locy = 2
            players.remove(player)  # NOT DEBUG
            players.append(player)  # NOT DEBUG
            res = upd_cur_player_db(token)
            if res == "good":
                code = 200
                content = "passed_to_next_part_tutor"
            else:
                code = 400
                content = "database_update_went_wrong"
        else:
            code = 400
            content = "you already leaved the town"
    else:
        code = 400
        content = "bad-token"
    return {"status": content}, code, {"Access-Control-Allow-Origin": "*",
                                                                   "Content-type": "application/json",
                                                                   "Access-Control-Allow-Methods": "POST"}



if __name__ == "__main__":
    myconfig = myloading()
    opencon(myconfig)
    aging_routine = threading.Thread(target=server_routine)
    aging_routine.start()
    print('run web server')
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()


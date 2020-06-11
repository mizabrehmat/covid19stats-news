import pymysql.cursors
host = "104.223.107.42"
new_user_busy = 0
new_group_busy = 0
update_user_busy = 0
update_group_busy = 0

class DB:
    conn = None
    def connect(self):
        self.conn = pymysql.connect(host = host,user = "mizab",password = "mizabrehmat",db = "covid19bot")
    def query(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except:
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor
    def commit(self):
        try:
            self.conn.commit()
        except:
            self.connect()
            self.conn.commit()

db = DB()

def check_connection(conn):
    def check_db_connection(conn):
        if conn:
            return True
        else:
            try:
                conn =  connect(host = "104.223.107.42",user = "amit",password = "amitpandey123121",db = "covid19bot")
                return True
            except:
                return False
    return check_db_connection(conn)

def new_user(userid):
    
    sql = "Insert into tgusers (userid) values ({})".format(userid)
    db.query(sql)
    db.commit()
    print("Executed New User ID :{}".format(argv[0]))


def check_user(id):
    sql = "Select * from tgusers where userid = {}".format(id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False
    print("Check USer ID: {}".format(id))

def check_group(id):
    sql = "Select * from groups where chatid = {}".format(id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False
    print("CHeck Group ID: {}".format(id))

def check_news(chat_id):
    sql = 'Select * from autonews where chatid = {}'.format(chat_id)
    a = db.query(sql)
    r = a.fetchall()
    if r:
        return r[0]
    else:
        return False

def create_auto_news(chatid,*args):
    if args:
        ison = int(args[0])
        sql = 'Insert into autonews(chatid,ison) values({},{})'.format(chatid,ison)
    else:
        args = False
        sql = 'insert into autonews(chatid) values({})'.format(chatid)
    db.query(sql)
    db.commit()

def update_news(chatid,value,country):
    sql = str("Update autonews SET ")
    if chatid:
        pass
    else:
        return False
    end = str("Where chatid = {}").format(chatid)
    if value != 'n':
        sql = sql+"ison = {} ".format(value)
    if country != 'n':
        if value!='n':
            sql = sql+',country = "{}" '.format(country)
        else:
            sql = sql+'country = "{}" '.format(country)
    sql = sql+end
    print(sql)
    db.query(sql)
    db.commit()


import pymysql


class Database:
    def __init__(self):
        self.db = None
        self.cur = None

    def connect_db(self):
        self.db = pymysql.connect(host='localhost',
                                  port=3306,
                                  user='root',
                                  passwd='123456789a!',
                                  db='login_schema',
                                  charset='utf8')
        self.cur = self.db.cursor(pymysql.cursors.DictCursor)

    def close_db(self):
        self.db.commit()
        self.db.close()

    def insert_user(self, id, pw, name, email):
        self.connect_db()
        sql = """INSERT INTO `login_schema`.`info`
        (`id`,`password`,`username`,`email`)VALUES(%s, %s, %s, %s);"""
        self.cur.execute(sql, (id, pw, name, email))
        self.close_db()

    def user_id_check(self):
        self.connect_db()
        sql = "SELECT ID FROM INFO;"
        self.cur.execute(sql)

    def executeOne(self):
        row = self.cur.fetchone()
        return row

    def executeAll(self):
        row = self.cur.fetchall()
        return row


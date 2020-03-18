import psycopg2


class Postgre:
    conn = None
    cur = None

    def __init__(self):
        self.conn = psycopg2.connect(database="d1774sms9m8gp5", user="hmrdcrywqbdvqj",
                                     password="f1219187293d8e10e69ee806cf6012787a696fb3539e0976db9f664db7112d38",
                                     host="ec2-23-22-156-110.compute-1.amazonaws.com", port="5432")
        self.cur = self.conn.cursor()

    def query(self, sql, params=None):
        res = None
        try:
            self.cur.execute(sql, params)
            res = self.cur.fetchall()
        except Exception:
            print("error happened when query")
        return res

    def close(self):
        self.cur.close()
        self.conn.close()

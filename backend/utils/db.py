from utils.connection import PostgreConn


class Database:
    def __init__(self, sufix=""):
        self.sufix = sufix

    def __enter__(self):
        self.conn = PostgreConn(sufix=self.sufix)
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.conn:
            self.conn.close()

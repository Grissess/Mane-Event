import sqlite3

class DB(object):
    def __init__(self, config):
        self.db = sqlite3.connect(config['database_file'])
        self.cur = self.db.cursor()

    def execute(self, stmt, repl=()):
        self.cur.execute(stmt, repl)
        return self.cur

    def commit(self):
        self.db.commit()

import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('mock.db', check_same_thread=False)
        self.conn.row_factory = dict_factory

        self.cursor = self.conn.cursor()

        # # create table if not exists
        # self._ensure_table()

    def _ensure_table(self):
        # Abstract method - must be overriden
        raise Exception


    def insert(self, query, data):
        self.cursor.execute(query, (list(data.values())))
        self.conn.commit()

    def select(self):
        sql = f"""
            select * from {self.table_name}
        """
        data = self.cursor.execute(sql)
        return data.fetchall()

    def list(self, conds={}):
        sql = f"""
            select * from {self.table_name} {self._handle_conds(conds)}
        """
        data = self.cursor.execute(sql)
        return data.fetchall()

    def _handle_conds(self, conds: dict) -> str:
        cond_components = []
        for key, value in conds.items():
            value = f"{value}" if isinstance(value, int) else f"'{value}'"

            cond_components.append(f"{key} = {value}")
        
        return "WHERE " + " AND ".join(cond_components)

    def read(self, query, id):
        data = self.cursor.execute(query)
        return data.fetchall()



class User(Database):
    def __init__(self):
        super().__init__()
        self.table_name = "user"

        self._ensure_table()

    def _ensure_table(self):
        self.cursor.execute(f"""
            create table if not exists {self.table_name}
            (id integer, name text, surname text, email text);
        """)
        self.conn.commit()

    def insert(self, data):
        query = f"""
            insert into {self.table_name} values (?, ?, ?, ?)
        """
        super().insert(query, data)

    def read(self, id, conds={}):
        conds["id"] = id
        query = f"""
            select * from {self.table_name} {self._handle_conds(conds)}
        """

        print(query)

        return super().read(query, id)


class Address(Database):
    def __init__(self):
      super().__init__()
      self.table_name = "address"

if __name__ == "__main__":
    db = User()
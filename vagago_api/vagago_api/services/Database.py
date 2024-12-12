from sqlalchemy import create_engine, insert, text

class Database:
    __instance = None
    __connection = None

    # This method ensures that only one instance of the Database class is created
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(Database, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        if Database.__connection is None:
            engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/DB")
            Database.__connection = engine.connect()

    def get_connection(self):
        return Database.__connection

    def insert(self, table, values):
        connection = self.get_connection()
        result = connection.execute(insert(table).returning(*table.c), values)
        connection.commit()
        return result.fetchone()

    def query(self, query, params = None):
        connection = self.get_connection()
        return connection.execute(text(query), params).fetchall()

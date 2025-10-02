import mysql.connector
from mysql.connector import Error


class MYSQLConnect:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.config={"host": host, "port": port, "user": user, "password": password}
        self.connection = None
        self.cursor = None

    try:
        def connect(self):
            self.connection =mysql.connector.connect(**self.config)
            self.cursor =self.connection.cursor()
            print("--------Connected to MYSQL-------")
            return self.connection, self.cursor

        def close(self):
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                print("--------MYSQL CLOSED--------")

        def __enter__(self):
            self.connect()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

    except Error as e:
        raise Exception(f"-------failed to connect MSQL : {e}--------------")


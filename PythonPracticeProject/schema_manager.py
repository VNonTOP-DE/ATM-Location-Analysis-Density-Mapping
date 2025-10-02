from mysql.connector import Error

SQL_PATH = "C:\\Users\\Public\\PythonPracticeProject\\schema.sql"

def create_mysql_schema(connection , cursor):
    database = "ATM_DATA"
    cursor.execute(f"DROP DATABASE IF EXISTS {database}")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    connection.commit()
    print(f"-----------------CREATE {database} SUCCESS------------------")
    connection.database = database
    try:
        with open(SQL_PATH, 'r') as file:
            sql_script = file.read()
            sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]

        for cmd in sql_commands:
            cursor.execute(cmd)
            print(f"------------Executed my sql command-----------")
    except Error as e:
        connection.rollback()
        raise Exception(f"-----------Failed to create mysql schema : {e} -------------") from e

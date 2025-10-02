from dataclasses import dataclass


@dataclass
class MYSQLConfig():
    host: str = 'localhost'
    port: int = 3306
    user: str = 'root'
    password: str = '123'
    table: str = 'ATM_DATA'  # Updated to match the table name
    database: str = 'ATM_DATA'  # Added for database name

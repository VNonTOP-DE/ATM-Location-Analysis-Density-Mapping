import pandas as pd
from database_connect import MYSQLConnect
from schema_manager import create_mysql_schema
from database_config import MYSQLConfig
from sqlalchemy import create_engine
from ATM_analyze import ATMDensityAnalyzer


def main():
    df = pd.read_csv('ATM_Banking.csv')
    config = MYSQLConfig(
        host='localhost',
        port=3306,
        user='root',
        password='123',
        table='ATM_DATA',
        database='ATM_DATA'
    )

    with MYSQLConnect(config.host, config.port, config.user, config.password) as my_sql_client:
        connection, cursor = my_sql_client.connection, my_sql_client.cursor
        create_mysql_schema(connection, cursor)
        url = "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(config.user, config.password, config.host, config.port,
                                                             config.database)
        engine = create_engine(url)
        df.to_sql(config.table, con=engine, if_exists="append", index=False)

        # Run ATM Analysis
        analyzer = ATMDensityAnalyzer()
        analyzer.run_analysis()


if __name__ == "__main__":
    main()
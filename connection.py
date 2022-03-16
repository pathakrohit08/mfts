import pandas as pd
import psycopg2
from sqlalchemy import create_engine

from config import Config


class SQLDB(object):
    """This is a singleton class that returns only 1 instance of POSTGRESSQL connection"""
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SQLDB, cls).__new__(cls)
            cls.__conn = None
            try:
                """Initializes and returns new connection to POSTGRESQL server"""
                print('Connecting to the PostgreSQL database...')
                cls.__conn = psycopg2.connect(host=Config.DB_HOSTNAME,
                            database=Config.DB_DATABASE,
                            user=Config.DB_USERNAME,
                            password=Config.DB_PASSWORD)
                cls.__engine=create_engine(f'postgresql://{Config.DB_USERNAME}:{Config.DB_PASSWORD}@{Config.DB_HOSTNAME}:{Config.DB_PORT}/{Config.DB_DATABASE}')

                print('Connection was successfull')
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
        return cls.instance

    def test_connection(self):
        if self.__conn is None:
            raise ValueError("Connection is not initialized")

        cur = self.__conn.cursor()
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print(db_version)
        cur.close()

    def save_stock_master(self,sql,symbol,name,volume,sector,industry,last_updated_date):
        """ insert a new vendor into the vendors table """
        id=None
        try:
            # create a new cursor
            cur =self.__conn.cursor()
            # execute the INSERT statement
            cur.execute(sql, (symbol,name,volume,sector,industry,last_updated_date,))
            # get the generated id back
            id = cur.fetchone()[0]
            # commit the changes to the database
            self.__conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except psycopg2.ProgrammingError as exc:
            print(exc.message)
        except psycopg2.InterfaceError as exc:
            print(exc.message)
    
        return id


    def update_stock_master(self,sql,last_updated_date,stockId):
        """ insert a new vendor into the vendors table """
        id=None
        try:
            # create a new cursor
            cur =self.__conn.cursor()
            # execute the UPDATE statement
            updatedDate="'"+last_updated_date+"'"
            cur.execute(sql,(last_updated_date,stockId))
            # get the generated id back
            id = cur.rowcount
            # commit the changes to the database
            self.__conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except psycopg2.ProgrammingError as exc:
            print(exc.message)
        except psycopg2.InterfaceError as exc:
            print(exc.message)
    
        return id

    def save_data(self,table_name,df):
        """use this function to save dataframe
           Args
           table_name: the name of the table (will get created if not exist)
           dataframe: the dataframe which holds the data
        """
        df.head(df.shape[0]).to_sql(table_name, self.__engine,if_exists='append',index=True)

    def get_stock_details(self,tickrId,start_date,end_date):  
        # startDate="'"+start_date+"'"
        # endDate="'"+end_date+"'"
        df = pd.read_sql(f'select * from stockdetails where "stockId" =\'{tickrId}\' and "Date">=\'{end_date}\' and "Date"<=\'{start_date}\' order by "Date" asc', con=self.__engine)
        return df

    def get_tickr(self,tickr): 
        try:
            # tickrInfo="'"+tickr+"'"
            df = pd.read_sql(f'select * from "stockmaster" where "Symbol" =\'{tickr}\';', con=self.__engine)
            return df
        except Exception as e:
            print(e)

    def delete_stock_details(self,stockId):
        """use this function to delete stock details """

        rows_deleted=None
        try:
            print("Delete was called")
            # create a new cursor
            cur =self.__conn.cursor()
            # execute the INSERT statement
            cur.execute(f'Delete from "stockdetails" where "stockId"={stockId}')
            # get the generated id back
            rows_deleted = cur.rowcount
            # commit the changes to the database
            self.__conn.commit()
            # close communication with the database
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        except psycopg2.ProgrammingError as exc:
            print(exc.message)
        except psycopg2.InterfaceError as exc:
            print(exc.message)
    
        return rows_deleted

    def execute_query(self,query):
        if self.__conn is None:
            raise ValueError("Connection is not initialized")
        cur = self.__conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        cur.close()

        return result

    def update_query(self,query):
        if self.__conn is None:
            raise ValueError("Connection is not initialized")
        cur = self.__conn.cursor()
        cur.execute(query)
        result = cur.rowcount
        cur.close()

        return result

    


    



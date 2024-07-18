# coding=utf-8
# databaseQuery.py

import mysql
from mysql.connector import Error
from contextlib import contextmanager

class Database:
    def __init__(self, config, db):
        self.config = config
        self.db = db

    @contextmanager
    def get_connection(self):
        connection = None
        try:
            connection = mysql.connector.connect(**self.config)
            yield connection
        except Error as e:
            self._logger.info(f"Error connecting to MySQL database: {e}")
        finally:
            if connection and connection.is_connected():
                self._logger.info("Successfully connected to the database.")
                connection.close()

    def execute_query(self, query, params=None):
        with self.get_connection() as connection:
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                connection.commit()
                return cursor.fetchall()
            except Error as e:
                self._logger.info(f"Error executing query: {e}")
                return None
            finally:
                cursor.close()
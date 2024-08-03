import pymysql
from pymysql import Error

class DatabaseManager:
    def __init__(self, plugin, logger):
        self.logger = logger
        self.plugin = plugin
        self.connection_settings = None
        self.connection = None

    def _set_connection_settings(self, config):
        """
        Sets the database connection settings.
        """
        db_config = {
        'host': config.get('db_host'),
        'user': config.get('db_user'),
        'password': config.get('db_password'),
        'database': config.get('db_database'),
        'port': int(config.get('db_port', 3306))
        }
        
        self.connection_settings = db_config
        
    def _test_connection(self, config):
        """
        Tests the database connection.
        """
        db_config = {
        'host': config.get('db_host'),
        'user': config.get('db_user'),
        'password': config.get('db_password'),
        'database': config.get('db_database'),
        'port': int(config.get('db_port', 3306))
        }
    
        try:
            connection = pymysql.connect(**db_config)
            connection.close()
            self.logger.info("Successfully connected to the database.")
            return {"status": "success", "message": "Connection successful"}
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")
            return {"status": "error", "message": str(e)}

    def get_connection(self):
        """
        Establishes and returns a connection to the database.
        """
        if not self.connection_settings:
            self.logger.error("Database configuration is not set.")
            return {"status": "error", "message": str(e)}
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(**self.connection_settings)
                self.logger.info("Successfully connected to the database.")
            return self.connection
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")
            return {"status": "error", "message": str(e)}

    def close_connection(self):
        """
        Closes the database connection.
        """
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed.")
            except Error as e:
                self.logger.error(f"Error closing database connection: {e}")

    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        """
        Executes a given SQL query with optional parameters.

        :param query: The SQL query to execute.
        :param params: The parameters to pass to the SQL query.
        :param fetchone: If True, fetch and return a single result.
        :param fetchall: If True, fetch and return all results.
        :return: The result of the query, or None if an error occurs.
        """
        connection = self.get_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, params)
                    if fetchone:
                        result = cursor.fetchone()
                    elif fetchall:
                        result = cursor.fetchall()
                    else:
                        result = None

                    # No commit here; only use it for transactions
                    self.logger.info(f"Query executed successfully: {query}")
                    return result

            except Error as e:
                self.logger.error(f"Error executing query: {e}")
                connection.rollback()
                return {"status": "error", "message": str(e)}
        else:
            return {"status": "error", "message": "No connection"}
            
    def _update_insert_printer_config(self, printer_data):        
        """
        Inserts or updates printer configuration in the database.
        """
        printer_id = printer_data.get('printer_id', 0) if printer_data.get('printer_id') is not None else 0
        brand = printer_data.get('printer_brand')
        model = printer_data.get('printer_model')
        name = printer_data.get('printer_name')
        power_consumption = printer_data.get('printer_power_consumption', 0.0)

        connection = self.get_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Check if the printer already exists
                    existing_printer_query = "SELECT printer_id FROM OctoPrint.Printer WHERE printer_id = %s"
                    existing_printer = self.execute_query(existing_printer_query, params=(printer_id), fetchone=True)

                    if existing_printer:
                        # Update existing printer
                        update_query = """
                            UPDATE OctoPrint.Printer
                            SET brand = %s, model = %s, name = %s, power_consumption = %s
                            WHERE printer_id = %s
                        """
                        params = (brand, model, name, power_consumption, printer_id)
                        self.execute_query(update_query, params=params)
                        self.logger.info(f"Updated Printer record with ID {printer_id}")
                    else:
                        # Insert new printer
                        insert_query = """
                            INSERT INTO OctoPrint.Printer (brand, model, name, power_consumption)
                            VALUES (%s, %s, %s, %s)
                        """
                        params = (brand, model, name, power_consumption)
                        self.execute_query(insert_query, params=params)

                        # Get the last inserted ID
                        last_id_query = "SELECT LAST_INSERT_ID()"
                        result = self.execute_query(last_id_query, fetchone=True)
                        printer_id = result[0] if result else None
                        self.logger.info(f"Inserted new Printer record with ID {printer_id}")

                connection.commit()

            except Error as e:
                self.logger.error(f"Error executing query: {e}")
                connection.rollback()
                return {"status": "error", "message": str(e)}
            finally:
                self.logger.info(f"Returning printer_id: {printer_id}")
                self.close_connection()
                return {"id": printer_id}
        else:
            return {"status": "error", "message": "No connection"}
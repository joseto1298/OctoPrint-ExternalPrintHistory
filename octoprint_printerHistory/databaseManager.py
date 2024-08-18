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
        The function `_set_connection_settings` sets the database connection settings based on the provided
        configuration.
        
        :param config: The `_set_connection_settings` method takes a `config` dictionary as input, which
        contains the following keys:
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
        The `_test_connection` function tests the database connection using the provided configuration
        parameters.
        
        :param config: The `_test_connection` method is used to test the database connection using the
        provided configuration parameters. The `config` parameter is a dictionary containing the following
        database connection details:
        :return: The `_test_connection` method returns a dictionary with two keys: "error" and "message".
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
            return {"error": False, "message": "Connection successful"}
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")
            return {"error": True, "message": str(e)}
        
    def get_connection(self):
        """
        The function `get_connection` establishes and returns a connection to a database using pymysql
        in Python.
        :return: The `get_connection` method returns either the established connection to the database
        if successful, or a dictionary with an error message if there was an issue with the database
        configuration or connecting to the database.
        """
        if not self.connection_settings:
            self.logger.error("Database configuration is not set.")
            return {"error": True, "message": "Database configuration is not set."}
        try:
            if self.connection is None or not self.connection.open:
                self.connection = pymysql.connect(**self.connection_settings)
                self.logger.info("Successfully connected to the database.")
            return self.connection
        except Error as e:
            self.logger.error(f"Error connecting to MySQL database: {e}")
            return {"error": True, "message": str(e)}

    def close_connection(self):
        """
        The `close_connection` function closes the database connection and logs the status.
        """
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed.")
            except Error as e:
                self.logger.error(f"Error closing database connection: {e}")

    def execute_query(self, query, params=None, fetchone=False, fetchall=False):
        """
        The function `execute_query` executes a SQL query with optional parameters and fetches either one
        or all results based on the specified flags.
        
        :param query: The `query` parameter in the `execute_query` method is a SQL query string that you
        want to execute against the database. It represents the SQL statement that you want to run, such
        as a SELECT, INSERT, UPDATE, or DELETE statement
        :param params: The `params` parameter in the `execute_query` method is used to pass any parameters
        that need to be substituted into the SQL query. These parameters can be used to make the query
        dynamic and prevent SQL injection attacks. When the query is executed, the parameters are
        substituted into the query in a safe
        :param fetchone: The `fetchone` parameter in the `execute_query` method is used to determine
        whether to fetch only one row of the query result. If `fetchone` is set to `True`, the method will
        fetch and return only the first row of the query result. If `fetchone` is, defaults to False
        (optional)
        :param fetchall: The `fetchall` parameter in the `execute_query` method is used to determine
        whether to fetch all the results of the query execution. If `fetchall` is set to `True`, the
        method will fetch all the results returned by the query. If `fetchall` is set to `, defaults to
        False (optional)
        :return: The `execute_query` method returns the result of the query execution based on the
        parameters `fetchone` and `fetchall`. If `fetchone` is set to True, it returns a single row as a
        tuple. If `fetchall` is set to True, it returns all rows as a list of tuples. If neither
        `fetchone` nor `fetchall` is set to True
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

                    self.logger.info(f"Query executed successfully: {query}")
                    return result

            except Error as e:
                self.logger.error(f"Error executing query: {e}")
                raise 

    def _update_insert_printer_config(self, printer_data):        
        """
        The function `_update_insert_printer_config` updates or inserts printer configuration data into
        a database based on the provided input.
        
        :param printer_data: The given code snippet is a method that updates or inserts printer
        configuration data into a database table. It first extracts the necessary information from the
        `printer_data` dictionary, such as `printer_id`, `power_consumption`, `purchase_price`,
        `estimated_lifespan`, `maintenance_costs`, `brand
        :return: The function `_update_insert_printer_config` returns a dictionary `result` which
        contains information about the operation performed. The dictionary may have keys such as "error"
        to indicate if there was an error during the operation, "printer_id" to provide the ID of the
        printer involved, "update" to indicate if an update was performed, and "insert" to indicate if a
        new record was inserted.
        """
        printer_id = printer_data.get('printer_id', 0)
        power_consumption = printer_data.get('printer_power_consumption', 0)
        purchase_price = printer_data.get('printer_purchase_price', 0) 
        estimated_lifespan = printer_data.get('printer_estimated_lifespan', 0)
        maintenance_costs = printer_data.get('printer_maintenance_costs', 0)
        brand = printer_data.get('printer_brand')
        model = printer_data.get('printer_model')
        name = printer_data.get('printer_name')
        
        connection = self.get_connection()
        if connection:
            try:
                with connection.cursor():
                    # Check if the printer already exists
                    existing_printer_query = f"""SELECT printer_id FROM {self.connection_settings['database']}.Printer WHERE printer_id = %s"""
                    existing_printer = self.execute_query(existing_printer_query, params=(printer_id), fetchone=True)

                    if existing_printer:
                        # Update existing printer
                        update_query = f"""
                            UPDATE {self.connection_settings['database']}.Printer
                            SET brand = %s, model = %s, name = %s, power_consumption = %s , purchase_price = %s, estimated_lifespan = %s, maintenance_costs = %s
                            WHERE printer_id = %s
                        """
                        params = (brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs, printer_id)
                        self.execute_query(update_query, params=params)
                        self.logger.info(f"Updated Printer record with ID {printer_id}")
                        result = {"error": False, "printer_id": printer_id, "update": True}
                    else:
                        # Insert new printer
                        insert_query = f"""
                            INSERT INTO {self.connection_settings['database']}.Printer (brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        params = (brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs)
                        self.execute_query(insert_query, params=params)

                        # Get the last inserted ID
                        last_id_query = "SELECT LAST_INSERT_ID()"
                        result = self.execute_query(last_id_query, fetchone=True)
                        printer_id = result[0] if result else None
                        self.logger.info(f"Inserted new Printer record with ID {printer_id}")
                        result = {"error": False, "printer_id": printer_id, "insert": True}
                
                connection.commit()

            except Error as e:
                connection.rollback()
                result = {"error": True, "message": str(e)}
            finally:
                self.logger.info(f"Returning printer_id: {printer_id}")
                self.close_connection()
                return result


    def _select_printer_config(self, id):
        """
        The function `_select_printer_config` selects and returns details of a printer configuration
        from a database based on the provided ID.
        
        :param id: The `id` parameter in the `_select_printer_config` method is used to specify the
        printer ID for which you want to fetch details from the database. If the `id` is provided, it
        will be used for fetching details of the corresponding printer. If `id` is `None`, then
        :return: The `_select_printer_config` method returns a dictionary containing information about a
        printer based on the provided printer ID. The returned dictionary has two possible structures:
        """
        printer_id = id if id is not None else 0

        connection = self.get_connection()
        if connection:
            try:
                with connection.cursor():
                    select_query = f"""
                        SELECT printer_id, brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs
                        FROM {self.connection_settings['database']}.Printer
                        WHERE printer_id = %s
                    """
                    # Execute query to fetch all details for the given printer_id
                    result = self.execute_query(select_query, params=(printer_id,), fetchone=True)

                    if result:
                        # Return all details as a dictionary
                        printer_data = {
                            "printer_id": result[0],
                            "brand": result[1],
                            "model": result[2],
                            "name": result[3],
                            "power_consumption": result[4],
                            "purchase_price": result[5],
                            "estimated_lifespan": result[6],
                            "maintenance_costs": result[7],
                        }
                        self.logger.info(f"Fetched Printer record with ID {printer_id}: {printer_data}")
                        result = {"error": False, "printer_data": printer_data}
                    else:
                        self.logger.info(f"No Printer record found with ID {printer_id}")
                        result = {"error": True, "message": "No printer found with the provided ID"}

                connection.commit()

            except Error as e:
                connection.rollback()
                result = {"error": True, "message": str(e)}
            finally:
                self.close_connection()
                return result



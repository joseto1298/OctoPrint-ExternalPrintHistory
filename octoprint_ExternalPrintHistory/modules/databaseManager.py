# coding=utf-8
from __future__ import absolute_import

import pymysql
from pymysql import MySQLError
from ..common.SettingsKeys import SettingsKeys

class DatabaseManager():
    def __init__(self):
        """
        Initializes the DatabaseManager class.

        This constructor initializes the DatabaseManager class, which is responsible for managing the database connection.

        Attributes:
            connection_settings (dict): A dictionary containing the configuration settings for the database connection.
        """
        self.connection_settings = None
        
    def set_and_test_connection(self, config):
        try:
            settings = {
                'host': config.get('db_host'),
                'user': config.get('db_user'),
                'password': config.get('db_password'),
                'database': config.get('db_database'),
                'port': int(config.get('db_port'))
            }
        
            # Attempt to connect to the database with the given settings
            with pymysql.connect(**settings) as connection:
                # Connection test successful
                
                self.connection_settings = settings
                
                self._settings.set([SettingsKeys.DB_HOST], config["db_host"])
                self._settings.set([SettingsKeys.DB_USER], config["db_user"])
                self._settings.set([SettingsKeys.DB_PASSWORD], config["db_password"])
                self._settings.set([SettingsKeys.DB_DATABASE], config["db_database"])
                self._settings.set([SettingsKeys.DB_PORT], config["db_port"])

                self._settings.save()
                
                return {"error": False, "message": "Connection successful - Database settings saved."}
        
        except KeyError as e:
            # Log error if a configuration key is missing
            self._logger.error("Missing configuration key: " + str(e))
            raise MySQLError("Error setting connection settings: Missing configuration key") from e
        
        except MySQLError as e:
            # Log error if a MySQL error is encountered
            self._logger.error("Error testing DB connection: " + str(e))
            return {"error": True, "message": str(e)}
        
        except Exception as e:
            # Log unexpected errors
            self._logger.error("Unexpected error during DB connection test: " + str(e))
            return {"error": True, "message": "An unexpected error occurred."}
    
    def _get_connection(self, result):        
        """
        Establishes a connection to the MySQL database using the configured settings.

        The connection settings are stored in the self.connection_settings dictionary.
        If the connection settings are not set, this method logs an error and
        returns a tuple containing None and a dictionary with an error message.

        Args:
            result (dict): A dictionary to store error information if the connection fails.

        Returns:
            tuple: A tuple containing the database connection object and the result dictionary.
                The connection object is None if the connection could not be established.
                The result dictionary contains an error message if the connection failed.
        """
        
        connection = None
        
        if not self.connection_settings:
            self._logger.error("Database configuration is not set.")
            result.update({"error": True, "message": "Database configuration is not set."})
        else:
            try:
                connection = pymysql.connect(**self.connection_settings)
                #self._logger.info("Database connection established.")
            except MySQLError as e:
                self._logger.error("Error connecting to MySQL database: " + str(e))
                result.update({"error": True, "message": "Error connecting to MySQL database"})
            except Exception as e:
                self._logger.error("Unexpected error connecting to MySQL database: " + str(e))
                result.update({"error": True, "message": "Error connecting to MySQL database"})
        
        return connection, result


    def close_connection(self, result, connection):
        """
        Closes the database connection and updates the result dictionary with any errors.

        This method attempts to close the provided database connection. If an error occurs
        during the closing process, it updates the result dictionary with the error details.
        If the connection is not open, it logs a warning.

        Args:
            result (dict): A dictionary to store error information if the connection closing fails.
            connection: The database connection object to be closed.

        Returns:
            dict: The updated result dictionary containing error information if any occur.
        """
        if connection:
            try:
                connection.close()
                # Log successful closure of the connection
                # self._logger.info("Database connection closed.")
            except MySQLError as e:
                # Log and update result if a MySQL error occurs
                self._logger.error("Error closing database connection: " + str(e))
                result.update({"error": True, "message": "Error closing database connection"})
            except Exception as e:
                # Log and update result if an unexpected error occurs
                self._logger.error("Unexpected error closing database connection: " + str(e))
                result.update({"error": True, "message": "Unexpected error closing database connection"})
        else:
            # Log a warning if there is no connection to close
            self._logger.warning("Attempted to close a connection that was not open.")
        
        return result
    
    """ 

    PRINTER TABLE

    """
    
    def update_insert_printer_config(self, printer_data, printer_id):
        """
        Updates or inserts a printer configuration in the database.

        This method retrieves a database connection and updates or inserts a printer
        configuration based on the given printer data and printer ID. If a printer ID is
        provided, it checks if the printer ID exists in the Printer table. If it does, it updates
        the configuration. If not, it inserts the configuration. If no printer ID is provided,
        it inserts the configuration.

        Args:
            printer_data (dict): The printer data to be updated/inserted in the database.
            printer_id (int): The ID of the printer to be updated/inserted.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary contains
                the following keys:

                - error (bool): True if an error occurred, False otherwise.
                - printer_id (int): The ID of the printer if an insert occurred.
                - insert (bool): True if an insert occurred, False otherwise.
                - update (bool): True if an update occurred, False otherwise.
        """
        result = {"error": False, "printer_id": printer_id, "insert": False, "update": False}
        
        connection, result = self._get_connection(result)
        if connection:
            try:
                with connection.cursor() as cursor:
                    if printer_id:
                        query = """
                            SELECT printer_id FROM Printer WHERE printer_id = %s
                        """
                        cursor.execute(query, (printer_id,))
                        if cursor.fetchone():
                            # Update the printer configuration if it already exists
                            update_fields = []
                            params = []

                            for field in ["printer_brand", "printer_model", "printer_name", "printer_power_consumption", 
                                        "printer_purchase_price", "printer_estimated_lifespan", "printer_maintenance_costs"]:
                                if field in printer_data:
                                    db_field = field.replace("printer_", "")
                                    update_fields.append(f"{db_field} = %s")
                                    params.append(printer_data[field])

                            if update_fields:
                                update_query = f"""
                                    UPDATE Printer
                                    SET {', '.join(update_fields)}
                                    WHERE printer_id = %s
                                """
                                params.append(printer_id)
                                cursor.execute(update_query, params)
                                result.update({"update": True})
                        else:
                            # Insert the printer configuration if it doesn't exist
                            result = self._insert_printer(cursor, printer_data)
                    else:
                        # Insert the printer configuration if no printer ID is provided
                        result = self._insert_printer(cursor, printer_data)
                    
                    connection.commit()
                        
            except MySQLError as e:
                connection.rollback()
                result.update({"error": True, "message": "Error updating/inserting printer configuration"})
                self._logger.error("Error updating/inserting printer configuration: " + str(e))
            except Exception as e:
                connection.rollback()
                result.update({"error": True, "message": "An unexpected error occurred"})
                self._logger.error("Unexpected error updating/inserting printer configuration: " + str(e))
            finally:
                result = self.close_connection(result, connection)
        
        return result

    def insert_printer(self, cursor, printer_data):
        """
        Inserts a new printer configuration.

        Args:
            cursor (cursor): A database cursor object.
            printer_data (dict): A dictionary containing the printer configuration data.

        Returns:
            dict: A dictionary containing information about the executed query.
                - error (bool): True if an error occurred, False otherwise.
                - printer_id (int): The ID of the printer if an insert occurred.
                - insert (bool): True if an insert occurred, False otherwise.
                - update (bool): True if an update occurred, False otherwise.
        """
        try:
            fields = []
            values = []
            params = []

            # Iterate over the possible fields and add them to the query
            for field in ["printer_brand", "printer_model", "printer_name", "printer_power_consumption", 
                        "printer_purchase_price", "printer_estimated_lifespan", "printer_maintenance_costs"]:
                if field in printer_data:
                    fields.append(field.replace("printer_", ""))
                    values.append("%s")
                    params.append(printer_data[field])

            if fields:
                query = f"""
                    INSERT INTO Printer ({', '.join(fields)})
                    VALUES ({', '.join(values)})
                """
                cursor.execute(query, params)
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                printer_id = result[0]
                #self._logger.info(f"Inserted new Printer record with ID {printer_id}")
                return {"error": False, "printer_id": printer_id, "insert": True, "update": False}
            else:
                raise ValueError("No data provided to insert printer record.")
        except MySQLError as e:
            self._logger.error("Error inserting printer record: " + str(e))
            raise
        except Exception as e:
            self._logger.error("Unexpected error inserting printer record: " + str(e))
            raise


    def select_printer(self, printer_id):
        """
        Selects the printer settings based on the provided printer ID.

        Args:
            printer_id (int): The ID of the printer to select.

        Returns:
            dict: A dictionary containing information about the executed query.
                - error (bool): True if an error occurred, False otherwise.
                - message (str): The error message if an error occurred, otherwise a success message.
                - printer_data (dict): A dictionary containing the printer configuration data if the query was successful.
        """
        result = {"error": True, "message": "Error selecting printer settings"}

        connection, result = self._get_connection(result)
        if connection:
            try:
                with connection.cursor() as cursor:
                    query = """
                        SELECT printer_id, brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs
                        FROM Printer
                        WHERE printer_id = %s
                    """
                    cursor.execute(query, (printer_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        printer_data = {
                            "printer_id": row[0],
                            "brand": row[1],
                            "model": row[2],
                            "name": row[3],
                            "power_consumption": row[4],
                            "purchase_price": row[5],
                            "estimated_lifespan": row[6],
                            "maintenance_costs": row[7],
                        }
                        result = {"error": False, "printer_data": printer_data}
                        #self._logger.info(f"Fetched Printer record with ID {printer_id}: {printer_data}")
                    else:
                        result = {"error": False, "message": "Printer data not found"}
                        #self._logger.info(result["message"])
                    
                connection.commit()
                
            except MySQLError as e:
                connection.rollback()
                result.update({"message": "Error selecting printer configuration"})
                self._logger.error("Error selecting printer configuration: " + str(e))
            except Exception as e:
                connection.rollback()
                result.update({"message": "An unexpected error occurred"})
                self._logger.error("Unexpected error selecting printer configuration: " + str(e))
            finally:
                result = self.close_connection(result, connection)
        
        return result

    """ 

    PRINT TABLE

    """

    def update_insert_print(self, print_data):
        """
        Updates or inserts a print configuration in the database.

        Args:
            print_data (dict): The print data to be updated/inserted in the database.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary contains
                the following keys:

                - error (bool): True if an error occurred, False otherwise.
                - print_id (int): The ID of the print if an insert occurred.
                - insert (bool): True if an insert occurred, False otherwise.
                - update (bool): True if an update occurred, False otherwise.
        """
        print_id = print_data.get("print_id")
        result = {"error": False, "print_id": print_id}
        connection, result = self._get_connection(result)
        if connection:
            try:
                with connection.cursor() as cursor:
                    if print_id:
                        query = "SELECT print_id FROM Print WHERE print_id = %s"
                        cursor.execute(query, (print_id,))
                        if cursor.fetchone():
                            # Update the print configuration if it already exists
                            set_clauses = []
                            params = []

                            for field in [
                                "printer_id", "spool_id", "name", "start_time", "end_time",
                                "estimated_time", "state", "thumbnail", "bed_temperature",
                                "chamber_temperature", "height","layers","total_height", "total_layers"
                            ]:
                                if field in print_data:
                                    set_clauses.append(f"{field} = %s")
                                    params.append(print_data[field])
                                    
                            if params:
                                update_query = f"UPDATE Print SET {', '.join(set_clauses)} WHERE print_id = %s"
                                params.append(print_id)
                                cursor.execute(update_query, params)
                        else:
                            # Insert the print configuration if it does not exist
                            result = self._insert_print(cursor, print_data)
                    else:
                        # Insert the print configuration without a print ID
                        result = self._insert_print(cursor, print_data)
                        
                    connection.commit()
                    
            except MySQLError as e:
                connection.rollback()
                result.update({"error": True, "message": "Error updating/inserting print configuration"})
                self._logger.error("Error updating/inserting print configuration: " + str(e))
            except Exception as e:
                connection.rollback()
                result.update({"error": True, "message": "An unexpected error occurred"})
                self._logger.error("Unexpected error updating/inserting print configuration: " + str(e))
            finally:
                result = self.close_connection(result, connection)
        
        return result

    def insert_print(self, cursor, print_data):
        """
        Inserts a new print configuration into the database.

        Args:
            cursor (cursor): A database cursor object.
            print_data (dict): A dictionary containing the print configuration data.

        Returns:
            dict: A dictionary containing information about the executed query.
                - error (bool): True if an error occurred, False otherwise.
                - print_id (int): The ID of the print if an insert occurred.

        Raises:
            ValueError: If no data is provided to insert a print record.
            Exception: If an unexpected error occurs during the operation.
        """
        try:
            # Initialize lists to store field names, value placeholders, and parameter values
            fields = []
            values = []
            params = []

            # Iterate over the possible fields and add them to the query if present in print_data
            for field in [
                    "printer_id", "spool_id", "name", "start_time", "end_time",
                    "estimated_time", "state", "thumbnail", "bed_temperature",
                    "chamber_temperature", "height", "layers", "total_height", "total_layers"
                    ]:
                if field in print_data:
                    fields.append(field)
                    values.append("%s")
                    params.append(print_data[field])

            if fields:
                # Construct and execute the SQL insert query
                query = f"""
                    INSERT INTO Print ({', '.join(fields)})
                    VALUES ({', '.join(values)})
                """
                cursor.execute(query, params)
                
                # Retrieve the last inserted ID to confirm the insertion
                cursor.execute("SELECT LAST_INSERT_ID()")
                result = cursor.fetchone()
                print_id = result[0]
                
                return {"error": False, "print_id": print_id}
            else:
                raise ValueError("No data provided to insert print record.")
        
        except MySQLError as e:
            self._logger.error("Error inserting print record: " + str(e))
            raise
        except Exception as e:
            self._logger.error("Unexpected error inserting print record: " + str(e))
            raise

    """ 

    SPOOL TABLE

    """

    def update_insert_spool(self, spool_data, print_id, tool_id):
        """
        Updates or inserts a spool configuration in the database.

        Args:
            spool_data (dict): A dictionary containing the spool configuration data.
            print_id (int): The ID of the print record this spool configuration belongs to.
            tool_id (int): The ID of the tool this spool configuration belongs to.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary contains
                the following keys:

                - error (bool): True if an error occurred, False otherwise.
                - message (str): An optional message describing the error.
        """
        result = {"error": False}

        connection, result = self._get_connection(result)
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Check if the spool configuration already exists
                    query = """
                        SELECT print_id, tool_id 
                        FROM Spool 
                        WHERE print_id = %s AND tool_id = %s
                    """
                    cursor.execute(query, (print_id, tool_id))

                    if cursor.fetchone():
                        # Update the spool configuration if it already exists
                        update_fields = []
                        params = []

                        for field in ["spool_id", "extrusionLength", "weight", "cost", 
                                    "name", "material", "colorHex", "temperature"]:
                            if field in spool_data:
                                update_fields.append(f"{field} = %s")
                                params.append(spool_data[field])

                        if update_fields:
                            update_query = f"""
                                UPDATE Spool
                                SET {', '.join(update_fields)}
                                WHERE print_id = %s AND tool_id = %s
                            """
                            params.extend([print_id, tool_id])
                            cursor.execute(update_query, params)
                    else:
                        # Insert the spool configuration if it does not exist
                        result = self._insert_spool(cursor, spool_data, print_id, tool_id)

                    connection.commit()

            except MySQLError as e:
                connection.rollback()
                result.update({"error": True, "message": "Error updating/inserting spool configuration"})
                self._logger.error("Error updating/inserting spool configuration: " + str(e))
            except Exception as e:
                connection.rollback()
                result.update({"error": True, "message": "An unexpected error occurred"})
                self._logger.error("Unexpected error updating/inserting spool configuration: " + str(e))
            finally:
                result = self.close_connection(result, connection)

        return result

    def insert_spool(self, cursor, spool_data, print_id, tool_id):
        """
        Inserts a new spool configuration into the database.

        Args:
            cursor (cursor): A database cursor object.
            spool_data (dict): A dictionary containing the spool configuration data.
            print_id (int): The ID of the print record this spool configuration belongs to.
            tool_id (int): The ID of the tool this spool configuration belongs to.

        Returns:
            dict: A dictionary containing the result of the operation. The dictionary contains
                the following keys:

                - error (bool): True if an error occurred, False otherwise.
        """
        try:
            # Construct the field names and placeholders for the query
            fields = ["print_id", "tool_id", "spool_id", "extrusionLength", "weight", "cost", 
                    "name", "material", "colorHex", "temperature"]
            params = [print_id, tool_id]
            values = ["%s", "%s"]

            # Iterate over the possible fields and add them to the query if present in spool_data
            for field in fields[2:]:
                if field in spool_data:
                    values.append("%s")
                    params.append(spool_data[field])

            if len(values) != len(params):
                raise ValueError("Mismatch between placeholders and parameters.")

            # Construct and execute the SQL insert query
            query = f"""
                INSERT INTO Spool ({', '.join(fields)})
                VALUES ({', '.join(values)})
            """
            cursor.execute(query, params)
            return {"error": False}

        except MySQLError as e:
            self._logger.error(f"Error inserting spool record: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Unexpected error inserting spool record: {e}")
            raise
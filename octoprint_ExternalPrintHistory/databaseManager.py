import pymysql
from pymysql import MySQLError

class DatabaseManager:
    def __init__(self, plugin,logger):
        self.logger = logger 
        self.plugin = plugin
        self.connection_settings = None
        self.connection = None

    def _set_and_test_connection(self, config):
        try:
            self.connection_settings = {
                'host': config.get('db_host'),
                'user': config.get('db_user'),
                'password': config.get('db_password'),
                'database': config.get('db_database'),
                'port': int(config.get('db_port'))
            }
            with pymysql.connect(**self.connection_settings) as connection:
                #self.logger.info("Database connection test successful.")
                return {"error": False, "message": "Connection successful"}
        except KeyError as e:
            self.logger.error("Missing configuration key: " + str(e))
            raise MySQLError("Error setting connection settings: Missing configuration key") from e
        except MySQLError as e:
            self.logger.error("Error testing DB connection: " + str(e))
            return {"error": True, "message": str(e)}
        except Exception as e:
            self.logger.error("Unexpected error during DB connection test: " + str(e))
            return {"error": True, "message": "An unexpected error occurred: " + str(e)}
    
    def get_connection(self):
            if not self.connection_settings:
                self.logger.error("Database configuration is not set.")
                raise MySQLError("Database configuration is not set.")
            
            if self.connection is None or not self.connection.open:
                try:
                    self.connection = pymysql.connect(**self.connection_settings)
                    #self.logger.info("Database connection established.")
                except MySQLError as e:
                    self.logger.error("Error connecting to MySQL database: " + str(e))
                    raise
                except Exception as e:
                    self.logger.error("Unexpected error connecting to MySQL database: " + str(e))
                    raise
            
            return self.connection

    def close_connection(self, result):
        """
        Close the database connection and update the result with any errors.
        """
        if self.connection:
            try:
                self.connection.close()
                #self.logger.info("Database connection closed.")
            except MySQLError as e:
                self.logger.error("Error closing database connection: " + str(e))
                result.update({"error": True, "message": "Error closing database connection: " + str(e)})
            except Exception as e:
                self.logger.error("Unexpected error closing database connection: " + str(e))
                result.update({"error": True, "message": "Unexpected error closing database connection: " + str(e)})
            finally:
                self.connection = None
        else:
            self.logger.warning("Attempted to close a connection that was not open.")
        
        return result

    def _update_insert_printer_config(self, printer_data, printer_id):
        #self.logger.info(f"Updating or inserting Printer record with ID {printer_id}")
        params = (
            printer_data.get('printer_brand'),
            printer_data.get('printer_model'),
            printer_data.get('printer_name'),
            printer_data.get('printer_power_consumption', 0),
            printer_data.get('printer_purchase_price', 0),
            printer_data.get('printer_estimated_lifespan', 0),
            printer_data.get('printer_maintenance_costs', 0),
        )
        
        result = {"error": False, "printer_id": printer_id, "insert": False, "update": False}

        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                if printer_id:
                    query = """
                        SELECT printer_id FROM Printer WHERE printer_id = %s
                    """
                    cursor.execute(query, (printer_id,))
                    if cursor.fetchone():
                        update_query = """
                            UPDATE Printer
                            SET brand = %s, model = %s, name = %s, power_consumption = %s, purchase_price = %s, 
                                estimated_lifespan = %s, maintenance_costs = %s
                            WHERE printer_id = %s
                        """
                        cursor.execute(update_query, (*params, printer_id))
                        result.update({"update": True})
                        #self.logger.info(f"Updated Printer record with ID {printer_id}")
                    else:
                        result = self._insert_printer(cursor, params)
                else:
                    result = self._insert_printer(cursor, params)
                
                connection.commit()
        except MySQLError as e:
            connection.rollback()
            result.update({"error": True, "message": str(e)})
            self.logger.error("Error updating/inserting printer configuration: " + str(e))
        except Exception as e:
            connection.rollback()
            result.update({"error": True, "message": "An unexpected error occurred: " + str(e)})
            self.logger.error("Unexpected error updating/inserting printer configuration: " + str(e))
        finally:
            result = self.close_connection(result)
        
        return result
    
    def _insert_printer(self, cursor, params):
        try:
            query = """
                INSERT INTO Printer (brand, model, name, power_consumption, purchase_price, estimated_lifespan, maintenance_costs)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, params)
            cursor.execute("SELECT LAST_INSERT_ID()")
            result = cursor.fetchone()
            printer_id = result[0]
            #self.logger.info(f"Inserted new Printer record with ID {printer_id}")
            return {"error": False, "printer_id": printer_id, "insert": True, "update": False}
        except MySQLError as e:
            self.logger.error("Error inserting printer record: " + str(e))
            raise
        except Exception as e:
            self.logger.error("Unexpected error inserting printer record: " + str(e))
            raise

    def _select_Printer(self, printer_id):
        result = {"error": True, "message": "Error selecting printer settings"}
        
        try:
            connection = self.get_connection()
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
                    #self.logger.info(f"Fetched Printer record with ID {printer_id}: {printer_data}")
                else:
                    result = {"error": False, "message": "Printer data not found"}
                    #self.logger.info(result["message"])
                
            connection.commit()
        except MySQLError as e:
            connection.rollback()
            result.update({"message": str(e)})
            self.logger.error("Error selecting printer configuration: " + str(e))
        except Exception as e:
            connection.rollback()
            result.update({"message": "An unexpected error occurred: " + str(e)})
            self.logger.error("Unexpected error selecting printer configuration: " + str(e))
        finally:
            result = self.close_connection(result)
        
        return result

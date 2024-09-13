# coding=utf-8
from __future__ import absolute_import

class SettingsKeys:

    # Plugin parameters
    PLUGIN_PREHEAT = { "key": "preheat", "minVersion": "0.4.0"}
    PLUGIN_DISPLAY_LAYER_PROGRESS = { "key": "DisplayLayerProgress", "minVersion": "1.26.0"}
    PLUGIN_ULTIMAKER_FORMAT_PACKAGE = { "key": "UltimakerFormatPackage", "minVersion": "1.0.0"}
    PLUGIN_PRUSA_SLICER_THUMNAIL = { "key": "prusaslicerthumbnails", "minVersion": "1.0.0"}    
    
    #Plugin check
    PLUGIN_DEPENDENCY_CHECK ="plugin_dependency_check"
    
    # Printer parameters
    #PRINTER_NAME = "printer_name"
    #PRINTER_MODEL = "printer_model"
    #PRINTER_BRAND = "printer_brand"
    #PRINTER_POWER_CONSUMPTION = "printer_power_consumption"
    #PRINTER_PURCHASE_PRICE = "printer_purchase_price"
    #PRINTER_ESTIMATED_LIFESPAN = "printer_estimated_lifespan"
    #PRINTER_MAINTENANCE_COSTS = "printer_maintenance_costs"
    PRINTER_ID = "printer_id"
    
    # Database parameters
    DB_USER = "db_user"
    DB_PASSWORD = "db_password"
    DB_HOST = "db_host"
    DB_PORT = "db_port"
    DB_DATABASE = "db_database"

    # Currency and electricity cost
    CURRENCY = "currency"
    ELECTRICITY_COST = "electricity_cost"


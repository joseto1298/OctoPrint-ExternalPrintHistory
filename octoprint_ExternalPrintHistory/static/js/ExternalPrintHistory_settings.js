$(function () {
    function ExternalPrintHistorySettings(parameters) {
        var self = this;
        var apiUrl = BASEURL + "plugin/ExternalPrintHistory";

        self.settingsViewModel = parameters[0];

        self.connection_Status = ko.observable("");
        self.db_readonly = ko.observable(false);
        self.db_isloading = ko.observable(false);

        self.data_status = ko.observable("");
        self.data_readonly = ko.observable(true);
        self.data_isloading = ko.observable(false);

        self.clearConnectionStatusTimer = null;
        self.clearDataStatusTimer = null;

        self.testDbConnection = function () {
            self.connection_Status("");

            const db_user = $("#db_user").val();
            const db_password = $("#db_password").val();
            const db_host = $("#db_host").val();
            const db_port = $("#db_port").val();
            const db_database = $("#db_database").val();

            if (
                !db_user ||
                !db_password ||
                !db_host ||
                !db_port ||
                !db_database
            ) {
                self.connection_Status("All fields are required");
                return;
            }

            const settings = {
                db_user: db_user,
                db_password: db_password,
                db_host: db_host,
                db_port: db_port,
                db_database: db_database,
            };

            self.db_readonly(true);
            self.db_isloading(true);

            $.ajax({
                url: apiUrl + "/testdbconnection",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
            })
                .done(function (response) {
                    if (response.error == false) {
                        self.connection_Status(
                            "Connection successful - Database settings saved."
                        );
                    } else {
                        self.connection_Status(
                            "Connection failed: " + response.message
                        );
                    }
                })
                .fail(function (xhr) {
                    var errorMessage = "";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    self.connection_Status("Connection failed");
                    console.error(errorMessage);
                })
                .always(function () {
                    self.db_readonly(false);
                    self.db_isloading(false);
                    self.startClearConnectionStatusTimer();
                });
        };

        self.selectPrinter = function () {
            self.data_isloading(true);
            self.data_readonly(true);
            self.data_status("");

            $.ajax({
                url: apiUrl + "/selectPrinter",
                type: "GET",
                contentType: "application/json",
            })
                .done(function (response) {
                    if (response.error == false) {
                        if (response.printer_data) {
                            $("#printer_name").val(response.printer_data.name);
                            $("#printer_model").val(
                                response.printer_data.model
                            );
                            $("#printer_brand").val(
                                response.printer_data.brand
                            );
                            $("#printer_power_consumption").val(
                                response.printer_data.power_consumption
                            );
                            $("#printer_purchase_price").val(
                                response.printer_data.purchase_price
                            );
                            $("#printer_estimated_lifespan").val(
                                response.printer_data.estimated_lifespan
                            );
                            $("#printer_maintenance_costs").val(
                                response.printer_data.maintenance_costs
                            );
                            self.data_status("Data loaded successfully");
                            self.data_readonly(false);
                        } else {
                            self.data_status("Printer data not found");
                            self.data_readonly(true);
                        }
                    } else {
                        self.data_status("Connection failed");
                        console.error(response.message);
                    }
                })
                .fail(function (xhr) {
                    var errorMessage = "";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    self.data_status("Connection failed");
                    console.error(errorMessage);
                })
                .always(function () {
                    self.data_isloading(false);
                    self.startClearDataStatusTimer();
                });
        };

        self.startClearConnectionStatusTimer = function () {
            if (self.clearConnectionStatusTimer) {
                clearTimeout(self.clearConnectionStatusTimer);
            }
            self.clearConnectionStatusTimer = setTimeout(function () {
                self.connection_Status("");
            }, 8000);
        };

        self.startClearDataStatusTimer = function () {
            if (self.clearDataStatusTimer) {
                clearTimeout(self.clearDataStatusTimer);
            }
            self.clearDataStatusTimer = setTimeout(function () {
                self.data_status("");
            }, 8000);
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExternalPrintHistorySettings,
        dependencies: ["settingsViewModel"],
        elements: ["#ExternalPrintHistory-settings"],
    });
});

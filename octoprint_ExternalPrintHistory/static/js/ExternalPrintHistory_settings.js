$(function () {
    function ExternalPrintHistorySettings(parameters) {
        var self = this;
        self.api = new ExternalPrintHistoryApiRest();
        self.settingsViewModel = parameters[0];

        self.printerStatus = ko.observable("");
        self.connection_Status = ko.observable("");

        self.testDbConnection = function () {
            const settings = {
                db_user: $("#db_user").val(),
                db_password: $("#db_password").val(),
                db_host: $("#db_host").val(),
                db_port: $("#db_port").val(),
                db_database: $("#db_database").val(),
            };

            if (
                !settings.db_user ||
                !settings.db_password ||
                !settings.db_host ||
                !settings.db_port ||
                !settings.db_database
            ) {
                $("#connection_Status").text("All fields are required");
                return;
            }
            self.statusInputDatabase(true);
            self.toggleSpinner("spinner_test_connection", true);
            $("#test_connection").prop("disabled", true);
            self.api
                .testDbConnection(settings)
                .then((response) => {
                    //console.log(response);
                    if (response.error == false) {
                        $("#connection_Status").text("Connection successful");
                    } else {
                        $("#connection_Status").text(
                            "Connection failed: " + response.message
                        );
                    }
                })
                .catch((error) => {
                    $("#connection_Status").text("Connection failed: " + error);
                })
                .finally(() => {
                    $("#test_connection").prop("disabled", false);
                    self.statusInputDatabase(false);
                    self.toggleSpinner("spinner_test_connection", false);
                });
        };

        self.selectPrinter = function () {
            self.statusInputPrinter(true);
            self.toggleSpinner("spinner_printer_data", true);
            $("#data_Printer").prop("disabled", true);
            self.api
                .selectPrinter({})
                .then((response) => {
                    //console.log(response);
                    if (response.error == false) {
                        self.statusInputPrinter(false);
                        if (response.printer_data) {
                            $("#printerStatus").text(
                                "Data loaded successfully"
                            );
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
                        } else {
                            $("#printerStatus").text("Printer data  not found");
                        }
                        $("#data_Printer").prop("disabled", false);
                    } else {
                        $("#printerStatus").text(
                            "Connection failed: " + response.message
                        );
                    }
                })
                .catch((error) => {
                    $("#printerStatus").text("Connection failed: " + error);
                })
                .finally(() => {
                    $("#data_Printer").prop("disabled", false);
                    self.toggleSpinner("spinner_printer_data", false);
                });
        };

        self.statusInputDatabase = function (status) {
            $("#db_user").prop("readonly", status);
            $("#db_password").prop("readonly", status);
            $("#db_host").prop("readonly", status);
            $("#db_port").prop("readonly", status);
            $("#db_database").prop("readonly", status);
        };

        self.statusInputPrinter = function (status) {
            $("#printer_name").prop("readonly", status);
            $("#printer_model").prop("readonly", status);
            $("#printer_brand").prop("readonly", status);
            $("#printer_power_consumption").prop("readonly", status);
            $("#printer_purchase_price").prop("readonly", status);
            $("#printer_estimated_lifespan").prop("readonly", status);
            $("#printer_maintenance_costs").prop("readonly", status);
        };

        self.toggleSpinner = function (spinnerId, show) {
            if (show) {
                $("#" + spinnerId).removeClass("hidden");
            } else {
                $("#" + spinnerId).addClass("hidden");
            }
        };

        $("#databaseSettingsTab").on("blur", function () {
            $("#connection_Status").text("");
        });

        $("#printerDataTab").on("blur", function () {
            $("#printerStatus").text("");
            self.statusInputPrinter(true);
        });

        $("#data_Printer").click(self.selectPrinter);
        $("#test_connection").click(self.testDbConnection);
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExternalPrintHistorySettings,
        dependencies: ["settingsViewModel"],
        elements: ["#ExternalPrintHistory-settings"],
    });
});

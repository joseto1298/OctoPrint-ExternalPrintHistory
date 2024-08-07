$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        self.settingsViewModel = parameters[0];

        self.connectionStatus = ko.observable(" ");
        self.printerStatus = ko.observable(" ");

        function showMessage(observable, message, timeout = 7000) {
            observable(message);
            setTimeout(function () {
                observable("  ");
            }, timeout);
        }

        self.testDbConnection = function () {
            var settings = {
                db_user: $("#db_user").val(),
                db_password: $("#db_password").val(),
                db_host: $("#db_host").val(),
                db_port: $("#db_port").val(),
                db_database: $("#db_database").val(),
            };

            $.ajax({
                url: BASEURL + "plugin/printerHistory/testdbconnection",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (!response.error) {
                        //console.log("Database connection successful");
                        showMessage(
                            self.connectionStatus,
                            "Connection successful - Changes saved"
                        );
                        self.selectprinter();
                    } else {
                        console.error(
                            "Database connection failed: " + response.message
                        );
                        showMessage(
                            self.connectionStatus,
                            "Connection failed: " + response.message
                        );
                        setFieldsReadOnly(true);
                    }
                },
                error: function (xhr) {
                    var errorMessage = "Error testing connection";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }

                    console.error(
                        "Error testing database connection:",
                        errorMessage
                    );
                    showMessage(
                        self.connectionStatus,
                        "Error testing connection: " + errorMessage
                    );
                    setFieldsReadOnly(true);
                },
            });
        };

        self.updateprinterconfig = function () {
            var settings = {
                printer_id: $("#printer_id").val(),
                printer_name: $("#printer_name").val(),
                printer_model: $("#printer_model").val(),
                printer_brand: $("#printer_brand").val(),
                printer_power_consumption: $(
                    "#printer_power_consumption"
                ).val(),
            };

            $.ajax({
                url: BASEURL + "plugin/printerHistory/updateprinterconfig",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (!response.error) {
                        //console.log("Updated data on the printer");
                        showMessage(
                            self.printerStatus,
                            "Updated data on the printer"
                        );
                    } else {
                        console.error(
                            "Failure to update data: " + response.message
                        );
                        showMessage(
                            self.printerStatus,
                            "Failure to update data: " + response.message
                        );
                    }
                },
                error: function (xhr) {
                    var errorMessage = "Failure to update data";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }

                    console.error("Failure to update data:", errorMessage);
                    showMessage(
                        self.printerStatus,
                        "Failure to update data: " + errorMessage
                    );
                },
            });
        };

        self.selectprinter = function () {
            var settings = {
                printer_id: $("#printer_id").val(),
            };

            $.ajax({
                url: BASEURL + "plugin/printerHistory/selectprinterconfig",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (!response.error) {
                        //console.log("Printer data obtained");
                        showMessage(
                            self.printerStatus,
                            "Printer data obtained"
                        );
                        if (response.printer_data) {
                            $("#printer_id").val(
                                response.printer_data.printer_id
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
                        }
                    } else {
                        console.error(
                            "Failed to get data from printer: " +
                                response.message
                        );
                        showMessage(
                            self.printerStatus,
                            "Failed to get data from printer: " +
                                response.message
                        );
                        $("#printer_name").val("");
                        $("#printer_model").val("");
                        $("#printer_brand").val("");
                        $("#printer_power_consumption").val("");
                    }
                    setFieldsReadOnly(false);
                },
                error: function (xhr) {
                    var errorMessage = "Failed to get data from printer";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }

                    console.error(
                        "Failed to get data from printer:",
                        errorMessage
                    );
                    showMessage(
                        self.printerStatus,
                        "Failed to get data from printer: " + errorMessage
                    );
                    setFieldsReadOnly(false);
                    $("#printer_name").val("");
                    $("#printer_model").val("");
                    $("#printer_brand").val("");
                    $("#printer_power_consumption").val("");
                },
            });
        };

        function setFieldsReadOnly(status) {
            $("#printer_name").prop("readonly", status);
            $("#printer_model").prop("readonly", status);
            $("#printer_brand").prop("readonly", status);
            $("#printer_power_consumption").prop("readonly", status);
            $("#printerUpdate").prop("disabled", status);
        }

        $("#test_connection").click(self.testDbConnection);
        $("#printerUpdate").click(self.updateprinterconfig);
    }

    // Registrar el ViewModel con Knockout
    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        var urlApi = BASEURL + "plugin/printerHistory";

        self.settingsViewModel = parameters[0];

       /* The above code is defining two Knockout observables `connectionStatus` and `printerStatus`
       with initial values. These observables are being used to track the status of the connection
       and printer, respectively. The initial values indicate that changes to these statuses should
       be made using the "Save Changes" button. */
        self.connectionStatus = ko.observable(
            "Changes are made using the Save Changes Button."
        );
        self.printerStatus = ko.observable(
            "Changes are made using the Save Changes Button."
        );

      /**
       * The function `showMessage` updates an observable with a message and then updates it again
       * after a specified timeout.
       * @param observable - The `observable` parameter in the `showMessage` function is a function
       * that will be called with the `message` parameter and a default message after a specified
       * `timeout`.
       * @param message - The `message` parameter in the `showMessage` function is the message that
       * will be displayed using the `observable` function.
       * @param [timeout=10000] - The `timeout` parameter in the `showMessage` function is used to
       * specify the duration (in milliseconds) after which a default message will be displayed if no
       * other message is provided. In this case, if no message is provided within the specified
       * `timeout` duration, the message "Changes are made
       */
        function showMessage(observable, message, timeout = 10000) {
            observable(message);
            setTimeout(function () {
                observable("Changes are made using the Save Changes Button.");
            }, timeout);
        }

        /* The above code defines a function `testDbConnection` that sends an AJAX request to test a
        database connection. It collects database connection settings from input fields on a form,
        sends them to a specified API endpoint using a PUT request, and expects a JSON response. */
        self.testDbConnection = function () {
            var settings = {
                db_user: $("#db_user").val(),
                db_password: $("#db_password").val(),
                db_host: $("#db_host").val(),
                db_port: $("#db_port").val(),
                db_database: $("#db_database").val(),
            };

            $.ajax({
                url: urlApi + "/testdbconnection",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                /**
                 * Handles the successful response from the database connection test.
                 * Updates the connection status and selects the printer if the connection is successful.
                 * Otherwise, logs the error and updates the connection status with the error message.
                 *
                 * @param {object} response - The response object from the database connection test.
                 * @return {undefined}
                 */
                success: function (response) {
                    if (!response.error) {
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
                /**
                 * Handles errors that occur during database connection testing.
                 *
                 * @param {object} xhr - The XMLHttpRequest object containing error information.
                 * @return {undefined}
                 */
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

        /* The above JavaScript code defines a function `updateprinterconfig` that sends an AJAX
        request to update printer configuration data to a specified API endpoint. */
        self.updateprinterconfig = function () {
            var settings = {
                printer_id: $("#printer_id").val(),
                printer_name: $("#printer_name").val(),
                printer_model: $("#printer_model").val(),
                printer_brand: $("#printer_brand").val(),
                printer_power_consumption: $(
                    "#printer_power_consumption"
                ).val(),
                printer_purchase_price: $("#printer_purchase_price").val(),
                printer_estimated_lifespan: $(
                    "#printer_estimated_lifespan"
                ).val(),
                printer_maintenance_costs: $(
                    "#printer_maintenance_costs"
                ).val(),
            };

            $.ajax({
                url: urlApi + "/updateprinterconfig",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                /**
                 * Handles a successful response from the update printer configuration request.
                 *
                 * @param {object} response - The server response containing the updated printer configuration data.
                 * @return {undefined}
                 */
                success: function (response) {
                    if (!response.error) {
                        showMessage(
                            self.printerStatus,
                            "Updated data on the printer"
                        );
                        $("#printer_id").val(response.printer_id);
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
                /**
                 * Handles errors that occur during the update printer configuration process.
                 *
                 * @param {object} xhr - The XMLHttpRequest object containing error information.
                 * @return {undefined}
                 */
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

        /* The above JavaScript code defines a function `selectprinter` that makes an AJAX request to a
        specified API endpoint `/selectprinterconfig` using the HTTP method PUT. The function sends
        a JSON object `settings` containing the value of an input field with id `printer_id`. */
        self.selectprinter = function () {
            var settings = {
                printer_id: $("#printer_id").val(),
            };

            $.ajax({
                url: urlApi + "/selectprinterconfig",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (!response.error) {
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
                            $("#printer_purchase_price").val(
                                response.printer_data.purchase_price
                            );
                            $("#printer_estimated_lifespan").val(
                                response.printer_data.printer_estimated_lifespan
                            );
                            $("#printer_maintenance_costs").val(
                                response.printer_data.maintenance_costs
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
                    }
                    setDefaultValues();
                    setFieldsReadOnly(false);
                },
                /**
                 * Handles errors that occur during the retrieval of data from a printer.
                 *
                 * @param {object} xhr - The XMLHttpRequest object containing error information.
                 * @return {undefined}
                 */
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
                    setDefaultValues();
                    setFieldsReadOnly(false);
                },
            });
        };

        /* The above JavaScript code defines a function `saveInputData` that is responsible for saving
        input data related to electricity cost and currency to a server using an AJAX request. */
        self.saveInputData = function () {
            var electricityCost = $("#electricity_cost").val();
            var currency = $("#currency").val();

            var settings = {
                electricity_cost: electricityCost,
                currency: currency,
            };

            $.ajax({
                url: urlApi + "/saveData",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (response.error) {
                        console.error("Error saving data: " + response.message);
                    }
                },
            /**
             * Handles errors that occur during the save data process.
             *
             * @param {object} xhr - The XMLHttpRequest object containing error information.
             * @return {undefined}
             */
                error: function (xhr) {
                    var errorMessage = "Error saving data";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    console.error("Error saving data:", errorMessage);
                },
            });
        };

        /**
         * The function `setFieldsReadOnly` sets the readonly property and disabled attribute of
         * specified input fields based on the provided status.
         * @param status - The `status` parameter in the `setFieldsReadOnly` function is a boolean
         * value that determines whether the form fields and the update button should be set to
         * read-only/disabled (`true`) or editable/enabled (`false`).
         */
        function setFieldsReadOnly(status) {
            $("#printer_name").prop("readonly", status);
            $("#printer_model").prop("readonly", status);
            $("#printer_brand").prop("readonly", status);
            $("#printer_power_consumption").prop("readonly", status);
            $("#printer_purchase_price").prop("readonly", status);
            $("#printer_estimated_lifespan").prop("readonly", status);
            $("#printer_maintenance_costs").prop("readonly", status);

            $("#printerUpdate").prop("disabled", status);
        }

       /**
        * The function `setDefaultValues` sets default values for specified input fields if they are
        * empty or null.
        */
        function setDefaultValues() {
            var defaults = {
                "#printer_id": 0,
                "#printer_power_consumption": 0.0,
                "#printer_purchase_price": 0.0,
                "#printer_estimated_lifespan": 0,
                "#printer_maintenance_costs": 0.0,
            };

            $.each(defaults, function (selector, defaultValue) {
                var input = $(selector);
                if (input.val() === "" || input.val() === null) {
                    input.val(defaultValue);
                }
            });
        }


        /* The above code is written in JavaScript and it seems to be setting up event listeners for two
        different elements in the HTML document. */
        $("#test_connection").click(self.testDbConnection);
        $("#printerUpdate").click(self.updateprinterconfig);

        /* The above JavaScript code is setting up an event listener for the "blur" event on the elements with
        IDs "electricity_cost" and "currency". When either of these elements loses focus, the function
        `self.saveInputData()` will be called. */
        $("#electricity_cost, #currency").on("blur", function () {
            self.saveInputData();
        });
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#PrinterhistoryPlugin_settings"],
    });
});

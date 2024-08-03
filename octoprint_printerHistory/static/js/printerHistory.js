$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        self.settingsViewModel = parameters[0];

        // Observables para el estado de la conexión
        self.connectionStatus = ko.observable("");
        self.isDbConnected = ko.observable(false);

        // Función para probar la conexión a la base de datos
        self.testDbConnection = function () {
            var settings = {
                db_user: $("#db_user").val(),
                db_password: $("#db_password").val(),
                db_host: $("#db_host").val(),
                db_port: $("#db_port").val(),
                db_database: $("#db_database").val(),
            };

            $.ajax({
                url: BASEURL + "plugin/PrinterhistoryPlugin/testdbconnection",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(settings),
                success: function (response) {
                    if (response.success) {
                        console.log("Database connection successful");
                        self.connectionStatus("Connection successful");
                    } else {
                        console.log(
                            "Database connection failed: " + response.message
                        );
                        self.connectionStatus(
                            "Connection failed: " + response.message
                        );
                    }
                },
                error: function (xhr, status, error) {
                    // Obtén un mensaje de error más detallado
                    var errorMessage = "Error testing connection";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }

                    console.error("Error testing database connection:", error);
                    self.connectionStatus(
                        "Error testing connection: " + errorMessage
                    );
                    self.isDbConnected(false);
                },
            });
        };

        // Enlazar la función de prueba de conexión al evento de clic del botón
        $("#test_connection").click(self.testDbConnection);
    }

    // Registrar el ViewModel con Knockout
    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

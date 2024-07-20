// printerHistory.js

$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;

        self.global_settings = parameters[0];

        // Observables for form fields
        self.user = ko.observable("");
        self.password = ko.observable("");
        self.host = ko.observable("");
        self.port = ko.observable(0);
        self.database = ko.observable("");

        // Load settings from the config.json
        self.loadSettings = function () {
            OctoPrint.settings
                .getPluginSettings("printerhistory")
                .done(function (data) {
                    if (data && data.length > 0 && data[0].database) {
                        self.user(data[0].database.user);
                        self.password(data[0].database.password);
                        self.host(data[0].database.host);
                        self.port(data[0].database.port);
                        self.database(data[0].database.database);
                    } else {
                        console.warn(
                            "No se encontraron configuraciones de base de datos."
                        );
                    }
                })
                .fail(function () {
                    console.error("Error al cargar las configuraciones.");
                });
        };

        // Save settings to the config.json
        self.saveSettings = function () {
            var settings = [
                {
                    database: {
                        user: self.user(),
                        password: self.password(),
                        host: self.host(),
                        port: self.port(),
                        database: self.database(),
                    },
                },
            ];
            OctoPrint.settings
                .savePluginSettings("printerhistory", settings)
                .done(function () {
                    console.log("Configuraciones guardadas correctamente.");
                })
                .fail(function () {
                    console.error("Error al guardar las configuraciones.");
                });
        };

        // Initial load
        self.loadSettings();
    }

    // Bind the ViewModel to the DOM element with the ID "printerhistory"
    var printerHistoryViewModel = new PrinterHistoryViewModel();
    ko.applyBindings(
        printerHistoryViewModel,
        document.getElementById("printerhistory")
    );
});

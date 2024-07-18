$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;

        self.user = ko.observable("");
        self.password = ko.observable("");
        self.host = ko.observable("");
        self.port = ko.observable("");
        self.database = ko.observable("");

        self.loadSettings = function () {
            var settings = parameters[0];
            if (
                settings &&
                settings.settings &&
                settings.settings.plugins &&
                settings.settings.plugins.printerhistory
            ) {
                var dbSettings =
                    settings.settings.plugins.printerhistory.databaseSettings ||
                    {};
                self.user(dbSettings.user || "");
                self.password(dbSettings.password || "");
                self.host(dbSettings.host || "");
                self.port(dbSettings.port || "");
                self.database(dbSettings.database || "");
            } else {
                console.warn(
                    "No se encontraron configuraciones de base de datos."
                );
            }
        };

        self.saveDatabaseSettings = function () {
            var settings = {
                user: self.user(),
                password: self.password(),
                host: self.host(),
                port: self.port(),
                database: self.database(),
            };
            OctoPrint.settings
                .savePluginSettings("printerhistory", {
                    databaseSettings: settings,
                })
                .done(function () {
                    console.info("Configuraciones de base de datos guardadas.");
                });
        };

        self.loadSettings();
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

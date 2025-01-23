$(() => {
    function ExternalPrintHistorySidebarViewModel(params) {
        var self = this;
        var apiUrl = BASEURL + "plugin/ExternalPrintHistory";

        self.spoolmanUrl = ko.observable();
        self.spoolmanError = ko.observable(false);
        self.isloading = ko.observable(false);
        self.spools = ko.observableArray([]);

        self.getTools = function () {
            self.isloading(true);
            $.ajax({
                url: apiUrl + "/getTools",
                type: "GET",
                contentType: "application/json",
            })
                .done(function (response) {
                    console.table(response);
                    self.spools(
                        response.map((spool) => ({
                            tool: spool.tool,
                            color: spool.color || "white",
                            material: spool.material,
                            displayName: spool.displayName,
                            vendor: spool.vendor,
                            remainingWeight: spool.remainingWeight,
                            notFound: spool.notFound,
                        }))
                    );
                    self.spoolmanError(false);
                })
                .fail(function (xhr) {
                    self.spoolmanError(true);
                    var errorMessage =
                        xhr.responseJSON && xhr.responseJSON.message
                            ? xhr.responseJSON.message
                            : xhr.responseText || "Unknown error";
                    console.error("Error getting tools: ", errorMessage);
                })
                .always(function () {
                    self.isloading(false);
                });
        };

        self.getUrlSpoolman = function () {
            $.ajax({
                url: apiUrl + "/getUrlSpoolman",
                type: "GET",
                contentType: "application/json",
            })
                .done(function (response) {
                    self.spoolmanUrl(response);
                })
                .fail(function (xhr) {
                    var errorMessage =
                        xhr.responseJSON && xhr.responseJSON.message
                            ? xhr.responseJSON.message
                            : xhr.responseText || "Unknown error";
                    console.error("Error getting Spoolman url: ", errorMessage);
                });
        };

        // Desselectar un spool
        self.deselectSpool = function (spool) {
            // TODO: Implementar lógica para desselectar un spool
            console.log("Deselect spool with index:", spool.index);
        };

        // Cambiar un spool
        self.changeSpool = function (spool) {
            // TODO: Implementar lógica para cambiar un spool
            console.log("Change spool with index:", spool.index);
        };

        self.refreshTools = function () {
            self.spoolmanError(false);
            self.getTools();
        };

        self.onAfterBinding = function () {
            self.getTools();
            self.getUrlSpoolman();
        };
    }
    // Registrar el ViewModel en OctoPrint
    OCTOPRINT_VIEWMODELS.push({
        construct: ExternalPrintHistorySidebarViewModel,
        dependencies: ["settingsViewModel", "printerStateViewModel"],
        elements: ["#ExternalPrintHistory-sidebar"], // Asegúrate de que el selector del div es correcto
    });
});

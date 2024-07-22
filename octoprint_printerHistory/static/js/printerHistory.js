$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        self.settingsViewModel = parameters[0];

        // Maneja mensajes del plugin de datos
        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin !== "PrinterHistory") {
                return;
            }

            // Procesar datos específicos del plugin
            console.log("Mensaje del plugin de historial de impresoras:", data);
            // Implementar lógica adicional aquí
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

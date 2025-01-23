$(function () {
    function ExternalPrintHistoryTabDialogs(parameters) {
        var self = this;

        // Modelos de vista de OctoPrint
        self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[1];
        self.printerStateViewModel = parameters[2];
        self.filesViewModel = parameters[3];
        self.printerProfilesViewModel = parameters[4];

        self.pluginCheckDialog = new ExternalPrintHistoryPluginCheckDialog();
        self.costEstimate = new ExternalPrintHistoryCostEstimate();

        // Mensajes desde el plugin
        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin === "ExternalPrintHistory") {
                if (data.action === "PluginCheck") {
                    self.pluginCheckDialog.showMissingPluginsDialog(
                        data.message
                    );
                } else if (data.action === "showPopUp") {
                    new PNotify({
                        title: "External Print History: " + data.title,
                        text: data.message,
                        type: data.popupType,
                        hide: data.hide,
                    });
                } else if (data.action === "costEstimated") {
                    self.costEstimate.showCostEstimate(data);
                }
            }
        };

        const origStartPrintFunction = self.printerStateViewModel.print;

        // Nueva función con confirmación
        const newStartPrintFunction = function () {
            const confirmPrint = confirm("¿Deseas iniciar la impresión?");
            if (confirmPrint) {
                origStartPrintFunction();
            } else {
                console.log("Impresión cancelada por el usuario.");
            }
        };

        // Sobrescribir la función de impresión
        self.printerStateViewModel.print = newStartPrintFunction;

        // Sobrescribir carga y confirmación de impresión
        self.filesViewModel.loadFile = function (data, printAfterLoad) {
            if (
                !self.filesViewModel.loginState.hasPermission(
                    self.filesViewModel.access.permissions.FILES_SELECT
                )
            )
                return;

            if (!data) return;

            if (
                printAfterLoad &&
                self.filesViewModel.listHelper.isSelected(data) &&
                self.filesViewModel.enablePrint(data)
            ) {
                newStartPrintFunction();
            } else {
                OctoPrint.files
                    .select(data.origin, data.path, false)
                    .done(function () {
                        if (printAfterLoad) {
                            newStartPrintFunction();
                        }
                    });
            }
        };
    }

    // Registrar el modelo en OctoPrint
    OCTOPRINT_VIEWMODELS.push({
        construct: ExternalPrintHistoryTabDialogs,
        dependencies: [
            "loginStateViewModel",
            "settingsViewModel",
            "printerStateViewModel",
            "filesViewModel",
            "printerProfilesViewModel",
        ],
        elements: ["#modal-dialogs-ExternalPrintHistory"],
    });
});

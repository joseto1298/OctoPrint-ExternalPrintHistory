$(function () {
    function ExternalPrintHistoryTabDialogs(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        //self.apiClient = new PrintJobHistoryAPIClient(PLUGIN_ID, BASEURL);
        self.apiClient = new ExternalPrintHistoryApiRest();

        self.pluginCheckDialog = new ExternalPrintHistoryPluginCheckDialog();

        self.pluginCheckDialog.init(self.apiClient);

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin == "ExternalPrintHistory") {
                if (data.type == "PluginCheck") {
                    self.pluginCheckDialog.showMissingPluginsDialog(
                        data.message
                    );
                }
                if (data.action == "showPopUp") {
                    new PNotify({
                        title: "External Print History: " + data.title,
                        text: data.message,
                        type: data.popupType,
                        hide: data.hide,
                    });
                }
            }
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: ExternalPrintHistoryTabDialogs,
        dependencies: ["settingsViewModel"],
        elements: ["#modal-dialogs-ExternalPrintHistory"],
    });
});

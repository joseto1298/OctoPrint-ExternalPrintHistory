// printerHistory.js

$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        self.settingsViewModel = parameters[0];
        self.popup = undefined;

        self.onDataUpdaterPluginMessage = function (plugin, data) {};
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

$(function () {
    function PrinterHistoryViewModel(parameters) {
        var self = this;
        self.settingsViewModel = parameters[0];
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PrinterHistoryViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#printerhistory"],
    });
});

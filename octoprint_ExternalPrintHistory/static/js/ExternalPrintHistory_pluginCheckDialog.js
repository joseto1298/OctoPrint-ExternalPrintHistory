function ExternalPrintHistoryPluginCheckDialog() {
    var self = this;

    self.apiClient = null;
    self.missingPluginsDialog = $("#dialog-ExternalPrintHistory-missingPlugins");
    self.missingPluginMessage = $("#Plugin-Message-check");

    self.init = function (apiClient) {
        self.apiClient = apiClient;
    };

    this.hideDialog = function () {
        self.missingPluginsDialog.modal("hide");
    };

    this.closeDialog = function () {
        if ($("#deactivate-PluginCheck").is(":checked")) {
            self.apiClient.callDeactivatePluginCheck();
        }
        $("#closeMissingPlugins").off("click");
        self.hideDialog();
    };

    this.showMissingPluginsDialog = function (dialogMessage) {
        if (
            self.missingPluginsDialog != null &&
            self.missingPluginsDialog.is(":visible")
        ) {
            return;
        }
        self.missingPluginMessage.html(dialogMessage);
        $("#closeMissingPlugins").on("click", self.closeDialog);

        self.missingPluginsDialog
            .modal({
                //minHeight: function() { return Math.max($.fn.modal.defaults.maxHeight() - 80, 250); }
                keyboard: false,
                clickClose: false,
                showClose: false,
                backdrop: "static",
            })
            .css({
                width: "auto",
                "margin-left": function () {
                    return -($(this).width() / 2);
                },
            });
    };
}
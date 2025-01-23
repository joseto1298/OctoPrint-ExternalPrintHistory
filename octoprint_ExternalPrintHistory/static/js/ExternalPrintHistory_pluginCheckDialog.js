/**
 * The ExternalPrintHistoryPluginCheckDialog class is used to display the dialog for checking plugins.
 */
function ExternalPrintHistoryPluginCheckDialog() {
    var self = this;
    var apiUrl = BASEURL + "plugin/ExternalPrintHistory";

    /**
     * The element that contains the missing plugins dialog
     * @type {JQuery}
     */
    self.missingPluginsDialog = $(
        "#dialog-ExternalPrintHistory-missingPlugins"
    );

    /**
     * The element that contains the missing plugin message
     * @type {JQuery}
     */
    self.missingPluginMessage = $("#Plugin-Message-check");

    /**
     * Hide the dialog
     */
    this.hideDialog = function () {
        self.missingPluginsDialog.modal("hide");
    };

    /**
     * Close the dialog
     */
    this.closeDialog = function () {
        if ($("#deactivate-PluginCheck").is(":checked")) {
            $.ajax({
                url: apiUrl + "/deactivatePluginCheck",
                type: "PUT",
                contentType: "application/json",
                success: function (response) {},
                error: function (xhr) {
                    var errorMessage = "";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    console.error(
                        "Failed to deactivate plugin check: " + errorMessage
                    );
                },
            });
        }
        $("#closeMissingPlugins").off("click");
        self.hideDialog();
    };

    /**
     * Show the dialog with the given message
     * @param {string} dialogMessage The message to display in the dialog
     */
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

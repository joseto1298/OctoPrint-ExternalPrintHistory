/**
 * ExternalPrintHistoryApiRest class
 *
 * This class is used to interact with the OctoPrint server
 * and the ExternalPrintHistory plugin
 */
function ExternalPrintHistoryApiRest() {
    /**
     * The base URL for the OctoPrint server
     * @type {string}
     */
    var urlApi = BASEURL + "plugin/ExternalPrintHistory";

    /**
     * The instance of the ExternalPrintHistoryApiRest class
     * @type {ExternalPrintHistoryApiRest}
     */
    var self = this;

    /**
     * Deactivate plugin check
     *
     * Send a PUT request to the OctoPrint server to deactivate the plugin check
     *
     * @param {object} [data] The data to send with the request
     */
    this.callDeactivatePluginCheck = function (data) {
        $.ajax({
            url: urlApi + "/deactivatePluginCheck",
            type: "PUT",
            contentType: "application/json",
            data: data,
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
    };

    /**
     * Test database connection
     *
     * Send a PUT request to the OctoPrint server to test the database connection
     *
     * @param {object} data The data to send with the request
     * @returns {Promise} A promise that is resolved if the request is successful or rejected if the request fails
     *
    self.testDbConnection = function (data) {
        //console.table(data);
        return new Promise((resolve, reject) => {
            $.ajax({
                url: urlApi + "/testdbconnection",
                type: "",
                contentType: "application/json",
                data: JSON.stringify(data),
                success: function (response) {
                    resolve(response);
                },
                error: function (xhr) {
                    var errorMessage = "";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    console.error(
                        "Failed to test database connection: " + errorMessage
                    );
                    reject(errorMessage);
                },
            });
        });
    };
    */

    /**
     * Select printer
     *
     * Send a PUT request to the OctoPrint server to select the printer
     *
     * @param {object} data The data to send with the request
     * @returns {Promise} A promise that is resolved if the request is successful or rejected if the request fails
     *
    self.selectPrinter = function (data) {
        //console.table(data);
        return new Promise((resolve, reject) => {
            //console.table(data);
            $.ajax({
                url: urlApi + "/selectPrinter",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(data),
                success: function (response) {
                    resolve(response);
                },
                error: function (xhr) {
                    var errorMessage = "";
                    if (xhr.responseJSON && xhr.responseJSON.message) {
                        errorMessage = xhr.responseJSON.message;
                    } else if (xhr.responseText) {
                        errorMessage = xhr.responseText;
                    }
                    console.error(
                        "Failed to test database connection: " + errorMessage
                    );
                    reject(errorMessage);
                },
            });
        });
    };
    */
}

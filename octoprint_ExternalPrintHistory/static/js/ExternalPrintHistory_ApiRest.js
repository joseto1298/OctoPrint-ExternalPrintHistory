function ExternalPrintHistoryApiRest() {
    var urlApi = BASEURL + "plugin/ExternalPrintHistory";
    self = this;

    /**
     * Sends a PUT request to deactivate the plugin check.
     *
     * @param {object} data - The data to be sent in the request body.
     * @return {void} This function does not return anything.
     */
    this.callDeactivatePluginCheck = function (data) {
        $.ajax({
            url: urlApi + "/deactivatePluginCheck",
            type: "PUT",
            contentType: "application/json",
            success: function (response) {},
            error: function (xhr) {
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
     * Tests the database connection by sending a PUT request to the /testdbconnection endpoint.
     *
     * @param {object} data - The data to be sent in the request body.
     * @return {Promise} A promise that resolves with the response data or rejects with an error message.
     */
    self.testDbConnection = function (data) {
        //console.table(data);
        return new Promise((resolve, reject) => {
            $.ajax({
                url: urlApi + "/testdbconnection",
                type: "PUT",
                contentType: "application/json",
                data: JSON.stringify(data),
                success: function (response) {
                    resolve(response);
                },
                error: function (xhr) {
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
}

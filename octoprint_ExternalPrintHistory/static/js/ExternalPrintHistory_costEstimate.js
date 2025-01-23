function ExternalPrintHistoryCostEstimate() {
    var self = this;

    self.filamentCost = ko.observable(0);
    self.electricityCost = ko.observable(0);
    self.printerCost = ko.observable(0);
    self.currency = ko.observable("€"); // Asignamos un valor por defecto a la moneda

    self.estimatedTotalCost = ko.computed(function () {
        var filament = parseFloat(self.filamentCost()) || 0;
        var electricity = parseFloat(self.electricityCost()) || 0;
        var printer = parseFloat(self.printerCost()) || 0;

        return (filament + electricity + printer).toFixed(2);
    });

    self.costBreakdown = ko.computed(function () {
        return (
            "Filament: " +
            self.filamentCost().toFixed(2) +
            " " +
            self.currency() +
            "\n" +
            "Electricity: " +
            self.electricityCost().toFixed(2) +
            " " +
            self.currency() +
            "\n" +
            "Printer: " +
            self.printerCost().toFixed(2) +
            " " +
            self.currency()
        );
    });

    self.showCostEstimate = function (data) {
        // Asegurar que los datos de moneda sean válidos
        self.currency(data.estimatedCost?.currency || "€");
        self.filamentCost(parseFloat(data.estimatedCost?.filamentCost) || 0);
        self.electricityCost(
            parseFloat(data.estimatedCost?.electricityCost) || 0
        );
        self.printerCost(parseFloat(data.estimatedCost?.printerCost) || 0);

        var element = $("#state").find("hr:nth-of-type(2)");

        if (element.length) {
            var costDiv = $("#costestimation");

            if (costDiv.length === 0) {
                costDiv = $("<div id='costestimation'></div>");
                var name = gettext("Cost");
                var text = gettext(
                    "Estimated print cost based on required quantity of filament and print time"
                );

                costDiv.append(
                    "<span title='" + text + "'>" + name + "</span>: "
                );
                costDiv.append(
                    "<strong data-bind='text: estimatedTotalCost() + \" \" + currency(), attr: { title: costBreakdown() }'></strong>"
                );

                element.before(costDiv);

                ko.applyBindings(self, costDiv[0]);
            }

            if (data.visibility === "hidden") {
                costDiv.hide();
            } else {
                costDiv.show();
            }
        }
    };
}

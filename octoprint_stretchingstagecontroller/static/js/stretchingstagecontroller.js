$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        var self = this;

        self.name = "stretchingstagecontroller";

        self.settings = parameters[0];
        self.printerStateViewModel = parameters[2];

        self.savePath = ko.observable();

        self.serialReadPort = ko.observable();
        
        self.saveFileName = ko.observable();
        self.newFileName = ko.observable();

        self.portOptions = ko.observable();

        //Wrap start print in new function for data check popup
        const startPrint = self.printerStateViewModel.print;
        const newStartPrint = function confirmSpoolSelectionBeforeStartPrint() {
            alert("pre vaildate stuff");
            console.log("Test")
            startPrint();
        };
        self.printerStateViewModel.print = newStartPrint;


        self.updateFileName = function() {
            self.saveFileName(self.newFileName());
        }

        self.onBeforeBinding = function() {
            //Retrieve save file path from settings
            self.savePath(self.settings.settings.plugins.stretchingstagecontroller.save_path());

            self.serialReadPort(self.settings.settings.plugins.stretchingstagecontroller.serial_read_port());

            self.portOptions(self.settings.settings.plugins.stretchingstagecontroller.port_options());

            self.newFileName("text.txt");
            self.updateFileName();


        }

        self.validateSettings = function() {
            var  payload = {"save_path": self.savePath(), "file_name": self.saveFileName()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "validateSettings", payload)
            .done(function(response) {
            })

        }


    }



    OCTOPRINT_VIEWMODELS.push({
        construct: stretchingstagecontrollerViewModel,

          // e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel", "connectionViewModel", "printerStateViewModel" ],

          // e.g. #settings_plugin_DetailedProgress, #tab_plugin_DetailedProgress, ...
        elements: ["#tab_plugin_stretchingstagecontroller"]
    });
});
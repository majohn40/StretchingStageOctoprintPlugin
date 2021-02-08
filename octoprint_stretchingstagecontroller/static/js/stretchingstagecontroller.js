$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        var self = this;
        self.name = "stretchingstagecontroller";

        self.settings = parameters[0];

        self.savePath = ko.observable();

        self.serialReadPort = ko.observable();
        
        self.saveFileName = ko.observable();
        self.newFileName = ko.observable();

        self.updateFileName = function() {
            self.saveFileName(self.newFileName());
        }

        self.onBeforeBinding = function() {
            //Retrieve save file path from settings
            self.savePath(self.settings.settings.plugins.stretchingstagecontroller.save_path());

            self.serialReadPort(self.settings.settings.plugins.stretchingstagecontroller.serial_read_port());

            self.newFileName("text.txt");
            self.updateFileName();

        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: stretchingstagecontrollerViewModel,

          // e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel", "connectionViewModel"],

          // e.g. #settings_plugin_DetailedProgress, #tab_plugin_DetailedProgress, ...
        elements: ["#tab_plugin_stretchingstagecontroller"]
    });
});
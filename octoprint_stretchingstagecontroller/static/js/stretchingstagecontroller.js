$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        var self = this;
        self.name = "stretchingstagecontroller";

        self.settings = parameters[0];

        self.savePath = ko.observable();
        self.saveFileName = ko.observable();

        self.newFileName = ko.observable();

        // this will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL

        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.
        self.updateFileName = function() {
            self.saveFileName(self.newFileName());
        }

        self.onBeforeBinding = function() {
            //Retrieve save file path from settings
            self.savePath(self.settings.settings.plugins.stretchingstagecontroller.save_path());

            self.newFileName("text.txt");
            self.updateFileName();

        }
    }
    OCTOPRINT_VIEWMODELS.push({
        construct: stretchingstagecontrollerViewModel,

          // e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel"],

          // e.g. #settings_plugin_DetailedProgress, #tab_plugin_DetailedProgress, ...
        elements: ["#tab_plugin_stretchingstagecontroller", "#settings_plugin_stretchingstagecontroller"]
    });
});
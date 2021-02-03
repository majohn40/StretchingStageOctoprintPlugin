$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        var self = this;

        self.settings = parameters[0];

        // this will hold the URL currently displayed by the iframe
        self.portsAvailable = ko.observable();

        // this will hold the URL entered in the text field
        self.newPort = ko.observable();

        self.savePath = ko.observable()

        // this will be called when the user clicks the "Go" button and set the iframe's URL to
        // the entered URL

        // This will get called before the HelloWorldViewModel gets bound to the DOM, but after its
        // dependencies have already been initialized. It is especially guaranteed that this method
        // gets called _after_ the settings have been retrieved from the OctoPrint backend and thus
        // the SettingsViewModel been properly populated.

        self.onBeforeBinding = function() {
            self.savePath(self.settings.settings.plugins.stretchingstagecontroller.save_path());
        }
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    OCTOPRINT_VIEWMODELS.push([
        construct: stretchingstagecontrollerViewModel,
        elements: ["#tab_plugin_stretchingstagecontroller"]
    ]);
});
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

        self.dataPortConnected = ko.observable();

        //Wrap start print in new function for data check popup
        const startPrint = self.printerStateViewModel.print;
        const newStartPrint = function confirmSpoolSelectionBeforeStartPrint() {
            showDialog("#sidebar_simpleDialog", function(dialog){
                startPrint();
                dialog.modal('hide');
            });
        };
        self.printerStateViewModel.print = newStartPrint;

        //Dialog modal code
        function showDialog(dialogId, confirmFunction){
                // show dialog
                // sidebar_deleteFilesDialog
                var myDialog = $(dialogId);
                var confirmButton = $("button.btn-confirm", myDialog);
                var cancelButton = $("button.btn-cancel", myDialog);
                //var dialogTitle = $("h3.modal-title", editDialog);

                confirmButton.unbind("click");
                confirmButton.bind("click", function() {
                    alert ("Clicked");
                    confirmFunction(myDialog);
                });
                myDialog.modal({
                    //minHeight: function() { return Math.max($.fn.modal.defaults.maxHeight() - 80, 250); }
                }).css({
                    width: 'auto',
                    'margin-left': function() { return -($(this).width() /2); }
                });
        }


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
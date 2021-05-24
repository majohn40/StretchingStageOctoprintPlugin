$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        var self = this;

        self.name = "stretchingstagecontroller";

        self.settings = parameters[0];
        self.connectionViewModel = parameters[1];
        self.printerStateViewModel = parameters[2];

        self.savePath = ko.observable();

        self.serialReadPort = ko.observable();
        self.newPort = ko.observable();
        
        self.saveFileName = ko.observable();
        self.newFileName = ko.observable();

        self.portOptions = ko.observable();

        self.dataPortConnected = ko.observable();
        self.dataPortConnected(false);

        //Wrap start print in new function for data check popup
        const startPrint = self.printerStateViewModel.print;
        const newStartPrint = function validateCOMBeforeStartingPrint() {
            console.log(self.dataPortConnected());
            if(self.dataPortConnected() == true){
                showDialog("#sidebar_startPrintDialog", function(dialog){
                    startPrint();
                    dialog.modal('hide');
                    new PNotify({
                        title: 'Serial Data Collection Started',
                        text: "Reading Serial Data",
                        type: "info",
                        hide: true
                    });
                });
            } else {
                showDialog("#sidebar_noComWarningDialog", function(dialog){
                    startPrint();
                    dialog.modal('hide');
                });   
            }

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

        self.updatePortSelection=function(){
            self.serialReadPort(self.newPort())
        }

        self.onBeforeBinding = function() {
            //Retrieve save file path from settings
            console.log("Data Request Output");
            console.log(self.connectionViewModel.portOptions())

            self.newFileName("text.txt");
            self.updateFileName();

            self.dataPortConnected(false);


        }
        self.onDataUpdaterPluginMessage = function(plugin, data){
            if (plugin != "stretchingstagecontroller") {
                return;
            }
            if(data.message == "ComNotConnected"){
                new PNotify({
                    title: 'COM Not Connected',
                    text: "The serial COM port was not connected",
                    type: "error",
                    hide: true
                });
                self.dataPortConnected(false);
            } else if (data.message == "ComConnected"){
                new PNotify({
                    title: 'COM Connected',
                    text: "Ready for Serial Data Readout",
                    type: "info",
                    hide: true
                });
                self.dataPortConnected(true);

            } else if (data.message == "valid_filename"){
                new PNotify({
                    title: 'Filename Accepted',
                    text: "New files will be named "+self.settings.settings.plugins.stretchingstagecontroller.save_path(),
                    type: "info",
                    hide: true
                });
                self.dataPortConnected(true);

            } else if (data.message == "invalid_filename"){
                new PNotify({
                    title: 'Invalid Filename',
                    text: "File already exists. The new data file will overwrite the existing file.",
                    type: "error",
                    hide: true
                });
                self.dataPortConnected(true);

            }

        }


        self.validateSettings = function() {
            self.updateFileName();
            var  payload = {"save_path": self.settings.settings.plugins.stretchingstagecontroller.save_path(), "file_name": self.saveFileName()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "validateSettings", payload)
            .done(function(response) {
            })

        }

        self.connectCOM = function() {
            self.updatePortSelection();
            var payload = {"serial_read_port":self.serialReadPort()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "connectCOM", payload)
            .done(function(response){
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
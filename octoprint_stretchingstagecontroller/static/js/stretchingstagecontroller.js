$(function() {
    function stretchingstagecontrollerViewModel(parameters) {
        let self = this;

        self.name = "stretchingstagecontroller";

        self.settings = parameters[0];
        self.connectionViewModel = parameters[1];
        self.printerStateViewModel = parameters[2];

        self.serialReadPort = ko.observable();
        self.newPort = ko.observable();

        self.saveFileName = ko.observable();
        self.newFileName = ko.observable();

        self.selectedPorts = ko.observableArray([]);
        self.listOfPorts = ko.observableArray([]);

        self.dataPortConnected = ko.observable();
        self.dataPortConnected(false);

        self.pathValidated = ko.observable();
        self.pathValidated(false);

        // Wrap start print in new function for data check popup
        const startPrint = self.printerStateViewModel.print;
        const newStartPrint = function validateCOMBeforeStartingPrint() {
            if(self.dataPortConnected() == true){
                if(self.pathValidated() == true){
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
                } else{
                    showDialog("#sidebar_filePathNotValidated", function(dialog){
                        startPrint();
                        dialog.modal('hide');
                    });
                }

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
            let myDialog = $(dialogId);
            let confirmButton = $("button.btn-confirm", myDialog);
            let cancelButton = $("button.btn-cancel", myDialog);

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

        self.updateSelectedPorts=function(){
            self.selectedPorts(self.listOfPorts())
        }

        self.updatePortSelection=function(){
            self.serialReadPort(self.newPort())
        }

        self.onBeforeBinding = function() {
            // Retrieve save file path from settings
            console.log("Data Request Output");
            console.log(self.connectionViewModel.portOptions())

            self.newFileName("text.txt");
            self.updateFileName();
            self.fetchPorts();

            self.dataPortConnected(false);
        }

        self.onDataUpdaterPluginMessage = function(plugin, data){
            if (plugin != "stretchingstagecontroller") {
                return;
            }
            let notification = {};

            notification.buttons =
                {
                    closer_hover: false,
                    show_on_nonblock: false
                };

            switch(data.message) {

                case "ComNotConnected":
                    notification.title = 'COM Not Connected';
                    notification.text =  "Connection to the following COM port could not be established: " + data.port;
                    notification.type = "error";
                    notification.hide = true;
                    self.dataPortConnected(false);
                    break;

                case "ComConnected":
                    notification.title =  'COM Connected';
                    notification.text =  "Ready for Serial Data Readout";
                    notification.type = "info";
                    notification.hide = true;
                    self.dataPortConnected(true);
                    break;

                case "ports_fetched":
                    self.listOfPorts(data.ports);
                    break;

                case "valid_filename":
                    notification.title =  'Filename Accepted';
                    notification.text =  "File will be saved at " + self.settings.settings.plugins.stretchingstagecontroller.save_path() + self.saveFileName();
                    notification.type = "info";
                    notification.hide = true;
                    self.pathValidated(true);
                    break;

                case "invalid_filename":
                    notification.title =  'Invalid Filename';
                    notification.text =  "File already exists. Please select new filename or delete conflicting file.";
                    notification.type = "error";
                    notification.hide = true;
                    break;

                case "path_does_not_exist":
                    notification.title =  'Path Does Not Exist';
                    notification.text =  "You are trying to save files to a nonexistent path. Please edit the save path in Octoprint settings to a valid path";
                    notification.type = "error";
                    notification.hide = true;
                    break;

                case "path_missing_slash":
                    notification.title =  'Path must end in /';
                    notification.text =  "You are trying to save files to an invalid path. Path must end in /. Please edit the save path in Octoprint settings to a valid path";
                    notification.type = "error";
                    notification.hide = true
                    break;

                case "com_disconnected":
                    notification.title =  'COM Port Disconnected';
                    notification.text =  "COM port has been successfully disconnected";
                    notification.type = "info";
                    notification.hide = true
                    self.dataPortConnected(false)
                    break;

                case "data_collected":
                    self.pathValidated(false);
                    break;
            }
            if(notification.title){
                new PNotify(notification);
            }

        }

        self.fetchPorts = function() {
            let payload = {}
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "fetchPorts", payload)
                .done(function(response){
                })
        }


        self.validateSettings = function() {
            self.updateFileName();
            let  payload = {"save_path": self.settings.settings.plugins.stretchingstagecontroller.save_path(),
                "file_name": self.saveFileName(),"serial_read_port":self.serialReadPort()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "validateSettings", payload)
                .done(function(response) {
                })
        }

        self.connectCOM = function() {
            self.updateSelectedPorts();
            let payload = {"serial_read_port":self.selectedPorts()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "connectCOM", payload)
                .done(function(response){
                })
        }

        // self.connectCOM = function() {
        //     self.updatePortSelection();
        //     let payload = {"serial_read_port":self.serialReadPort()};
        //     OctoPrint.simpleApiCommand("stretchingstagecontroller", "connectCOM", payload)
        //         .done(function(response){
        //         })
        // }

        self.disconnectCOM = function() {
            self.updatePortSelection();
            let payload = {"serial_read_port":self.serialReadPort()};
            OctoPrint.simpleApiCommand("stretchingstagecontroller", "disconnectCOM", payload)
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

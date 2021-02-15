# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import serial.tools.list_ports
import os
import os.path
from os import path




class StretchingStagePlugin(octoprint.plugin.StartupPlugin,
			    octoprint.plugin.TemplatePlugin,
			    octoprint.plugin.AssetPlugin,
			    octoprint.plugin.EventHandlerPlugin,
			    octoprint.plugin.SettingsPlugin,
                octoprint.plugin.SimpleApiPlugin):

    def on_after_startup(self):
        self.ports_available = ["port1", "port2", "port3"]##[comport.device for comport in serial.tools.list_ports.comports()]
        port = 0;
        self._logger.info("Hello World! (more: %s)" % self._settings.get(["save_path"]))
        self.selected_port = []


    def get_assets(self):
	    return dict(
	        js=["js/stretchingstagecontroller.js"]
	    )
    def on_event(self, event, payload):
        title = description = None

        if event == octoprint.events.Events.UPLOAD:
            title = "A new file was uploaded"
            print(title)

        elif event == octoprint.events.Events.PRINT_STARTED:
            file = payload['name']

            title = "A new print job was started"
            description = "{file} has started printing".format(file=file)
            print(title)
            print(description)


        elif event == octoprint.events.Events.PRINT_DONE:
            title = "Print job finished"
            description = "{file} finished printing, took {elapsed_time} seconds".format(file=file, elapsed_time=elapsed_time)
            print(title)

        elif event == octoprint.events.Events.PRINT_FAILED:
            title = "Print failed hook test"
            print(title)

        self._logger.info("Hello World! (more: %s)" % self._settings.get(["save_path"]))



    def get_template_configs(self):
	    return [
	        dict(type="settings", custom_bindings=False),
	        dict(type="tab", custom_bindings=False)
	    ]


    def get_settings_defaults(self):
    	return dict(
            save_path="~/",
            port_options = [comport.device for comport in serial.tools.list_ports.comports()]
        )

    def get_api_commands(self):
        return dict(
            validateSettings=["save_path", "file_name"]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "validateSettings":
            if "save_path" in data:
                self._logger.info("Parameters Recieved. Save path is {save_path}".format(**data))
                parameter = "set"
                dir_exists = path.exists("{save_path}".format(**data))
                file_exists = path.exists("{save_path}{file_name}".format(**data))
                print("{save_path}{file_name}".format(**data))
                if(dir_exists):
                    self._logger.info("Settings directory exists and is ready for readout")
                else:
                    self._logger.info("*******WARNING******** Save directory for Stretching Stage Controller does not exist! Please pick a valid save directory")
                if(file_exists):
                    self._logger.info("*******WARNING******** File you are attempting to write to already exists- file will be appended")
                else:
                    self._logger.info("New file being created")

        elif command == "command2":
            self._logger.info("command2 called, some_parameter is {some_parameter}".format(**data))





__plugin_name__ = "Stretching Stage Controller"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = StretchingStagePlugin()

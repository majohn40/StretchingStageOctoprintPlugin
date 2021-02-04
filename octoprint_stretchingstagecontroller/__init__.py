# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import serial.tools.list_ports



class StretchingStagePlugin(octoprint.plugin.StartupPlugin,
			    octoprint.plugin.TemplatePlugin,
			    octoprint.plugin.AssetPlugin,
			    octoprint.plugin.EventHandlerPlugin,
			    octoprint.plugin.SettingsPlugin):

    def on_after_startup(self):
        self.ports_available = [comport.device for comport in serial.tools.list_ports.comports()]
        port = 0;
        self._logger.info("Hello World! (more: %s)" % self._settings.get(["save_path"]))

    def get_assets(self):
	    return dict(
	        js=["js/stretchingstagecontroller.js"]
	    )
    def on_event(self, event, payload):
        import os

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
    	return dict(save_path="~/")




__plugin_name__ = "Stretching Stage Controller"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = StretchingStagePlugin()

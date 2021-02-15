# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import octoprint.plugin
import serial.tools.list_ports
import os
import os.path
from os import path
import threading
import serial





class StretchingStagePlugin(octoprint.plugin.StartupPlugin,
			    octoprint.plugin.TemplatePlugin,
			    octoprint.plugin.AssetPlugin,
			    octoprint.plugin.EventHandlerPlugin,
			    octoprint.plugin.SettingsPlugin,
                octoprint.plugin.SimpleApiPlugin):

    stop = threading.Event()

    def on_stop(self):
        self.stop.set();

    def start_serial_thread(self):
        threading.Thread(target=self.serial_thread).start()
    
    def serial_thread(self):
        ##When this thread is initialized, open serial port
        try:
            ser = serial.Serial(
            port='/dev/cu.usbserial-14220',\
            baudrate=57600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
            self._logger.info("Connected to COM port for data readout")
            f = open("myfile.txt", "x")

        except:
            self._logger.error("COM port not opened- data cannot be collected")
            return

        ser.flushInput()
        ser.flushOutput()

        while True:
            f.write(ser.readline().decode('utf-8'))
            ##If GUI is closed, stop this thread so python can exit fully
            if self.stop.is_set():
                print("The serial thread is being stopped")
                f.close();
                return



    def on_after_startup(self):
        self._logger.info("Hello World! (more: %s)" % self._settings.get(["save_path"]))


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

            title = "Begin Data Collection"
            description = "{file} has started printing".format(file=file)
            print(title)
            print(description)
            self.start_serial_thread()


        elif event == octoprint.events.Events.PRINT_DONE:
            title = "Stop Data collection'"
            description = "{file} finished printing, took {elapsed_time} seconds".format(file=file, elapsed_time=elapsed_time)
            print(title)
            self.stop.set();


        elif event == octoprint.events.Events.PRINT_FAILED:
            title = "Stop Data Collection"
            print(title)
            self.stop.set();


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

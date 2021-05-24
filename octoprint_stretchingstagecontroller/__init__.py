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
    read_serial_data = False
    com_connected = False;

    def on_shutdown(self):
        self.stop.set();

    def on_stop(self):
        self.stop.set();

    def start_serial_thread(self, port):
        threading.Thread(target=self.serial_thread, args=(port,)).start()
    
    def serial_thread(self, port):
        ##When this thread is initialized, open serial port
        try:
            self.ser = serial.Serial(
            #port=self._settings.get(["serial_read_port"]),\
            port=port,\
            baudrate=57600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
            self._logger.info("Connected to COM port for data readout")
            self._plugin_manager.send_plugin_message(self._identifier, dict(message="ComConnected"))
            self.com_connected = True;


        except:
            self._logger.error("COM port {x} not opened- data cannot be collected".format(x=port))
            self._plugin_manager.send_plugin_message(self._identifier, dict(message="ComNotConnected"))
            self.com_connected = False;
            return

        self.ser.flushInput()
        self.ser.flushOutput()

        while True:
            if self.stop.is_set():
                self._logger.info("The serial thread is being shut down")
                self.f.close();
                self.com_connected = False;

                return

    def read_serial(self):
        while self.read_serial_data:
            self.f.write("10,20,30")#self.ser.readline().decode('utf-8'))
            ##If GUI is closed, stop this thread so python can exit fully
            if self.stop.is_set():
                self.f.close();
                return



    def on_after_startup(self):
        self._logger.info("Stretching Stage Controller Starting Up")


    def get_assets(self):
	    return dict(
	        js=["js/stretchingstagecontroller.js"]
	    )
    def on_event(self, event, payload):
        if event == octoprint.events.Events.PRINT_STARTED:
            self._logger.info("Starting New Print--- serial read should start")
            if self.com_connected:
                self.read_serial_data = True;
                self.f = open("myfile.txt", "x")
                self.read_serial();


        if event == octoprint.events.Events.PRINT_DONE:
            if self.read_serial_data:
                self.read_serial_data = False;
                self.stop.set();
                self.f.close();


        if event == octoprint.events.Events.PRINT_FAILED:
            if self.read_serial_data:
                self.read_serial_data = False;
                self.stop.set();
                self.f.close();


        if event == octoprint.events.Events.PRINT_CANCELLING:
            self._logger.info("Canceling this print-- loop should stop ehre")
            if self.read_serial_data:
                self.read_serial_data = False;
                self.stop.set();
                self.f.close();


    def get_template_configs(self):
	    return [
	        dict(type="settings", custom_bindings=False),
	        dict(type="tab", custom_bindings=False)
	    ]


    def get_settings_defaults(self):
    	return dict(
            save_path="~/"
            #port_options = [comport.device for comport in serial.tools.list_ports.comports()],
           # serial_read_port = ""
        
        )

    def get_api_commands(self):
        return dict(
            validateSettings=["save_path", "file_name"],
            connectCOM=["serial_read_port"]
        )

    def on_api_command(self, command, data):
        import flask
        if command == "validateSettings":
            if "save_path" in data:
                self._logger.info("Parameters Recieved. Save path is {save_path}".format(**data))
                parameter = "set"
                dir_exists = path.exists("{save_path}".format(**data))
                file_exists = path.exists("{save_path}{file_name}".format(**data))
                if(dir_exists):
                    self._logger.info("Settings directory exists and is ready for readout")
                else:
                    self._logger.info("*******WARNING******** Save directory for Stretching Stage Controller does not exist! Please pick a valid save directory")
                if(file_exists):
                    self._logger.info("*******WARNING******** File you are attempting to write to already exists- file will be appended")
                else:
                    self._logger.info("New file being created")

        if command == "connectCOM":
            if "serial_read_port" in data:
                self._logger.info("connectCOM called. Port is {serial_read_port}".format(**data))
                self.start_serial_thread("{serial_read_port}".format(**data));





__plugin_name__ = "Stretching Stage Controller"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = StretchingStagePlugin()

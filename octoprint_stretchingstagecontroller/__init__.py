# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import re

import octoprint.plugin
import serial.tools.list_ports
from os import path
import threading
import serial


class CommunicationPort:

	stop = threading.Event()

	def __init__(self, port=None, logger=None, plugin_manager=None, identifier=None):
		self.port = port
		self._logger = logger
		self._plugin_manager = plugin_manager
		self._identifier = identifier
		self.f = None
		self.read_serial_data = False
		self.save_path = None
		self.com_connected = False
		self.ser = None

	def __str__(self):
		return self.port

	def on_stop(self):
		self.stop.set()

	def serial_thread(self):
		# When this thread is initialized, open serial port
		try:
			self.ser = serial.Serial(
				port=self.port,
				baudrate=57600,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout=0)
			self._logger.info("Connected to COM port {} for data readout".format(self.port))
			self._plugin_manager.send_plugin_message(self._identifier, dict(message="ComConnected", port=self.port))
			self.com_connected = True
		except:
			self._logger.error("COM port {} could not be opened - data cannot be collected".format(self.port))
			self._plugin_manager.send_plugin_message(self._identifier, dict(message="ComNotConnected", port=self.port))
			self.com_connected = False
			return

		self.ser.flushInput()
		self.ser.flushOutput()

		while True:
			if self.read_serial_data:
				self.f.write(self.ser.readline().decode('utf-8'))

			# If GUI is closed, stop this thread so python can exit fully
			if self.stop.is_set():
				self._logger.info("The serial thread for port {} is being shut down.".format(self.port))
				if self.f:
					self.f.close()
				self.com_connected = False
				return

	def on_event(self, event, payload):
		if event == octoprint.events.Events.PRINT_STARTED:
			if self.com_connected:
				if self.save_path is not None:
					self.f = open(self.save_path, "x")
					self.read_serial_data = True
					self._logger.info("Starting read from serial port {}...".format(self.port))
					self._plugin_manager.send_plugin_message(self._identifier, dict(message="data_collected"))

		if event == octoprint.events.Events.PRINT_DONE or \
				event == octoprint.events.Events.PRINT_FAILED or \
				event == octoprint.events.Events.PRINT_CANCELLING:
			if self.read_serial_data:
				self.read_serial_data = False
				self.f.close()

	def validate_save_path(self):
		escaped_port = re.sub('[^A-Za-z0-9]+', '_', self.port)
		dot_index = self.save_path.index(".")
		self.save_path = self.save_path[:dot_index] + escaped_port + self.save_path[dot_index:]
		self._logger.info("Save path for com port {} modified: {}".format(self.port, self.save_path))
		append_num = 1
		dot_index = self.save_path.index(".")
		new_save_path = self.save_path
		while path.exists(new_save_path):
			new_save_path = self.save_path[:dot_index] + "(" + str(append_num) + ")" + self.save_path[dot_index:]
			append_num += 1
		self.save_path = new_save_path
		self._logger.info("Final save path: {}".format(self.save_path))


class StretchingStagePlugin(octoprint.plugin.StartupPlugin,
							octoprint.plugin.TemplatePlugin,
							octoprint.plugin.AssetPlugin,
							octoprint.plugin.EventHandlerPlugin,
							octoprint.plugin.SettingsPlugin,
							octoprint.plugin.SimpleApiPlugin):
	stop = threading.Event()
	comPorts = []

	def on_shutdown(self):
		self.stop.set()

	def on_stop(self):
		self.stop.set()

	def on_after_startup(self):
		self._logger.info("Stretching Stage controller starting up...")

	def get_assets(self):
		return dict(
			js=["js/stretchingstagecontroller.js"]
		)

	def start_serial_thread(self, port):
		threading.Thread(target=port.serial_thread).start()

	def on_event(self, event, payload):

		for p in self.comPorts:
			p.on_event(event, payload)

		if event == octoprint.events.Events.PRINT_STARTED:
			self._logger.info("Print started.")

		if event == octoprint.events.Events.PRINT_DONE:
			self._logger.info("Print completed successfully.")

		if event == octoprint.events.Events.PRINT_FAILED:
			self._logger.info("Print failed.")

		if event == octoprint.events.Events.PRINT_CANCELLING:
			self._logger.info("Print cancelled.")

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False),
			dict(type="tab", custom_bindings=False)
		]

	def get_settings_defaults(self):
		return dict(
			save_path="/home/pi"
		)

	def get_api_commands(self):
		return dict(
			fetchPorts=[],
			validateSettings=["save_path", "file_name"],
			connectCOM=["serial_read_port"],
			disconnectCOM=[]
		)

	def on_api_command(self, command, data):
		if command == "fetchPorts":
			if data["type"] == "available":
				list_of_ports = [p.__dict__ for p in serial.tools.list_ports.comports()]
				self._plugin_manager.send_plugin_message(self._identifier, dict(message="ports_fetched",
																				ports=list_of_ports,
																				type=data["type"]))
			elif data["type"] == "currently_connected":
				self._plugin_manager.send_plugin_message(self._identifier, dict(message="ports_fetched",
																				ports=self.comPorts,
																				type=data["type"]))

		if command == "validateSettings":
			if "save_path" in data:
				self._logger.info("Parameters Received. Save path is {save_path}".format(**data))
				dir_exists = path.exists("{save_path}".format(**data))
				if "{save_path}".format(**data)[-1] != "/":
					self._plugin_manager.send_plugin_message(self._identifier, dict(message="path_missing_slash"))
				else:
					if dir_exists:
						self._logger.info("Settings directory exists and is ready for readout.")
						self._logger.info("New file(s) being created.")
						self._plugin_manager.send_plugin_message(self._identifier, dict(message="valid_filename"))
						for p in self.comPorts:
							p.save_path = "{save_path}{file_name}".format(**data)
							p.validate_save_path()
					else:
						self._logger.warning(
							"*******WARNING******** Save directory for Stretching Stage Controller does not exist!"
							" Please pick a valid save directory")
						self._plugin_manager.send_plugin_message(self._identifier, dict(message="path_does_not_exist"))

		if command == "connectCOM":
			if "serial_read_port" in data:
				self.comPorts = []
				ports = [p for p in data["serial_read_port"]]
				self._logger.info("connectCOM called. Port(s) detected: {}".format(ports))
				for p in ports:
					new_com = CommunicationPort(p,
												self._logger,
												self._plugin_manager,
												self._identifier)
					self.comPorts.append(new_com)
					self.start_serial_thread(new_com)

		if command == "disconnectCOM":
			for p in self.comPorts:
				p.stop.set()
			self.stop.set()
			self._plugin_manager.send_plugin_message(self._identifier, dict(message="com_disconnected"))


__plugin_name__ = "Stretching Stage Controller"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = StretchingStagePlugin()

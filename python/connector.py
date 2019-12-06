import subprocess, shlex;
import threading;
import re;
import time;
import sys;
from mytypes import *;

import ctypes;
from ctypes import wintypes;


hook = None

packet_history = [];
packet_queue = [];

current_id = 0x00; # 1 Byte long

on_message_event = None;



class Packet(object):
	def __init__(self, data):
		self._pid = None;
		self._c_uint8_array = None;
		self._c_double = None;
		self.acked = False;

		if (isinstance(data, list)):
			# array of c_uint8
			self._pid = data[0].value;
			self._c_uint8_array = data;
			self._c_double = uint8_array_to_double(data);
		elif (isinstance(data, ctypes.c_double)):
			# double
			self._c_double = data;
			self._c_uint8_array = double_to_uint8_array(data);
			self._pid = self._c_uint8_array[0].value;
		else:
			raise TypeError("Data must be array of c_uint8 or c_double");
			return;

	def get_pid(self):
		return self._pid;

	def get_c_double(self):
		return self._c_double;

	def get_c_uint8_array(self):
		return self._c_uint8_array[:];

	def update_c_uint8_array(self, new):
		self._pid = new[0].value;
		self._c_uint8_array = new;
		self._c_double = uint8_array_to_double(new);

	def update_c_double(self, new):
		self._c_double = new;
		self._c_uint8_array = double_to_uint8_array(new);
		self._pid = self._c_uint8_array[0].value;


def run_connector():
	global hook, packet_history, current_id, packet_queue;

	def run_scanner(command):
		pid = None;
		addresses = [];

		process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)

		lines_left = None

		while True:
			output = process.stdout.readline().decode().strip()
			if output == '' and process.poll() is not None:
				break
			if output:
				print(output)

				output_length = len(output)
				if output_length >= 7 and output[:7] == "found: ":
					num = output[7-output_length:]
					if (int(num) == 0):
						break;
					lines_left = int(num)
				elif "PID of LOTRO" in output:
					pid = int(output.split()[-1], 16);
				elif output[0:7] == "address":
					address = re.findall(r"address\: ([0-9a-fA-F]+).+", output)[0];
					addresses.append(int(address, 16));

					lines_left -= 1;
					if(lines_left == 0):
						process.kill();
						break;


		rc = process.poll()

		return pid, addresses


	print("The Great Vault python script by pydlv.");

	while True:
		print("Running scanner");

		pid, addresses = run_scanner("../scanner.exe");

		if (addresses):
			break;

		time.sleep(10);


	rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
	rPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPCVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
	rPM.restype = wintypes.BOOL
	wPM = ctypes.WinDLL('kernel32',use_last_error=True).WriteProcessMemory
	wPM.argtypes = [wintypes.HANDLE,wintypes.LPCVOID,wintypes.LPCVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
	wPM.restype = wintypes.BOOL

	PROCESS_ALL_ACCESS = 0x1F0FFF

	processHandle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)


	def write_double(handle, address, value):
		buff = ctypes.c_double(float(value));
		bytes_written = ctypes.c_size_t();
		code = wPM(handle,address,ctypes.byref(buff),8,ctypes.byref(bytes_written))
		if not code:
			raise IOError("Failed with error: %s" % ctypes.get_last_error());
			return False;

		return bool(code);

	def read_double(handle, address):
		buff = ctypes.c_double();
		bytes_read = ctypes.c_size_t();
		code = rPM(handle,address,ctypes.byref(buff),8,ctypes.byref(bytes_read));
		if not code:
			raise IOError("Failed with error: %s" % ctypes.get_last_error());
			return False;
		return buff.value;



	# Synchronize with LOTRO/confirm we have the right address

	print("Attempting to start communication with plugin.");

	if(not pid):
		print("Could not find lotroclient.exe");
		sys.exit(0);

	def zero_array():
		return [ctypes.c_uint8(0) for i in range(8)]


	def get_next_id(val):
		if(val >= 255):
			return val % 254
		elif(val <= 0):
			return 0;
		else:
			return val + 1;

	def get_previous_id(val):
		if(val <= 1):
			return (256 - val) % 256
		else:
			return val - 1;

	assert(get_next_id(0) == 0);
	assert(get_next_id(255) == 1);
	assert(get_previous_id(0) == 0);
	assert(get_previous_id(1) == 255);


	def generate_new_packet():
		global current_id;

		while(True):
			current_id = get_next_id(current_id);
			if( current_id % 2 == 0 ):
				break;
		new_array = zero_array();
		new_array[0] = ctypes.c_uint8(current_id);
		new_packet = Packet(new_array);

		return new_packet;

	def tx_packet(packet):
		status = write_double(processHandle, hook, packet.get_c_double().value);

		if(not status):
			raise IOError("Failed to send packet.");

		return status;

	def queue_packet(packet):
		packet_queue.append(packet);


	for address in addresses:
		status = write_double(processHandle, address, 2.0);

	while hook is None:
		for address in addresses:
			value = read_double(processHandle, address);

			if(value == 1337):
				hook = address;
				break;

		time.sleep(.1);

	print("Confirmed hook at %s" % hex(address));





	message_history = [];

	current_message_rx = b"";


	def send_python_ready():
		new_arr = zero_array();
		new_arr[7] = ctypes.c_uint8(1);
		new_packet = Packet(new_arr);
		tx_packet(new_packet);

	try:
		while (True):
			current_read = read_double(processHandle, hook);
			read_packet = Packet(ctypes.c_double(current_read));
			#print(hex(ctypes.c_uint64.from_buffer_copy(read_packet.get_c_double()).value))
			arr = read_packet.get_c_uint8_array();

			just_finished_receiving = False;

			if(arr[0].value == 0):
				if(arr[7].value == 3):
					if(current_message_rx):
						just_finished_receiving = True;
					print("Received end message code.");
			else:
				message_slice = arr[1:];
				j = [i.value for i in message_slice]
				k = [l for l in j if l != 0];
				current_message_rx += bytes(k);

				if 0 in j:
					just_finished_receiving = True;

			if(just_finished_receiving):
				print("RECEIVED MESSAGE: ", current_message_rx);
				message_history.append(current_message_rx);

				if(on_message_event):
					on_message_event(current_message_rx);

				current_message_rx = b"";

			already_set = arr[0].value | arr[1].value | arr[2].value | arr[3].value |\
							arr[4].value | arr[5].value | arr[6].value == 0 and \
							arr[7].value == 1;

			if(not already_set):
				send_python_ready();
				
	except (Exception, ):
		send_python_ready();


	ctypes.windll.kernel32.CloseHandle(processHandle)

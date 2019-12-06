



##############################################

sys.exit(0);




previous_read = None

message_history = [];
current_message_rx = "";
currently_receiving = False;

def read_hook():
	global current_message_rx, currently_receiving;

	current_read = read_double(processHandle, hook);
	read_packet = Packet(ctypes.c_double(current_read));
	#print(hex(ctypes.c_uint64.from_buffer_copy(read_packet.get_c_double()).value))
	arr = read_packet.get_c_uint8_array();

	# Refer to reference.txt
	if (arr[0].value == 0):
		if (arr[7].value == 2 and arr[6].value >= 1 and arr[6].value <= 255):
			# The other side is claiming they didn't receive it, so
			# Look through the last 100 packets to try and find it
			requested_packet = None;
			
			for packet in packet_history[::-1]:
				if(packet.get_pid() == arr[6].value):
					requested_packet = packet;
					break;

			if(requested_packet):
				print("Resending packet %i because plugin claiming to \
					not have received it." % arr[6].value);
				requested_packet.acked = False;
				tx_packet(requested_packet);
				packet_history.remove(requested_packet);
				packet_history.append(requested_packet);
			else:
				print("Plugin requesting packet %i, which doesn't exist." % arr[6].value);

			return;

		elif(arr[7].value == 1 and arr[6].value % 2 == 0):
			pid_to_ack = arr[6].value;

			for packet in packet_history[::-1]:
				if(packet.get_pid() == pid_to_ack):
					packet.acked = True;

	elif (arr[0].value >= 1 and arr[0].value <= 255 and arr[0].value % 2 == 1):
		found_packet = None;
		for packet in packet_history[::-1]:
			if(packet.get_pid() == arr[0].value):
				found_packet = packet;
				break;

		if(found_packet is None):
			just_finished_receiving = False;

			if (arr[1].value + arr[2].value + arr[3].value + arr[4].value +\
				arr[5].value + arr[6].value == 0):
				if(arr[7].value == 0 or arr[7].value == 2):
					# Null/end message or start transmit new message
					if (currently_receiving):
						just_finished_receiving = True;

					if(arr[7].value == 2):
						print("Received packet to start reading message.");
						currently_receiving = True;
					else:
						currently_receiving = False;

			elif(currently_receiving):
				message_slice = arr[1:];
				j = [i.value for i in message_slice]
				k = [l for l in j if l != 0];
				current_message_rx += bytes(k).decode();

				if 0 in j:
					just_finished_receiving = True;
			else:
				print("Received message while not expecting to.");

			if(just_finished_receiving and current_message_rx):
				print("RECEIVED MESSAGE: ", current_message_rx);
				message_history.append(current_message_rx);
				current_message_rx = "";

			message_history.append(read_packet)
			if(len(message_history) > 100):
				message_history.pop(0);
		else:
			print("Plugin sent packet %i, which was already received." % arr[0].value);



		# Ack this PID
		new_arr = zero_array();
		new_arr[7] = ctypes.c_uint8(1);
		new_arr[6] = ctypes.c_uint8(arr[0].value);
		new_packet = Packet(new_arr);

		tx_packet(new_packet);

		return;


	else:
		print("Received invalid packet ID: %i" % arr[0].value);
		return;

while (False):
	read_hook();

	# Make sure we aren't missing any messages
	first_id = None;
	packet_ids = sorted([packet.get_pid() for packet in packet_history]);
	if(packet_history):
		first_id = packet_ids[0];

	should_break = False;

	if(first_id):
		if(first_id % 2 == 0):
			first_id += 1;

		for i, v in enumreate(range(first_id, first_id+(2*len(packet_history)+1), 2)):
			if(packet_ids[i] != v):
				print("Missing packet with ID %i" % i);

				# Request again.
				new_arr = zero_array();
				new_arr[7] = ctypes.c_uint8(2);
				new_arr[6] = ctypes.c_uint8(v);
				new_packet = Packet(new_arr);

				tx_packet(new_packet);

				should_break = True;
				break;

	if(should_break):
		break;

	# Ensure all our packets are acked if they need to be...
	for packet in sorted(packet_history, key=lambda x: x.get_pid()):
		if(not packet.acked):
			print("Packet %i is not Acked. Resending." % packet.get_pid());

			tx_packet(requested_packet);
			packet_history.remove(requested_packet);
			packet_history.append(requested_packet);

			should_break = True;

			break;

	if(should_break):
		break;

	if(packet_queue):
		oldest_packet = packet_queue.pop(0)
		tx_packet(oldest_packet);
		packet_history.append(oldest_packet);

# 	global previous_read;

# 	while(True):
# 		current_value = read_double(processHandle, hook);

# 		if(current_value != previous_read):
# 			previous_read = current_value;

# 			write_double(processHandle, hook, -2.0);

# 			return current_value

# MASKS = [
# 	0xff00000000000000,
# 	0x00ff000000000000,
# 	0x0000ff0000000000,
# 	0x000000ff00000000,
# 	0x00000000ff000000,
# 	0x0000000000ff0000,
# 	0x000000000000ff00,
# 	0x00000000000000ff
# ];

# try:
# 	current_rx = "";
# 	while (True):
# 		value = read_hook();

# 		#value = -1.0;

# 		if (value == -1.0):
# 			while (True):
# 				value = read_hook();
# 				#value = 0xd09f006500790000;

# 				if ( current_rx and (value == -1.0 or value == 0) ):
# 					print("RECEIVED MESSAGE: ", current_rx);
# 					print(current_rx.encode("utf-8"))
# 					messages.append(current_rx);
# 					current_rx = "";
# 					break;

# 				byte_array = [];
# 				for i, mask in enumerate(MASKS):
# 					byte_array.append( (mask & value) >> (56-(i*8)) );

# 				byte_string = bytes([i for i in byte_array if i != 0]);

# 				current_rx += byte_string.decode();

# 				if 0 in byte_array:
# 					print("RECEIVED MESSAGE: ", current_rx);
# 					print(current_rx.encode("utf-8"))
# 					messages.append(current_rx);
# 					current_rx = "";
# 					break;
# except (KeyboardInterrupt, ):
# 	print("Attempting to unfreeze LOTRO.");
# 	while (True):
# 		write_double(processHandle, hook, -2.0);
















# def encode_packet(packet_id, body):
# 	# Ensure the first byte is blank, otherwise it will be lost
# 	if ( int(body) & 0x00ffffffffffffff != int(body) ):
# 		raise ValueError("The first byte is reserved for packet ID.");
# 		return;

# 	if (packet_id < 0 or packet_id > 255):
# 		raise ValueError("Packet ID must be between 0 and 255.");
# 		return;

# 	return (packet_id << 56) | int(body);


# def decode_packet(packet):
# 	packet_id = packet >> 56;
# 	body = packet & 0x00ffffffffffffff;
# 	return packet_id, body;



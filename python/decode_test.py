import ctypes
import io;
from bitfloat import float_and, float_or;

def double_to_int(val):
	return ctypes.c_longlong.from_buffer(ctypes.c_double(val))

def ctype_to_bin(val):
	fakefile = io.BytesIO()
	fakefile.write(val)
	return fakefile.getvalue()

def form_packet(packet_id, body):
	# Ensure the first byte is blank, otherwise it will be lost
	if (float_and(body & 0x00ffffffffffffff) != body):
		raise ValueError("The first byte is reserved for packet ID.");
		return;

	if (packet_id < 0 or packet_id > 255):
		raise ValueError("Packet ID must be between 0 and 255.");
		return;

	return (packet_id << 56) | body;


def decode_packet(packet):
	packet_id = packet >> 56;
	body = packet & 0x00ffffffffffffff;
	return packet_id, body;

j = ctypes.c_uint64.from_buffer_copy(ctypes.c_double(1));
print(j.value);
print(bin(j.value));
print(len(bin(j.value)))

k = ctypes.c_double.from_buffer_copy(j).value;
print(k);

input()

print(j);
packet_id = 0x0C;
print("ID: ", hex(packet_id));
print("Body: ", hex(j));
p = form_packet(packet_id, j)
print(hex(p))


print("Decoded");
d_id, d_body = decode_packet(p);
print("ID: ", hex(d_id))
print("Body: ", hex(d_body));

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

# messages = [];

# current_rx = "";
# while (True):
# 	#value = get_next_value();

# 	value = -1.0;

# 	if (value == -1.0):
# 		while (True):
# 			#value = get_next_value();
# 			value = 0xd09f006500790000;

# 			byte_array = [];
# 			for i, mask in enumerate(MASKS):
# 				byte_array.append( (mask & value) >> (56-(i*8)) );

# 			byte_string = bytes([i for i in byte_array if i != 0]);

# 			current_rx += byte_string.decode();

# 			if 0 in byte_array:
# 				print("RECEIVED MESSAGE: ", current_rx);
# 				print(current_rx.encode("utf-8"))
# 				messages.append(current_rx);
# 				current_rx = "";
# 				break;

# 	input()
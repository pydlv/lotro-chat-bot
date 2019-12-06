import ctypes;
import random;

def uint8_array_to_double(arr):
	num = 0;
	for i, c_val in enumerate(arr):
		num |= c_val.value << (56-(i*8))

	num_uint64 = ctypes.c_uint64(num);
	
	result = ctypes.c_double.from_buffer_copy(num_uint64);

	return result;

def double_to_uint8_array(val):
	result = [];

	num = ctypes.c_uint64.from_buffer_copy(val).value;

	for i in range(8):
		mask = 0xff << (8*(7-i))
		j = (num & mask) >> (8*(7-i));
		result.append(ctypes.c_uint8(j))

	return result;


if __name__ == "__main__":
	# Run tests

	arr = [ctypes.c_uint8(random.randint(0, 255)) for i in range(8)]

	val_double = uint8_array_to_double(arr);

	val_arr = double_to_uint8_array(val_double);

	print("Original:");
	print(arr);
	print("Cast back:");
	print(val_arr);
	print("They should be the same.");
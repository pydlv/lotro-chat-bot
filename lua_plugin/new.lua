packet_history = {};
packet_queue = {};

current_id = 0x00;

Packet = class();

function Packet:Constructor(data)
	self._pid = nil;
	self._c_uint8_array = nil;
	self._c_double = nil;
	self.acked = false;

	if(type(data) == "table") then
		-- array of c_uint8
		self._pid = data[1].value;
		self._c_uint8_array = data;
		self.double = uint8_array_to_double(data);
	else if (getmetatable(data) == ctypes.c_double) then
		-- double
		self._c_double = data;
		self._c_uint8_array = double_to_uint8_array(data);
		self._pid = self._c_uint8_array[1].value;
	else
		DebugOut("Data must be array of c_uint8 or c_double");
		assert(false);
	end
end

function Packet:get_pid()
	return self._pid;
end

function Packet:get_c_double()
	return self._c_double;
end

function Packet:get_c_uint8_array()
	-- make sure this returns a copy (don't return the original)
	return self._c_uint8_array;
end

function Packet:update_c_uint8_array(new)
	self._pid = new[1].value;
	self._c_uint8_array = new;
	self._c_double = uint8_array_to_double(new);
end

function Packet:update_c_double(new)
	self._c_double = new;
	self._c_uint8_array = double_to_uint8_array(new);
	self._pid = self._c_uint8_array[1].value;
end


function zero_array()
	local result = {};

	for i = 1, 8 do
		table.insert(result, ctypes.c_uint8(0));
	end

	return result;
end


function get_next_id(val)
	if(val >= 255) then
		return val % 254
	else if (val <= 0) then
		return 0;
	else
		return val + 1;
	end
end

function get_previous_id(val)
	if(val <= 1) then
		return (256 - val) % 256
	else
		return val - 1;
	end
end

assert(get_next_id(0) == 0);
assert(get_next_id(255) == 1);
assert(get_previous_id(0) == 0);
assert(get_previous_id(1) == 255);


function generate_new_packet()
	repeat 
		current_id = get_next_id(current_id)
	until current_id % 2 == 1;

	new_array = zero_array();
	new_array[1] = ctypes.c_uint8(current_id);
	new_packet = Packet(new_array);

	return new_packet;
end


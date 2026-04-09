local path = getfenv(1)._.Name;

import "Turbine";
import "Turbine.Gameplay";
import "Turbine.UI";
import "Turbine.UI.Lotro";

-- keep the order
import (path .. ".utf8");
import (path .. ".utf8upperMap");
import (path .. ".utf8lowerMap");
import (path .. ".bit");
bit32 = _G.M;

function DebugOut(arg)
	message = "";

	if (type(arg) == "table") then
		for k, v in pairs(arg) do
			message = message .. tostring(k) .. ": " .. tostring(v) .. "\n"
		end
	else
		message = tostring(arg);
	end

	Turbine.Shell.WriteLine(message)
end

DebugOut("The Great Vault Plugin loaded")

-- Variable that gets hooked onto
local hook = 29382838;

local my_username = Turbine.Gameplay.LocalPlayer.GetInstance():GetName();

shellCommand=Turbine.ShellCommand();
shellCommand.Execute = function(sender, cmd, args)
	DebugOut(hook)
end
Turbine.Shell.AddCommand("thing",shellCommand);

shellCommand2=Turbine.ShellCommand();
shellCommand2.Execute = function(sender, cmd, args)
	hook = hook + 1
	DebugOut(hook)
end
Turbine.Shell.AddCommand("inc",shellCommand2);


Timer=class(Turbine.UI.Window);

function Timer:Constructor( delay, callback )
	Turbine.UI.Window.Constructor( self );

	self:SetWantsUpdates(true);
	self.Changed=true;

	self.delay = delay;
	self.start_time = Turbine.Engine:GetLocalTime();
	self.callback = callback;

	self.Update=function()
		if (Turbine.Engine.GetLocalTime() - self.start_time >= self.delay ) then
			self:SetWantsUpdates(false);
			self.callback();
			return;
		end
	end
end


local my_string = "ПфышояА"


local lock = false;
local message_queue = {};


-- Returns true if succeeded else false
function tx_double(double)
	if (not lock) then
		lock = true;

		-- This looks so paradoxical but it should work...
		repeat hook = -1 until hook == -2;

		-- We have been ACK so go ahead and tx
		repeat hook = double until hook == -2;

		-- Signal end of tx
		repeat hook = 0 until hook == -2;

		lock = false;

		return True;
	else
		return false;
	end
end


function check_queue()
	while (#message_queue) do
		if (not lock) then
			head = table.remove(message_queue, 1);

			repeat
				success = tx_double(head);
			until success == true;
		end
	end
end

function readDouble(bytes) 
  local sign = 1
  local mantissa = bytes[2] % 2^4
  for i = 3, 8 do
	mantissa = mantissa * 256 + bytes[i]
  end
  if bytes[1] > 127 then sign = -1 end
  local exponent = (bytes[1] % 128) * 2^4 + math.floor(bytes[2] / 2^4)
  
  if exponent == 0 then
	return 0
  end
  mantissa = (math.ldexp(mantissa, -52) + 1) * sign
  return math.ldexp(mantissa, exponent - 1023)
end

function writeDouble(num)
  local bytes = {0,0,0,0, 0,0,0,0}
  if num == 0 then
	return bytes
  end
  local anum = math.abs(num)
  
  local mantissa, exponent = math.frexp(anum)
  exponent = exponent - 1
  mantissa = mantissa * 2 - 1
  local sign = num ~= anum and 128 or 0
  exponent = exponent + 1023
  
  bytes[1] = sign + math.floor(exponent / 2^4)
  mantissa = mantissa * 2^4
  local currentmantissa = math.floor(mantissa)
  mantissa = mantissa - currentmantissa
  bytes[2] = (exponent % 2^4) * 2^4 + currentmantissa
  for i= 3, 8 do
	mantissa = mantissa * 2^8
	currentmantissa = math.floor(mantissa)
	mantissa = mantissa - currentmantissa
	bytes[i] = currentmantissa
  end
  return bytes
end


python_ready = 5e-324;
finished_tx = 1.5e-323;

function continue()
	DebugOut("Ready")
	hook = 1337

	-- packet = readDouble({0x03, 0x68, 0x69, 0x00, 0x00, 0x00, 0x00, 0x00})

	-- hook = packet

	-- while(hook ~= python_ready) do
	-- 	local n = 1+1; -- we're just waiting
	-- end


	-- hook = finished_tx;

	-- DebugOut("Done! :D");
	

	-- correct value
	-- hook = 3.05762892619533E-292



	-- repeat hook = 3 until hook == -2;

	-- message1 = 0xCCCCCCCCCCCCCCCC;
	-- message2 = 0xFFFFFFFFFFFFFFFF;

	-- table.insert(message_queue, message1);
	-- table.insert(message_queue, message2);

	-- check_queue();
end

-- Wait for first comm
function n()
	j = Timer(1, function()
		if ( hook ~= 2 ) then
			-- DebugOut("Not ready")
			n()
		else
			continue()
		end
	end)
end

n()

send_queue = {};

lock = false;

function wait_for_ready()
	while(hook ~= python_ready) do
		local n = 1+1;
	end
	return;
end

function empty_queue()
	if(not lock and hook == python_ready) then
		lock = true;

		while (#send_queue > 0) do
			head = table.remove(send_queue, 1);

			for i, bytes in pairs(head) do
				packet = readDouble(bytes)

				hook = packet

				wait_for_ready();
			end

			hook = finished_tx;

			wait_for_ready()
		end

		lock = false;
	else
		return;
	end
end


function Turbine.Chat:Received(args)
	local message = args.Message;

	local needed = 7-(#message % 7);

	for i=1, needed do
		message = message .. string.char(0);
	end

	local msg_bytes = {};

	for i=1, #message/7 do
		local byte_group = {0x03};
		for j=1, 7 do
			table.insert(byte_group, string.byte(message, (i-1)*7 + j));
		end
		table.insert(msg_bytes, byte_group);
	end

	table.insert(send_queue, msg_bytes);

	empty_queue();
end




function asdf()

	local num_groups = #message / 7

	local whole_groups = math.floor(num_groups);
	local num_remainder = #message % 7;
	local num_trailing_zeros = 7 - num_remainder;

	local ranges = {}
	for i = 1, whole_groups do
		table.insert(ranges, {(i-1)*7+1, (i-1)*7+8})
	end

	local parts = {}
	for i, v in pairs(ranges) do
		-- Don't through v[1] but not including v[2] i.e. [v[1], v[2])
		table.insert(parts, string.sub(message, v[1], v[2]-1))
		DebugOut(parts[i]);
	end

	if (num_remainder) then
		local trailing_zeros = ""
		for i=1, num_trailing_zeros do
			trailing_zeros = trailing_zeros .. string.char(0);
		end

		table.insert(parts, string.sub(message, -num_remainder) .. trailing_zeros);
	end

	for i, part in pairs(parts) do
		--DebugOut(part);
	end

	-- for _, part in pairs(parts) do
	-- 	local dub = 0;

	-- 	for i = 1, 7 do
	-- 		local int1 = string.byte(part, i);

	-- 		dub = bit32.bor( bit32.lshift(int1, 8*(i-1)) , dub )
	-- 	end
	-- end

end
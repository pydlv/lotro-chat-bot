local path = getfenv(1)._.Name;

import "Turbine";
import "Turbine.Gameplay";
import "Turbine.UI";
import "Turbine.UI.Lotro";

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
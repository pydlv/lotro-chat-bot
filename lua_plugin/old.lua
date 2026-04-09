local num_groups = #my_string / 8

local whole_groups = math.floor(num_groups);
local num_remainder = #my_string % 8;
local num_trailing_zeros = 8 - num_remainder;

local ranges = {}
for i = 1, whole_groups do
	table.insert(ranges, {i, i+8})
end

local parts = {}
for i, v in pairs(ranges) do
	-- Don't through v[1] but not including v[2] i.e. [v[1], v[2])
	table.insert(parts, string.sub(my_string, v[1], v[2]-1))
end

if (num_remainder) then
	local trailing_zeros = ""
	for i=1, num_trailing_zeros do
		trailing_zeros = trailing_zeros .. string.char(0);
	end

	table.insert(parts, string.sub(my_string, -num_remainder) .. trailing_zeros);
end

for i, part in pairs(parts) do
	DebugOut(part);
end

DebugOut(whole_groups)
DebugOut(num_trailing_zeros)


--create lookup table for octal to binary
oct2bin = {
    ['0'] = '000',
    ['1'] = '001',
    ['2'] = '010',
    ['3'] = '011',
    ['4'] = '100',
    ['5'] = '101',
    ['6'] = '110',
    ['7'] = '111'
}
function getOct2bin(a) return oct2bin[a] end
function convertBin(n)
    local s = string.format('%o', n)
    s = s:gsub('.', getOct2bin)
    return s
end


for _, part in pairs(parts) do
	local dub = 0;

	for i = 1, 8 do
		local int1 = string.byte(part, i);

		DebugOut(_G.M.tohex(int1));
		DebugOut(_G.M.tohex(bit32.lshift(int1, 8*(i-1))));

		dub = bit32.bor( bit32.lshift(int1, 8*(i-1)) , dub )
	end

	DebugOut(dub);
end


-- bytes = {}
-- for i = 1, #my_string do
-- 	table.insert(bytes, string.byte(my_string, i))
-- end

-- for i = 1, #bytes do
-- 	DebugOut(i);
-- 	DebugOut(bytes[i])
-- end


-- raw_message = args.Message;

	-- -- remove tags (risky)
	-- local plain = function(str)
	-- 	return string.gsub(utf8.printable(str), "<[^>]+>", "");
	-- end

	-- local plainMessage = raw_message; --plain(raw_message);

	-- -- the timestamp is not a part of the message (chat option), that's fine
	-- -- format -> [channel] user: 'text'
	-- local channel, username, text = string.match(plainMessage, "^%[([^%]]+)%]%s+([^:']+):%s+'(.*)'$");
	-- local message = text;

	-- if not channel or not username or not text then
	-- 	-- if the post is from current player
	-- 	-- format -> [To channel] 'text'
	-- 	channel, message = string.match(plainMessage, "^%[([^%]]+)%]%s+'(.*)'$");

	-- 	if not channel or not text then
	-- 		Turbine.Shell.WriteLine("oops, unable to parse the message");
	-- 		Turbine.Shell.WriteLine(plainMessage);
	-- 		return;
	-- 	end

	-- 	username = my_username;
	-- end


	-- DebugOut("Channel: " .. channel);
	-- DebugOut("Username: " .. username);
	-- DebugOut("Message: " .. message);

	-- Turbine.PluginData:Load(Turbine.DataScope.Account, "chat_logs", function(data) 
	-- 	return;
	-- end)

	-- Turbine.PluginData:Save(Turbine.DataScope.Account, "latest_chat", message, function(success, err)
	-- 	DebugOut("Callback function called.")
	-- 	DebugOut(success)
	-- 	DebugOut(err)
	-- 	return;
	-- end)

	-- Turbine.PluginData.Save(Turbine.DataScope.Account, "latest_chat", message);
-- not exactly, but helps
utf8 = {};

-- returns the number of characters
utf8.len = function(str)
	return string.len(string.gsub(str, "[\128-\191]*", ""));
end

-- removes control characters
utf8.printable = function(str)
	return string.gsub(str, "[^\32-\126\192-\253\128-\191]*", "");
end

-- returns an iterator over all printable ascii and unicode characters and optional the linefeed
utf8.chars = function(str, linefeed)
	local n;

	if linefeed then
		n = string.gfind(str, "([\n\32-\126\192-\253][\128-\191]*)");
	else
		n = string.gfind(str, "([\32-\126\192-\253][\128-\191]*)");
	end

	return function()
		return n();
	end
end

-- returns an iterator over all words with ascii letters and unicode letter
utf8.words = function(str)
	local n = utf8.chars(str);

	return function()
		local word = {};

		for c in n do 
			if utf8.upperMap[c] or utf8.lowerMap[c] then
				table.insert(word, c);
				break;
			end
		end

		if not (#word > 0) then 
			return nil;
		end

		for c in n do
			if not utf8.upperMap[c] and not utf8.lowerMap[c] then 
				break;
			end

			table.insert(word, c);
		end

		return table.concat(word, "");
	end
end

-- converts lower case letters to upper case
utf8.upper = function(str)
	local buff = {};

	for c in utf8.chars(str) do
		table.insert(buff, utf8.upperMap[c] or c);
	end

	return table.concat(buff, "");
end

-- converts upper case letters to lower case
utf8.lower = function(str)
	local buff = {};

	for c in utf8.chars(str) do
		table.insert(buff, utf8.lowerMap[c] or c);
	end

	return table.concat(buff, "");
end

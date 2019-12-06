import threading;
import connector;
import time;
import discord;
import asyncio;
import re;


connector_thread = threading.Thread(target=connector.run_connector);
connector_thread.start();


bot_ready = False;
server = None;

SERVER_ID = 571149619162251274;
WORLD_CHANNEL_ID = 571149731690971156;

world_channel = None;

waiting_to_send = [];


client = discord.Client();

async def uptime_count():
	await client.wait_until_ready();
	global up_hours;
	global up_minutes;
	up_hours = 0;
	up_minutes = 0;

	while(not client.is_closed):
		await asyncio.sleep(60);
		up_minutes += 1;
		if(up_minutes == 60):
			up_minutes = 0;
			up_hours += 1;

async def message_sender():
	await client.wait_until_ready();

	while(not client.is_closed()):
		await asyncio.sleep(.1);
		if(waiting_to_send and bot_ready):
			if(world_channel):
				head = waiting_to_send.pop(0);
				await world_channel.send(head);
			else:
				print("World channel is None!");


@client.event
async def on_server_join(server):
	try:
		await client.send_message(server.owner, f"Hey, you or an admin on your server invited me to '{server.name}'. :smiley:\n"
												"The default prefix is `/`, so type `/help` into a text channel "
												"on the server to see what you "
												"(or rather I) can do.")

		if(server.default_channel is not None):
			await client.send_message(server.default_channel, "Hey, I'm glad to be here. "
																"Hopefully I'll be helpful :smiley:.\n"
																"Type `/help` to see all available commands.");

	except discord.errors.Forbidden:
		pass;


def sanitize_message(message):
	matches = re.findall(r'((?:\<\w+\:[^\>]*\>)|(?:\<\\\w+\>)|(?:\<\w+\=[^\>]*\>)|(?:\<\/rgb\>))', message);
	for match in matches:
		message = message.replace(match, "");

	return message;


def on_ingame_message(message):
	print("Callback called.");
	if(bot_ready):
		# client.loop.create_task(client.send_message(server.default_channel, message));
		try:
			decoded = sanitize_message(message.decode());
		except (UnicodeDecodeError):
			print("Coudln't decode message: ", message);
			return;

		is_world = re.match(r'\[World\] \w+\: \'.+\'', decoded);
		if(is_world):
			waiting_to_send.append(decoded);


@client.event
async def on_message(message):
	#print(message.content);
	pass;


@client.event
async def on_ready():
	global bot_ready, server, world_channel;
	print(client.user.name);
	print("-" * 10);

	server = client.get_guild(id=str(SERVER_ID));

	# world_channel = discord.utils.get(server.channels, id=str(WORLD_CHANNEL_ID));

	world_channel = client.get_channel(WORLD_CHANNEL_ID);

	bot_ready = True;


connector.on_message_event = on_ingame_message;

client.loop.create_task(uptime_count());
client.loop.create_task(message_sender());
client.run("NTY4MTE3NTg3MzgxMzIxNzMy.XLda6A.PUCP2nMIIjGltqA-fUQ-_ZIJTJE");
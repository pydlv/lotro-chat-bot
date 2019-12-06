import discord;
import asyncio;

client = discord.Client();

@client.event
async def on_ready():
	print(client.user.name);
	print("-" * 10);

	guilds = await client.fetch_guilds().flatten();

	for guild in guilds:
		print("Leaving %s" % guild.name);
		await guild.leave();

client.run("NTY4MTE3NTg3MzgxMzIxNzMy.XLda6A.PUCP2nMIIjGltqA-fUQ-_ZIJTJE");
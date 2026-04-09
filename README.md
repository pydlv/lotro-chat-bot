# lotro-chat-bot

A bot that bridges **Lord of the Rings Online (LOTRO)** in-game chat to a **Discord** channel. It reads [World] chat messages from the game client in real time and forwards them to a configured Discord server channel.

---

## Architecture

The system has three layers:

```
┌──────────────────────────────────────┐
│  LOTRO game client (lotroclient.exe) │
│  Lua plugin exposes a "hook"         │
│  (a double in process memory)        │
└────────────────┬─────────────────────┘
                 │  shared memory (one 8-byte float)
                 │  ReadProcessMemory / WriteProcessMemory
                 ▼
┌──────────────────────────────────────┐
│  connector.py  (Python, Windows)     │
│  Scans for the hook address,         │
│  reads/decodes incoming packets      │
└────────────────┬─────────────────────┘
                 │  on_message_event callback
                 ▼
┌──────────────────────────────────────┐
│  __init__.py – Discord bot           │
│  Sanitizes and forwards [World]      │
│  messages to a Discord channel       │
└──────────────────────────────────────┘
```

### Components

| File | Role |
|------|------|
| `lua_plugin/__init__.lua` | LOTRO Lua plugin entry point. Listens for chat messages and streams them to Python via the shared hook variable. |
| `python/__init__.py` | Entry point. Starts the connector thread and runs the Discord bot. |
| `python/connector.py` | Core IPC logic. Discovers the hook address, polls it for packets, and fires `on_message_event` when a full message is received. |
| `python/mytypes.py` | Utility functions: converts between an 8-byte `c_uint8` array and a `c_double` (the wire format). |
| `cpp/main.cpp` | C++ source for `scanner.exe`. Scans LOTRO's process memory for the hook address. |

---

## Inter-Process Communication Scheme

LOTRO does not expose a public API, so the bot communicates with a LOTRO Lua plugin via a **single shared `double` (8-byte IEEE 754 float)** located inside the LOTRO process's address space.

### How the hook address is found

1. The LOTRO Lua plugin allocates a local variable with a known sentinel value and watches a `double` at a stable address.
2. At startup, `scanner.exe` (built from `cpp/main.cpp`) scans LOTRO's virtual memory for the sentinel and prints the address.
3. Python opens a handle to the LOTRO process with `PROCESS_ALL_ACCESS` and uses `ReadProcessMemory` / `WriteProcessMemory` to read and write that address.

### Packet format

Every message is encoded as a sequence of **8-byte packets**. The 8-byte `double` is reinterpreted as an array of 8 `uint8` bytes (`b1`–`b8`, most-significant byte first):

```
b1  b2  b3  b4  b5  b6  b7  b8
```

| Field | Meaning |
|-------|---------|
| `b1` | **Packet ID / control discriminator.** `0` = control packet; any other value = data packet ID. |
| `b2`–`b7` | **Payload bytes** for data packets (up to 6 bytes of UTF-8 text per packet). |
| `b8` | **Control byte** (used when `b1 == 0`). |

### Control codes (`b1 == 0`)

| `b8` value | Meaning |
|------------|---------|
| `1` | **Python ready** – Python signals it is idle and ready to receive. |
| `3` | **End of message** – The plugin has finished transmitting a message. |

### Message reception flow

1. Python polls the hook address in a tight loop.
2. When `b1 != 0`, the packet carries data: bytes `b2`–`b7` are appended to the in-progress message buffer (trailing `0x00` bytes are stripped).
3. When a `0x00` appears within `b2`–`b7`, or a control packet with `b8 == 3` arrives while the buffer is non-empty, the message is considered complete.
4. The completed byte string is passed to `on_message_event`, which decodes it, strips LOTRO XML colour tags, and (if it matches the `[World]` chat pattern) queues it for the Discord bot to forward.
5. After each read, if the value is not already the "Python ready" sentinel, Python writes the ready signal (`b8 = 1`, all other bytes `0`) to acknowledge and reset the hook.

### Packet ID assignment

Data packets sent **from** Python use even-numbered IDs (2, 4, 6, …, 254, then wrapping to 2); data packets sent **from** the plugin use odd-numbered IDs. ID `0` is reserved for control packets.

---

## Lua Plugin (`lua_plugin/`)

The LOTRO Lua plugin lives in `lua_plugin/` and runs inside the game client. It is a standard LOTRO Turbine plugin loaded from the in-game Plugin Manager.

### Startup handshake

1. On load, the plugin initialises `hook` to the sentinel value `29382838` and starts polling every second.
2. Python writes `2.0` to the hook address to signal it is ready.
3. When the plugin sees `hook == 2`, it calls `continue()`, which sets `hook = 1337`.
4. Python detects `hook == 1337` and records the confirmed hook address. Normal operation begins.

### Chat message transmission

The plugin registers a `Turbine.Chat:Received` handler. When any chat message arrives:

1. The message string is padded with `\0` bytes to the nearest multiple of 7.
2. It is split into 7-byte chunks. Each chunk is prefixed with `0x03` (the packet-ID byte) to form an 8-byte group.
3. The groups are pushed onto `send_queue`.
4. `empty_queue()` drains the queue: for each group it calls `readDouble()` to convert the 8 bytes into a `double`, writes that value to `hook`, then spin-waits until Python acknowledges by writing `python_ready` (`5e-324`) back.
5. After the last group, the plugin writes `finished_tx` (`1.5e-323`) to signal end-of-message.

---

## Setup

> **Platform:** Windows only (requires `ReadProcessMemory` / `WriteProcessMemory`).

### Prerequisites

- Python 3.6+
- `discord.py` library (`pip install discord.py`)
- LOTRO with the `lua_plugin/` plugin installed via the in-game Plugin Manager
- `scanner.exe` compiled from `cpp/main.cpp` and placed at the **repository root**

### Configuration

Edit `python/__init__.py` and set:

| Constant | Description |
|----------|-------------|
| `SERVER_ID` | Discord guild (server) ID to post to |
| `WORLD_CHANNEL_ID` | ID of the Discord text channel for [World] chat |

Replace the placeholder `YOUR_DISCORD_BOT_TOKEN_HERE` in `client.run(...)` with your Discord bot token. **Do not commit the token to version control.**

### Running

```
cd python
run.bat
```

Or directly:

```
cd python
python __init__.py
```

The bot will:
1. Launch a background thread running `connector.py`.
2. Wait for the scanner to locate the LOTRO hook address.
3. Begin polling the hook and forwarding [World] chat messages to Discord.

import os
import socket
import multiprocessing as mp
from typing import Any
from queue import Empty

import discord
from discord import Intents
from discord.ext import tasks
from dotenv import load_dotenv


class Client(discord.Client):
    def __init__(self, queue: mp.Queue, channel_id: int, *, intents: Intents, **options: Any) -> None:
        super().__init__(intents=intents, **options)
        self.q = queue
        self.channel_id = channel_id

    async def setup_hook(self) -> None:
        self.check_server.start()
        

    @tasks.loop(seconds=5)
    async def check_server(self):
        try:
            data: str = self.q.get(block=False)
            channel = self.get_channel(self.channel_id)
            await channel.send(data)
        except Empty:
            pass

    @check_server.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in


SOCKET_FILE = '/tmp/dc_unix_socket'

def start_server(queue: mp.Queue):
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)
        s.bind(SOCKET_FILE)

        print(f"Server listening on 8899...")
        while True:
            data, address = s.recvfrom(1024)
            buf = []
            # print(f"Received {data.decode()} from {address}")
            buf.append(data.decode())

            msg = str.join("", buf)
            queue.put(msg)


def main():
    q = mp.Queue()
    p = mp.Process(target=start_server, args=(q,))
    p.start()


    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    CHANNEL_ID = os.getenv('DISCORD_CHANNEL')
    assert TOKEN is not None
    assert CHANNEL_ID is not None


    intents = discord.Intents.default()
    intents.message_content = True
    client = Client(q, int(CHANNEL_ID), intents=intents)

    client.run(TOKEN)

    p.join()


if __name__ == "__main__":
    main()

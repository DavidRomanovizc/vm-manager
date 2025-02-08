import asyncio
import logging

from config import config_provider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def tcp_client():
    config = config_provider()
    reader, writer = await asyncio.open_connection(config.app.host, config.app.port)

    try:
        while True:
            message = input("Enter command: ").upper()
            if message.lower() == 'exit':
                break
            writer.write(message.encode())
            await writer.drain()

            data = await reader.read(100)
            print(f'Received: {data.decode()}')
    finally:
        logger.warning("Closing the connection")
        writer.close()
        await writer.wait_closed()


if __name__ == '__main__':
    try:
        with asyncio.Runner() as runner:
            runner.run(tcp_client())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Application interrupted")

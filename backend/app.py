import asyncio
import logging
from asyncio import StreamReader, StreamWriter
from functools import partial

import asyncpg

from src.vm.application.handler import CommandHandler
from src.vm.infrastructure import (
    CreateTable,
    DbApi,
    config_provider,
    VMRepository,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def handle_client(reader: StreamReader, writer: StreamWriter, cmd_handler: "CommandHandler") -> None:
    addr = writer.get_extra_info('peername')
    logger.info(f"Connected by {addr}")

    authenticated = False

    command_handlers = {
        "LOGIN": cmd_handler.handle_login,
        "LOGOUT": cmd_handler.handle_logout,
        "ADD_VM": cmd_handler.handle_add_vm,
        "LIST_VMS": cmd_handler.handle_list_vms,
        "LIST_AUTHORIZED_VMS": cmd_handler.handle_list_authorized_vms,
        "LIST_ALL_CONNECTED_VMS": cmd_handler.handle_list_all_connected_vms,
        "UPDATE_VM": cmd_handler.handle_update_vm,
        "LIST_DISKS": cmd_handler.handle_list_disks,
    }

    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        logger.info(f"Received {message} from {addr}")

        parts = message.split()
        command = parts[0]
        args = parts[1:]

        if command in command_handlers:
            if command == "LOGIN" and len(args) == 2:
                vm_id, password = args
                response = await command_handlers[command](int(vm_id), password)
                authenticated = response == "Login successful"
            elif command == "LOGOUT":
                vm_id = int(args)
                response = await command_handlers[command](vm_id)
                authenticated = False
            elif command == "ADD_VM":
                ram, cpu, password = int(args[0]), int(args[1]), str(args[2])
                response = await command_handlers[command](ram, cpu, password)
            elif authenticated:
                response = await command_handlers[command](*args)
            else:
                response = "Not authenticated"
        else:
            response = "Unknown command"

        logger.info(f"Sending response: {response} to {addr}")
        writer.write(response.encode())
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    logger.info(f"Connection closed by {addr}")


async def main():
    config = config_provider()
    logger.info("Connecting to the database...")
    conn = await asyncpg.connect(
        user=config.db.user,
        password=config.db.password,
        host=config.db.host,
        port=config.db.port,
        database=config.db.database
    )
    logger.info("Database connection established")

    db_api = DbApi(connection=conn)
    tables = CreateTable(db_api)
    await tables.create_tables()
    logger.info("Tables created successfully")

    repository = VMRepository(db_api)
    cmd_handler = CommandHandler(repository=repository)
    client_handler = partial(handle_client, cmd_handler=cmd_handler)

    srv = await asyncio.start_server(client_connected_cb=client_handler, host=config.app.host, port=config.app.port)
    logger.info(f"Serving on {config.app.host}:{config.app.port}")

    async with srv:
        await srv.serve_forever()


if __name__ == '__main__':
    try:
        with asyncio.Runner() as runner:
            runner.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Application interrupted")

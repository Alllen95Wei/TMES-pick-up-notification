# coding=utf-8
import asyncio
import json
from json import loads, dumps
from typing import Literal
import logging
import websockets
from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

import logger
import json_assistant

CONNECTED_CLIENTS: dict[int, ServerConnection] = {}
LOGGER = logger.create_logger()


def data_is_stored(data) -> tuple[bool, int | None]:
    for k, v in CONNECTED_CLIENTS.items():
        if data == v:
            return True, k
    return False, None


async def send_message(data: dict,
                       message_type: Literal[
                           "INIT", "ERROR", "CALLBACK", "BROADCAST", "STUDENT_LIST", "CALL_FOR_STUDENT"],
                       target: ServerConnection):
    data["type"] = message_type
    data_str = dumps(data)
    await target.send(data_str)


async def handler(websocket: ServerConnection):
    global CONNECTED_CLIENTS
    try:
        async for data in websocket:
            # JSON string to dict
            data = loads(data)
            client_id: int = data.get("classNo", -1)
            msg_type: str = data.get("type", "UNKNOWN")
            # process received data
            if msg_type == "INIT":
                client_is_stored, k = data_is_stored(websocket)
                if client_is_stored:
                    CONNECTED_CLIENTS.pop(k)
                CONNECTED_CLIENTS[client_id] = websocket
                if client_id == 777:
                    # return student list
                    student_list_callback: dict = {}
                    try:
                        student_list = json_assistant.StudentList.get_all_student_lists()
                        student_list_callback["students"] = student_list
                        await send_message(student_list_callback, "STUDENT_LIST", websocket)
                    except Exception as e:
                        error_message = f"{type(e).__name__}: {e}"
                        logging.error(error_message)
                        await send_message({"message": error_message}, "ERROR", websocket)
            elif msg_type == "BROADCAST":
                for key in CONNECTED_CLIENTS.keys():
                    if key == client_id:
                        continue
                    await send_message(data, "BROADCAST", CONNECTED_CLIENTS.get(key))
            elif msg_type == "CALL_FOR_STUDENT":
                target_id = data.get("targetClassNo", -1)
                target = CONNECTED_CLIENTS.get(target_id, None)
                if target is None:
                    logging.error(f"Cannot find target for {client_id}")
                    await send_message({"message": f"{target_id} not found"}, "ERROR", websocket)
                else:
                    await send_message(data, "CALL_FOR_STUDENT", target)
            await send_message({"received": True}, "CALLBACK", websocket)
    except (ConnectionClosedError, ConnectionClosedOK):
        client_is_stored, k = data_is_stored(websocket)
        if client_is_stored:
            CONNECTED_CLIENTS.pop(k)
            logging.info(f"{k} is removed.")


async def main():
    async with serve(handler, "", 8001, ping_timeout=None) as server:
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

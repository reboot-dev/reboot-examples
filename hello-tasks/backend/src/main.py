import asyncio
import logging
from hello_servicer import HelloServicer
from hello_tasks.v1.hello_rsm import (
    EraseTaskResponse,
    Hello,
    WarningTaskResponse,
)
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_STATE_MACHINE_ID = 'resemble-hello'


async def initialize(workflow: Workflow):
    hello = Hello(EXAMPLE_STATE_MACHINE_ID)

    logging.info("📬 Sending an initial message...")
    send_response = await hello.Send(workflow, message="Hello, World!")
    logging.info("💌 Message sent!")

    warning_response = await workflow.future_from_task_id(
        task_id=send_response.task_id,
        response_type=WarningTaskResponse,
    )
    logging.info("⏱ Message will be erased soon...")

    await workflow.future_from_task_id(
        task_id=warning_response.task_id,
        response_type=EraseTaskResponse,
    )
    logging.info("🗑 Message erased.")


async def main():
    await Application(
        servicers=[HelloServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

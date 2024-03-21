import asyncio
import logging
from hello_servicer import HelloServicer
from hello_tasks.v1.hello_rsm import Hello
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_STATE_MACHINE_ID = 'resemble-hello'


async def initialize(workflow: Workflow):
    hello = Hello(EXAMPLE_STATE_MACHINE_ID)

    logging.info("📬 Sending an initial message...")
    send_response = await hello.Send(workflow, message="Hello, World!")
    logging.info("💌 Message sent!")

    warning_response = await Hello.WarningTaskFuture(
        workflow,
        task_id=send_response.task_id,
    )
    logging.info("⏱ Message will be erased soon...")

    await Hello.EraseTaskFuture(
        workflow,
        task_id=warning_response.task_id,
    )
    logging.info("🗑 Message erased.")


async def main():
    await Application(
        servicers=[HelloServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

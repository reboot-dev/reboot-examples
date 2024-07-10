import asyncio
import logging
from hello_servicer import HelloServicer
from hello_tasks.v1.hello_rsm import Hello
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_STATE_MACHINE_ID = 'resemble-hello'


async def initialize(workflow: Workflow):
    hello = Hello.lookup(EXAMPLE_STATE_MACHINE_ID)

    logging.info("📬 Sending initial message if it isn't already...")

    send_response = await hello.idempotently().Send(
        workflow,
        message="Hello, World!",
    )

    logging.info("💌 Ensuring initial message was sent!")

    warning_response = await Hello.WarningTaskFuture(
        workflow,
        task_id=send_response.task_id,
    )

    logging.info("⏱ Ensuring initial message was erased...")

    await Hello.EraseTaskFuture(
        workflow,
        task_id=warning_response.task_id,
    )

    logging.info("🗑 Confirmed message erased.")


async def main():
    await Application(
        servicers=[HelloServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

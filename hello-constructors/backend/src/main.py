import asyncio
import logging
from hello_constructors.v1.hello_rsm import Hello
from hello_servicer import HelloServicer
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_STATE_MACHINE_ID = 'resemble-hello'


async def initialize(workflow: Workflow):
    # Explicitly create the state machine.
    hello, _ = await Hello.Create(
        EXAMPLE_STATE_MACHINE_ID,
        workflow,
        initial_message="Welcome! This message was sent by a constructor.",
    )

    # Send a message.
    await hello.Send(
        workflow, message="This message was sent after construction!"
    )

    messages_response = await hello.Messages(workflow)
    print(
        f"After initialization, the Hello messages are: {messages_response.messages}"
    )


async def main():
    application = Application(
        servicers=[HelloServicer],
        initialize=initialize,
    )

    logging.info('👋 Hello, World? Hello, Resemble! 👋')

    await application.run()


if __name__ == '__main__':
    asyncio.run(main())

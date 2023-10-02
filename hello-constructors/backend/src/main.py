import asyncio
import logging
from hello_constructors.v1.greeter_rsm import Greeter, GreetResponse
from greeter_servicer import GreeterServicer
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_GREETER_ID = 'my-cool-greeter'


async def initialize(workflow: Workflow):
    greeter = Greeter(EXAMPLE_GREETER_ID)

    # Create the state machine.
    await greeter.Create(workflow, greeting="Hello")

    # Demonstrate that we can use the actor.
    response: GreetResponse = await greeter.Greet(workflow, name="Constructors")
    logging.info(f"Received a greeting: '{response.message}'")


async def main():
    await Application(
        servicers=[GreeterServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

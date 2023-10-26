import asyncio
import logging
from deprecated_greeter_servicer import DeprecatedGreeterServicer
from hello_legacy_grpc.v1 import greeter_pb2, greeter_pb2_grpc
from hello_legacy_grpc.v1.greeter_rsm import GreetResponse, ResembleGreeter
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow
from resemble_greeter_servicer import ResembleGreeterServicer

logging.basicConfig(level=logging.INFO)


async def initialize(workflow: Workflow):
    # Call the ResembleGreeter service for some greetings.
    resemble_greeter = ResembleGreeter("my-greeter")
    for i in range(5):
        greet_response = await resemble_greeter.Greet(
            workflow, name="legacy gRPC"
        )
        logging.info(f"Received a greeting: '{greet_response.message}'")

    # Now call the DeprecatedGreeter service for a few greetings, to demonstrate
    # that it still works.
    async with workflow.legacy_grpc_channel() as channel:
        deprecated_greeter_stub = greeter_pb2_grpc.DeprecatedGreeterStub(
            channel
        )

        for i in range(5):
            greet_response = await deprecated_greeter_stub.Greet(
                greeter_pb2.GreetRequest(name="legacy gRPC")
            )
            logging.info(f"Received a greeting: '{greet_response.message}'")


async def main():
    await Application(
        servicers=[ResembleGreeterServicer],
        legacy_grpc_servicers=[DeprecatedGreeterServicer],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

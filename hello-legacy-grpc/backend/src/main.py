import asyncio
import logging
from deprecated_greeter_servicer import DeprecatedGreeterServicer
from hello_legacy_grpc.v1 import greeter_pb2, greeter_pb2_grpc
from proxy_greeter_servicer import ProxyGreeterServicer
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow
from resemble_greeter_servicer import ResembleGreeterServicer

logging.basicConfig(level=logging.INFO)


async def initialize(workflow: Workflow):
    # Call the ProxyGreeter service for a few greetings.
    async with workflow.legacy_grpc_channel() as channel:
        proxy_greeter_stub = greeter_pb2_grpc.ProxyGreeterStub(channel)

        for i in range(10):
            greet_response = await proxy_greeter_stub.Greet(
                greeter_pb2.GreetRequest(name="legacy gRPC")
            )
            logging.info(f"Received a greeting: '{greet_response.message}'")


async def main():
    await Application(
        servicers=[ResembleGreeterServicer],
        legacy_grpc_servicers=[
            DeprecatedGreeterServicer, ProxyGreeterServicer
        ],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

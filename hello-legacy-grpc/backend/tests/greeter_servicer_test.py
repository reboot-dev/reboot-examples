import sys
import unittest
from deprecated_greeter_servicer import DeprecatedGreeterServicer
from hello_legacy_grpc.v1 import greeter_pb2, greeter_pb2_grpc
from hello_legacy_grpc.v1.greeter_rsm import ResembleGreeter
from proxy_greeter_servicer import ProxyGreeterServicer
from resemble.aio.tests import Resemble
from resemble_greeter_servicer import ResembleGreeterServicer


class TestGreeter(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()
        await self.rsm.start()

    async def asyncTearDown(self) -> None:
        await self.rsm.stop()

    async def test_resemble_greeter(self) -> None:
        await self.rsm.up(
            servicers=[ResembleGreeterServicer],
            legacy_grpc_servicers=[DeprecatedGreeterServicer],
        )

        context = self.rsm.create_external_context(name=f"test-{self.id()}")

        # Call the Resemble greeter.
        resemble_greeter = ResembleGreeter.lookup("my-greeter")
        greet_response = await resemble_greeter.Greet(
            context, name="legacy gRPC"
        )
        self.assertIn(", legacy gRPC", greet_response.message)
        self.assertIn(
            "1 person has been greeted today", greet_response.message
        )

        # Call the Resemble greeter again to check that the count of greetings
        # issued has gone up.
        greet_response = await resemble_greeter.Greet(
            context, name="someone else"
        )
        self.assertIn(", someone else", greet_response.message)
        self.assertIn(
            "2 people have been greeted today", greet_response.message
        )

    async def test_deprecated_greeter(self) -> None:
        await self.rsm.up(legacy_grpc_servicers=[DeprecatedGreeterServicer])

        context = self.rsm.create_external_context(name=f"test-{self.id()}")

        # Call the DeprecatedGreeter service.
        async with context.legacy_grpc_channel() as channel:
            deprecated_greeter_stub = greeter_pb2_grpc.DeprecatedGreeterStub(
                channel
            )
            greet_response = await deprecated_greeter_stub.Greet(
                greeter_pb2.GreetRequest(name="legacy gRPC")
            )
            self.assertIn(", legacy gRPC", greet_response.message)

    @unittest.skipIf(
        sys.platform == "darwin", "This test requires Docker for "
        "the LocalEnvoy, which is unavailable on the MacOS GitHub Runner."
    )
    async def test_proxy_greeter(self) -> None:
        await self.rsm.up(
            servicers=[ResembleGreeterServicer],
            legacy_grpc_servicers=[
                DeprecatedGreeterServicer, ProxyGreeterServicer
            ],
            local_envoy=True,
        )

        context = self.rsm.create_external_context(name=f"test-{self.id()}")

        # Make sure the proxy eventually hits both services.
        # If not, the test will hang and eventually time out.
        resemble_hit = False
        deprecated_hit = False

        async with context.legacy_grpc_channel() as channel:
            proxy_greeter_stub = greeter_pb2_grpc.ProxyGreeterStub(channel)
            while not (resemble_hit and deprecated_hit):
                greet_response = await proxy_greeter_stub.Greet(
                    greeter_pb2.GreetRequest(name="legacy gRPC")
                )

                if "been greeted today" in greet_response.message:
                    resemble_hit = True
                else:
                    deprecated_hit = True

import random
from hello_legacy_grpc.v1 import greeter_pb2, greeter_pb2_grpc
from hello_legacy_grpc.v1.greeter_rsm import ResembleGreeter
from resemble.aio.interceptors import LegacyGrpcContext


class ProxyGreeterServicer(greeter_pb2_grpc.ProxyGreeterServicer):

    async def Greet(
        self,
        request: greeter_pb2.GreetRequest,
        context: LegacyGrpcContext,
    ) -> greeter_pb2.GreetResponse:
        # As part of a migration, one may want to slowly ramp up traffic to the
        # new Resemble service. This proxy servicer will forward traffic to
        # either the ResembleGreeter or the DeprecatedGreeter with a 50/50
        # ratio.
        workflow = context.workflow(name=self.Greet.__name__)
        if random.random() < 0.5:
            # Route to ResembleGreeter.
            resemble_greeter = ResembleGreeter.lookup("my-greeter")
            return await resemble_greeter.Greet(workflow, name=request.name)
        else:
            # Route to DeprecatedGreeter.
            async with workflow.legacy_grpc_channel() as channel:
                deprecated_greeter_stub = greeter_pb2_grpc.DeprecatedGreeterStub(
                    channel
                )

                return await deprecated_greeter_stub.Greet(request)

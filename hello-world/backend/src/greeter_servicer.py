import asyncio
from hello_world.v1.greeter_rsm import (
    CreateRequest,
    CreateResponse,
    Greeter,
    GreeterState,
    GreetRequest,
    GreetResponse,
)
from resemble.aio.contexts import ReaderContext, WriterContext


class GreeterServicer(Greeter.Interface):

    async def Create(
        self,
        context: WriterContext,
        request: CreateRequest,
    ) -> Greeter.CreateEffects:
        return Greeter.CreateEffects(
            state=GreeterState(greeting=request.greeting),
            response=CreateResponse()
        )

    async def Greet(
        self,
        context: ReaderContext,
        state: GreeterState,
        request: GreetRequest,
    ) -> GreetResponse:
        return GreetResponse(message=f"{state.greeting}, {request.name}")

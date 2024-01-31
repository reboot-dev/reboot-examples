from hello_constructors.v1.hello_rsm import (
    CreateRequest,
    CreateResponse,
    Hello,
    HelloState,
    MessagesRequest,
    MessagesResponse,
    SendRequest,
    SendResponse,
)
from resemble.aio.contexts import ReaderContext, WriterContext


class HelloServicer(Hello.Interface):

    async def Create(
        self,
        context: WriterContext,
        request: CreateRequest,
    ) -> Hello.CreateEffects:
        return Hello.CreateEffects(
            state=HelloState(messages=[request.initial_message]),
            response=CreateResponse()
        )

    async def Messages(
        self,
        context: ReaderContext,
        state: HelloState,
        request: MessagesRequest,
    ) -> MessagesResponse:
        return MessagesResponse(messages=state.messages)

    async def Send(
        self,
        context: WriterContext,
        state: HelloState,
        request: SendRequest,
    ) -> Hello.SendEffects:
        message = request.message
        state.messages.extend([message])
        return Hello.SendEffects(state=state, response=SendResponse())

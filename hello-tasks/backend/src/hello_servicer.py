import uuid
from datetime import timedelta
from hello_tasks.v1.hello_rbt import (
    EraseRequest,
    EraseResponse,
    Hello,
    Message,
    MessagesRequest,
    MessagesResponse,
    SendRequest,
    SendResponse,
    WarningRequest,
    WarningResponse,
)
from reboot.aio.auth.authorizers import allow
from reboot.aio.contexts import ReaderContext, WriterContext

SECS_UNTIL_WARNING = 7
ADDITIONAL_SECS_UNTIL_ERASE = 3


class HelloServicer(Hello.Servicer):

    def authorizer(self):
        return allow()

    async def Messages(
        self,
        context: ReaderContext,
        state: Hello.State,
        request: MessagesRequest,
    ) -> MessagesResponse:
        # Prepend a message saying how many other messages have been erased so
        # far.
        erased_messages_summary = (
            f"Number of messages erased so far: "
            f"{state.num_erased_messages}"
        )
        message_strings = [erased_messages_summary
                          ] + [message.text for message in state.messages]

        return MessagesResponse(messages=message_strings)

    async def Send(
        self,
        context: WriterContext,
        state: Hello.State,
        request: SendRequest,
    ) -> SendResponse:
        # Create an ID and store the new message.
        message = Message(id=str(uuid.uuid4()), text=request.message)
        state.messages.append(message)

        # Schedule the message to get a warning message added.
        # The warning task will then schedule a follow-up task to erase the
        # message.
        warning_task_id = await self.ref().schedule(
            when=timedelta(seconds=SECS_UNTIL_WARNING)
        ).Warning(
            context,
            message_id=message.id,
        )

        return SendResponse(task_id=warning_task_id)

    async def Warning(
        self,
        context: WriterContext,
        state: Hello.State,
        request: WarningRequest,
    ) -> WarningResponse:
        # Find the message in question and update its text with a warning.
        warn_index = -1
        for i in range(len(state.messages)):
            message = state.messages[i]
            if message.id == request.message_id:
                warn_index = i
                break

        if warn_index < 0:
            # There are two options for handling errors in a task:
            # 1. Silently complete the task and describe the error in the task
            #    response. The system will not log any error and won't retry the
            #    task.
            # 2. Raise an exception. The system will log an error and retry the
            #    task later.
            #
            # We're throwing an exception here because a message not being found
            # indicates an internal programming error. We want to log an error
            # so that a developer will come and debug.
            raise ValueError(f"ID {request.message_id} not found")

        state.messages[warn_index].text += " (Disappearing soon!)"

        # Schedule the task to be fully erased.
        erase_task_id = await self.ref().schedule(
            when=timedelta(seconds=ADDITIONAL_SECS_UNTIL_ERASE),
        ).Erase(
            context,
            message_id=request.message_id,
        )

        return WarningResponse(task_id=erase_task_id)

    async def Erase(
        self,
        context: WriterContext,
        state: Hello.State,
        request: EraseRequest,
    ) -> EraseResponse:
        # Find the message in question and remove it.
        delete_index = -1
        for i in range(len(state.messages)):
            message = state.messages[i]
            if message.id == request.message_id:
                delete_index = i
                break

        if delete_index < 0:
            # There are two options for handling errors in a task:
            # 1. Silently complete the task and describe the error in the task
            #    response. The system will not log any error and won't retry the
            #    task.
            # 2. Raise an exception. The system will log an error and retry the
            #    task later.
            #
            # We're throwing an exception here because a message not being found
            # indicates an internal programming error. We want to log an error
            # so that a developer will come and debug.
            raise ValueError(f"ID {request.message_id} not found")

        state.messages.pop(delete_index)
        state.num_erased_messages += 1

        return EraseResponse()

import asyncio
import uuid
from datetime import timedelta
from hello_tasks.v1.hello_rsm import (
    EraseTaskRequest,
    EraseTaskResponse,
    Hello,
    HelloState,
    Message,
    MessagesRequest,
    MessagesResponse,
    SendRequest,
    SendResponse,
    WarningTaskRequest,
    WarningTaskResponse,
)
from resemble.aio.contexts import ReaderContext, WriterContext
from resemble.aio.tasks import TaskEffect

SECS_UNTIL_WARNING = 7
ADDITIONAL_SECS_UNTIL_ERASE = 3


class HelloServicer(Hello.Interface):

    async def Messages(
        self,
        context: ReaderContext,
        state: HelloState,
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
        state: HelloState,
        request: SendRequest,
    ) -> Hello.SendEffects:
        # Create an ID and store the new message.
        message = Message(id=str(uuid.uuid4()), text=request.message)
        state.messages.append(message)

        # Schedule the message to get a warning message added.
        # The warning task will then schedule a follow-up task to erase the
        # message.
        warning_task: TaskEffect = self.schedule(
            timedelta(seconds=SECS_UNTIL_WARNING)
        ).WarningTask(
            context,
            message_id=message.id,
        )

        return Hello.SendEffects(
            state=state,
            tasks=[warning_task],
            response=SendResponse(task_id=warning_task.task_id),
        )

    async def WarningTask(
        self,
        context: WriterContext,
        state: HelloState,
        request: WarningTaskRequest,
    ) -> Hello.WarningTaskEffects:
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
        erase_task: TaskEffect = self.schedule(
            timedelta(seconds=ADDITIONAL_SECS_UNTIL_ERASE),
        ).EraseTask(
            context,
            message_id=request.message_id,
        )

        return Hello.WarningTaskEffects(
            state=state,
            tasks=[erase_task],
            response=WarningTaskResponse(task_id=erase_task.task_id),
        )

    async def EraseTask(
        self,
        context: WriterContext,
        state: HelloState,
        request: EraseTaskRequest,
    ) -> Hello.EraseTaskEffects:
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

        return Hello.EraseTaskEffects(
            state=state,
            response=EraseTaskResponse(),
        )

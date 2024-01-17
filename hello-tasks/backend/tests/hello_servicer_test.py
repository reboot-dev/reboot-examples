import hello_servicer
import unittest
from hello_servicer import HelloServicer
from hello_tasks.v1.hello_rsm import (
    EraseTaskResponse,
    Hello,
    WarningTaskResponse,
)
from resemble.aio.tests import Resemble
from resemble.aio.workflows import Workflow


class TestHello(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()
        await self.rsm.start()

    async def asyncTearDown(self) -> None:
        await self.rsm.stop()

    async def test_hello_tasks(self) -> None:
        # To make our test run quickly, remove delays before erasing the
        # message.
        hello_servicer.SECS_UNTIL_WARNING = 0
        hello_servicer.ADDITIONAL_SECS_UNTIL_ERASE = 0
        await self.rsm.up(
            servicers=[HelloServicer],
            # Normally, `rsm.up()` runs the servicers in a separate process, to
            # ensure that accidental use of blocking functions (an easy mistake
            # to make) doesn't cause the test to lock up. However, in this test
            # we're updating constants used in a servicer, and the servicer must
            # run in the same process as the test or that won't work.
            #
            # We MUST therefore pass `in_process=True`.
            in_process=True,
        )

        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")

        hello = Hello("testing-hello")

        # Send a message.
        send_response = await hello.Send(workflow, message="Hello, World!")

        # Wait for the message to be erased.
        warning_response = await workflow.future_from_task_id(
            task_id=send_response.task_id,
            response_type=WarningTaskResponse,
        )
        await workflow.future_from_task_id(
            task_id=warning_response.task_id,
            response_type=EraseTaskResponse,
        )

        # Check that the current list of messages reflects the erasure.
        messages_response = await hello.Messages(workflow)
        self.assertEqual(len(messages_response.messages), 1)
        self.assertEqual(
            messages_response.messages[0],
            "Number of messages erased so far: 1",
        )

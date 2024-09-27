import hello_servicer
import unittest
from hello_servicer import HelloServicer
from hello_tasks.v1.hello_rbt import Hello
from reboot.aio.tests import Reboot


class TestHello(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rbt = Reboot()
        await self.rbt.start()

    async def asyncTearDown(self) -> None:
        await self.rbt.stop()

    async def test_hello_tasks(self) -> None:
        # To make our test run quickly, remove delays before erasing the
        # message.
        hello_servicer.SECS_UNTIL_WARNING = 0
        hello_servicer.ADDITIONAL_SECS_UNTIL_ERASE = 0
        await self.rbt.up(
            servicers=[HelloServicer],
            # Normally, `rbt.up()` runs the servicers in a separate process, to
            # ensure that accidental use of blocking functions (an easy mistake
            # to make) doesn't cause the test to lock up. However, in this test
            # we're updating constants used in a servicer, and the servicer must
            # run in the same process as the test or that won't work.
            #
            # We MUST therefore pass `in_process=True`.
            in_process=True,
        )

        context = self.rbt.create_external_context(name=f"test-{self.id()}")

        hello = Hello.lookup("testing-hello")

        # Send a message.
        send_response = await hello.Send(context, message="Hello, World!")

        # Wait for the message to be erased.
        warning_response = await Hello.WarningTaskFuture(
            context,
            task_id=send_response.task_id,
        )
        await Hello.EraseTaskFuture(
            context,
            task_id=warning_response.task_id,
        )

        # Check that the current list of messages reflects the erasure.
        messages_response = await hello.Messages(context)
        self.assertEqual(len(messages_response.messages), 1)
        self.assertEqual(
            messages_response.messages[0],
            "Number of messages erased so far: 1",
        )

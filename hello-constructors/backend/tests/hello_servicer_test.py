import unittest
from hello_constructors.v1.hello_rsm import Hello
from hello_servicer import HelloServicer
from resemble.aio.tests import Resemble
from resemble.aio.workflows import Workflow


class TestHello(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()
        await self.rsm.start()

    async def asyncTearDown(self) -> None:
        await self.rsm.stop()

    async def test_hello_constructors(self) -> None:
        await self.rsm.up(servicers=[HelloServicer])

        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")

        # Create the state machine by calling its constructor. The fact that the
        # state machine _has_ a constructor means that this step is required
        # before other methods can be called on it.
        hello, _ = await Hello.Create(
            "testing-hello",
            workflow,
            initial_message="first message",
        )

        # Send another message.
        await hello.Send(workflow, message="second message")

        messages_response = await hello.Messages(workflow)
        self.assertEqual(
            messages_response.messages, [
                "first message",
                "second message",
            ]
        )

import unittest
from hello_constructors.v1.greeter_rsm import Greeter, GreetResponse
from greeter_servicer import GreeterServicer
from resemble.aio.tests import Resemble
from resemble.aio.workflows import Workflow


class TestGreeter(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()

    async def asyncTearDown(self) -> None:
        await self.rsm.down()

    async def test_hello_constructors(self) -> None:
        await self.rsm.up(servicers=[GreeterServicer])

        workflow: Workflow = self.rsm.create_workflow(name=self.id())

        greeter = Greeter("testing-greeter")

        # Create the state machine by calling its constructor. The fact that the
        # state machine _has_ a constructor means that this step is required
        # before other methods can be called on it.
        await greeter.Create(workflow, greeting="Hello")

        response: GreetResponse = await greeter.Greet(workflow, name="Constructors")
        self.assertEqual(response.message, "Hello, Constructors")

import unittest
from account_servicer import AccountServicer
from bank.v1.account_rsm import Account, BalanceResponse
from bank.v1.bank_rsm import Bank, SignUpResponse
from bank.v1.errors_pb2 import OverdraftError
from bank_servicer import BankServicer
from resemble.aio.tests import Resemble
from resemble.aio.workflows import Workflow


class TestAccount(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.rsm = Resemble()
        await self.rsm.start()

    async def asyncTearDown(self) -> None:
        await self.rsm.stop()

    async def test_signup(self) -> None:
        await self.rsm.up(servicers=[BankServicer, AccountServicer])
        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")
        bank = Bank("my-bank")

        # The Bank state machine doesn't have a constructor, so we can simply
        # start calling methods on it.
        response: SignUpResponse = await bank.SignUp(
            workflow,
            customer_name="Alice",
        )
        # The account ID generated by `SignUp` should be a 7-digit number.
        self.assertEqual(len(response.account_id), 7)

        # SignUp will have created an Account we can call.
        account = Account(response.account_id)
        response = await account.Balance(workflow)
        self.assertEqual(response.balance, 0)

    async def test_transfer(self):
        await self.rsm.up(servicers=[BankServicer, AccountServicer])
        workflow: Workflow = self.rsm.create_workflow(name=f"test-{self.id()}")
        bank = Bank("my-bank")

        alice: SignUpResponse = await bank.SignUp(
            workflow,
            customer_name="Alice",
        )
        alice_account = Account(alice.account_id)
        bob: SignUpResponse = await bank.SignUp(
            workflow,
            customer_name="Bob",
        )
        bob_account = Account(bob.account_id)

        # Alice deposits some money.
        await alice_account.Deposit(workflow, amount=100)
        response: BalanceResponse = await alice_account.Balance(workflow)
        self.assertEqual(response.balance, 100)

        # Alice transfers some money to Bob.
        await bank.Transfer(
            workflow,
            from_account_id=alice.account_id,
            to_account_id=bob.account_id,
            amount=40,
        )
        response = await alice_account.Balance(workflow)
        self.assertEqual(response.balance, 60)
        response = await bob_account.Balance(workflow)
        self.assertEqual(response.balance, 40)

        # Bob tries to transfer too much money back to Alice.
        with self.assertRaises(Bank.TransferAborted) as aborted:
            await bank.Transfer(
                workflow,
                from_account_id=bob.account_id,
                to_account_id=alice.account_id,
                amount=50,
            )
        self.assertTrue(isinstance(aborted.exception.error, OverdraftError))
        self.assertEqual(aborted.exception.error.amount, 10)

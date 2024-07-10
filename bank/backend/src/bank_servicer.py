import logging
import random
from bank.v1.account_rsm import Account
from bank.v1.bank_rsm import (
    Bank,
    SignUpRequest,
    SignUpResponse,
    TransferRequest,
)
from google.protobuf.empty_pb2 import Empty
from resemble.aio.contexts import TransactionContext

logging.basicConfig(level=logging.INFO)


class BankServicer(Bank.Interface):

    async def pick_new_account_id(self, state: Bank.State) -> str:
        """Picks an account ID for a new account."""
        # Transactions normally observe state through Reader calls. However for
        # convenience, it is possible to do an inline read of the state of this
        # state machine, which is like calling a Reader that simply returns the
        # whole state of the state machine.
        while True:
            new_account_id = str(random.randint(1000000, 9999999))
            if new_account_id not in state.account_ids:
                return new_account_id

    async def SignUp(
        self,
        context: TransactionContext,
        state: Bank.State,
        request: SignUpRequest,
    ) -> SignUpResponse:

        new_account_id = await self.pick_new_account_id(state)

        # Transactions like writers can alter state directly.
        state.account_ids.append(new_account_id)

        # Let's go create the account.
        account, _ = await Account.Open(
            new_account_id,
            context,
            customer_name=request.customer_name,
        )

        return SignUpResponse(account_id=new_account_id)

    async def Transfer(
        self,
        context: TransactionContext,
        state: Bank.State,
        request: TransferRequest,
    ) -> Empty:
        from_account = Account.lookup(request.from_account_id)
        to_account = Account.lookup(request.to_account_id)
        await from_account.Withdraw(context, amount=request.amount)
        await to_account.Deposit(context, amount=request.amount)
        return Empty()

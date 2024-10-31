import logging
import uuid
from bank.v1.account_rbt import Account
from bank.v1.bank_rbt import (
    Bank,
    SignUpRequest,
    SignUpResponse,
    TransferRequest,
    TransferResponse,
)
from reboot.aio.contexts import TransactionContext

logging.basicConfig(level=logging.INFO)


class BankServicer(Bank.Servicer):

    async def SignUp(
        self,
        context: TransactionContext,
        state: Bank.State,
        request: SignUpRequest,
    ) -> SignUpResponse:
        # Generating an account ID so that we can demonstrate setting
        # the account ID explicitly. Alternatively you can just call
        # `construct()` without any args and Reboot will generate a
        # unique ID for you.
        new_account_id = str(uuid.uuid4())

        # Let's go create the account.
        account, _ = await Account.construct(id=new_account_id).Open(
            context,
            customer_name=request.customer_name,
        )

        # Transactions like writers can alter state directly.
        state.account_ids.append(account.state_id)

        return SignUpResponse(account_id=account.state_id)

    async def Transfer(
        self,
        context: TransactionContext,
        state: Bank.State,
        request: TransferRequest,
    ) -> TransferResponse:
        from_account = Account.lookup(request.from_account_id)
        to_account = Account.lookup(request.to_account_id)

        await from_account.Withdraw(context, amount=request.amount)
        await to_account.Deposit(context, amount=request.amount)

        return TransferResponse()

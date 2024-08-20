import logging
from bank.v1.account_rsm import Account
from bank.v1.bank_rsm import (
    Bank,
    SignUpRequest,
    SignUpResponse,
    TransferRequest,
    TransferResponse,
)
from resemble.aio.contexts import TransactionContext

logging.basicConfig(level=logging.INFO)


class BankServicer(Bank.Interface):

    async def SignUp(
        self,
        context: TransactionContext,
        state: Bank.State,
        request: SignUpRequest,
    ) -> SignUpResponse:

        # Let's go create the account, which will have a generated unique id.
        account, _ = await Account.construct().Open(
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

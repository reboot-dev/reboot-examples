import logging
from bank.v1.account_rsm import (
    Account,
    AccountState,
    BalanceResponse,
    DepositRequest,
    DepositResponse,
    OpenRequest,
    OpenResponse,
    WithdrawRequest,
    WithdrawResponse,
)
from bank.v1.errors_pb2 import OverdraftError
from google.protobuf.empty_pb2 import Empty
from resemble.aio.contexts import ReaderContext, WriterContext

logging.basicConfig(level=logging.INFO)


class AccountServicer(Account.Interface):

    async def Open(
        self,
        context: WriterContext,
        request: OpenRequest,
    ) -> Account.OpenEffects:
        # Since this is a constructor, we are setting the initial state of the
        # state machine.
        initial_state = AccountState(customer_name=request.customer_name)

        # We'd like to send the new customer a welcome email, but that can be
        # done asynchronously, so we schedule it as a task.
        welcome_email_task = self.schedule().WelcomeEmailTask(context)

        return Account.OpenEffects(
            state=initial_state,
            tasks=[welcome_email_task],
            response=OpenResponse(
                welcome_email_task_id=welcome_email_task.task_id
            ),
        )

    async def Balance(
        self,
        context: ReaderContext,
        state: AccountState,
        request: Empty,
    ) -> BalanceResponse:
        return BalanceResponse(balance=state.balance)

    async def Deposit(
        self,
        context: WriterContext,
        state: AccountState,
        request: DepositRequest,
    ) -> Account.DepositEffects:
        updated_balance = state.balance + request.amount
        return Account.DepositEffects(
            state=AccountState(balance=updated_balance),
            response=DepositResponse(updated_balance=updated_balance),
        )

    async def Withdraw(
        self,
        context: WriterContext,
        state: AccountState,
        request: WithdrawRequest,
    ) -> Account.WithdrawEffects:
        updated_balance = state.balance - request.amount
        if updated_balance < 0:
            raise Account.WithdrawError(
                OverdraftError(amount=-updated_balance)
            )
        return Account.WithdrawEffects(
            state=AccountState(balance=updated_balance),
            response=WithdrawResponse(updated_balance=updated_balance),
        )

    async def WelcomeEmailTask(
        self,
        context: WriterContext,
        state: AccountState,
        request: Empty,
    ) -> Account.WelcomeEmailTaskEffects:
        message_body = (
            f"Hello {state.customer_name},\n"
            "\n"
            "We are delighted to welcome you as a customer.\n"
            f"Your new account has been opened, and has ID '{context.actor_id}'.\n"
            "\n"
            "Best regards,\n"
            "Your Bank"
        )

        await send_email(message_body)

        return Account.WelcomeEmailTaskEffects(
            state=state,
            response=Empty(),
        )


async def send_email(message_body: str):
    # We're not actually going to send an email here; but you could!
    #
    # If you do send real emails, please be sure to use an idempotent API, since
    # (like in any well-written distributed system) this call may be retried in
    # case of errors.
    logging.info(f"Sending email:\n====\n{message_body}\n====")

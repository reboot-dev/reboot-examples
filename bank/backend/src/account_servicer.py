import logging
from bank.v1.account_rbt import (
    Account,
    BalanceRequest,
    BalanceResponse,
    DepositRequest,
    DepositResponse,
    OpenRequest,
    OpenResponse,
    WelcomeEmailTaskRequest,
    WelcomeEmailTaskResponse,
    WithdrawRequest,
    WithdrawResponse,
)
from bank.v1.errors_pb2 import OverdraftError
from reboot.aio.contexts import ReaderContext, WriterContext

logging.basicConfig(level=logging.INFO)


class AccountServicer(Account.Interface):

    async def Open(
        self,
        context: WriterContext,
        state: Account.State,
        request: OpenRequest,
    ) -> OpenResponse:
        # Since this is a constructor, we are setting the initial state of the
        # state machine.
        state.customer_name = request.customer_name

        # We'd like to send the new customer a welcome email, but that can be
        # done asynchronously, so we schedule it as a task.
        task = await self.lookup().schedule().WelcomeEmailTask(context)

        return OpenResponse(welcome_email_task_id=task.task_id)

    async def Balance(
        self,
        context: ReaderContext,
        state: Account.State,
        request: BalanceRequest,
    ) -> BalanceResponse:
        return BalanceResponse(balance=state.balance)

    async def Deposit(
        self,
        context: WriterContext,
        state: Account.State,
        request: DepositRequest,
    ) -> DepositResponse:
        state.balance += request.amount
        return DepositResponse(updated_balance=state.balance)

    async def Withdraw(
        self,
        context: WriterContext,
        state: Account.State,
        request: WithdrawRequest,
    ) -> WithdrawResponse:
        updated_balance = state.balance - request.amount
        if updated_balance < 0:
            raise Account.WithdrawAborted(
                OverdraftError(amount=-updated_balance)
            )
        state.balance = updated_balance
        return WithdrawResponse(updated_balance=updated_balance)

    async def WelcomeEmailTask(
        self,
        context: WriterContext,
        state: Account.State,
        request: WelcomeEmailTaskRequest,
    ) -> WelcomeEmailTaskResponse:
        message_body = (
            f"Hello {state.customer_name},\n"
            "\n"
            "We are delighted to welcome you as a customer.\n"
            f"Your new account has been opened, and has ID '{context.state_id}'.\n"
            "\n"
            "Best regards,\n"
            "Your Bank"
        )

        await send_email(message_body)

        return WelcomeEmailTaskResponse()


async def send_email(message_body: str):
    # We're not actually going to send an email here; but you could!
    #
    # If you do send real emails, please be sure to use an idempotent API, since
    # (like in any well-written distributed system) this call may be retried in
    # case of errors.
    logging.info(f"Sending email:\n====\n{message_body}\n====")

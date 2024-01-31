# Before importing classes from generated Resemble code, we must update the
# Python path to include the directory into which the code is generated.
import sys

sys.path.append("../api/")

# ruff: noqa: E402
import argparse
import asyncio
import uuid
from bank.v1.account_rsm import Account
from bank.v1.bank_rsm import Bank
from bank.v1.errors_pb2 import OverdraftError
from resemble.aio.workflows import Workflow


def configure_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gateway_address",
        type=str,
        default="localhost.direct:9991",
    )
    parser.add_argument(
        "--bank_id",
        type=str,
        default="resemble-bank",
    )
    subparsers = parser.add_subparsers(dest='subcommand', required=True)

    # Signup arguments.
    signup_parser = subparsers.add_parser("signup")
    signup_parser.add_argument(
        "customer_name",
        type=str,
        help="name of the new customer",
    )

    # Deposit arguments.
    deposit_parser = subparsers.add_parser("deposit")
    deposit_parser.add_argument(
        "account_id",
        type=str,
        help="account to deposit into",
    )
    deposit_parser.add_argument(
        "amount",
        type=int,
        help="amount of money to deposit",
    )

    # Withdraw arguments.
    withdraw_parser = subparsers.add_parser("withdraw")
    withdraw_parser.add_argument(
        "account_id",
        type=str,
        help="account to withdraw from",
    )
    withdraw_parser.add_argument(
        "amount",
        type=int,
        help="amount of money to withdraw",
    )

    # Transfer arguments.
    transfer_parser = subparsers.add_parser("transfer")
    transfer_parser.add_argument(
        "from_account_id",
        type=str,
        help="account to transfer from",
    )
    transfer_parser.add_argument(
        "to_account_id",
        type=str,
        help="account to which money should be sent",
    )
    transfer_parser.add_argument(
        "amount",
        type=int,
        help="amount of money to transfer",
    )

    # Balance arguments.
    balance_parser = subparsers.add_parser("balance")
    balance_parser.add_argument(
        "account_id",
        type=str,
        help="account to fetch the balance of",
    )

    return parser


async def run_action(args: argparse.Namespace) -> int:
    workflow = Workflow(
        name=f"bank-cli-action-{str(uuid.uuid4())}",
        gateway=args.gateway_address,
    )

    bank = Bank(args.bank_id)
    if args.subcommand == "signup":
        response = await bank.SignUp(
            workflow, customer_name=args.customer_name
        )
        print(
            f"Signup successful! Your new account id is {response.account_id}"
        )
    elif args.subcommand == "transfer":
        try:
            response = await bank.Transfer(
                workflow,
                from_account_id=args.from_account_id,
                to_account_id=args.to_account_id,
                amount=args.amount
            )
            print("Transfer successful!")
        except Bank.TransferError as error:
            if isinstance(error.detail, OverdraftError):
                print(
                    "Transfer unsuccessful due to insufficient funds. "
                    "Your account balance is less than the requested "
                    f"amount by: {error.detail.amount}"
                )
            else:
                print(
                    f"Unexpected error during transfer: '{type(error.detail)}'"
                )
    else:
        # These commands talk directly to the Account state machine.
        account = Account(args.account_id)
        if args.subcommand == "deposit":
            response = await account.Deposit(workflow, amount=args.amount)
            print(
                f"Deposit successful! Your account balance is now: {response.updated_balance}"
            )
        elif args.subcommand == "withdraw":
            try:
                response = await account.Withdraw(workflow, amount=args.amount)
                print(
                    f"Withdrawal successful! Your account balance is now: {response.updated_balance}"
                )
            except Account.WithdrawError as error:
                if isinstance(error.detail, OverdraftError):
                    print(
                        "Withdrawal unsuccessful due to insufficient funds. "
                        "Your account balance is less than the requested "
                        f"amount by: {error.detail.amount}"
                    )
                else:
                    print(
                        f"Unexpected error during transfer: '{type(error.detail)}'"
                    )
        elif args.subcommand == "balance":
            response = await account.Balance(workflow)
            print(f"Your account balance is: {response.balance}")


if __name__ == '__main__':
    parser = configure_parser()
    args = parser.parse_args()
    asyncio.run(run_action(args))

import asyncio
import logging
from account_servicer import AccountServicer
from bank.v1.bank_rsm import Bank
from bank_servicer import BankServicer
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow

logging.basicConfig(level=logging.INFO)

EXAMPLE_STATE_MACHINE_ID = 'resemble-bank'


async def initialize(workflow: Workflow):
    bank = Bank(EXAMPLE_STATE_MACHINE_ID)
    response = await bank.SignUp(workflow, customer_name="Initial User")


async def main():
    application = Application(
        servicers=[AccountServicer, BankServicer],
        initialize=initialize,
    )

    logging.info('The Resemble Bank is open for business! 🏦')

    await application.run()


if __name__ == '__main__':
    asyncio.run(main())

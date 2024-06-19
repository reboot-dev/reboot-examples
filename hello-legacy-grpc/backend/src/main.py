import asyncio
from deprecated_greeter_servicer import DeprecatedGreeterServicer
from hello_legacy_grpc.v1.greeter_rsm import ResembleGreeter
from proxy_greeter_servicer import ProxyGreeterServicer
from resemble.aio.applications import Application
from resemble.aio.workflows import Workflow
from resemble_greeter_servicer import ResembleGreeterServicer


async def initialize(workflow: Workflow):
    # Schedule initialize on `ResembleGreeter` so that it only happens
    # once via idempotency (but see caveats in
    # `ResembleGreeterServicer.Initialize`).
    #
    # NOTE: we use `schedule()` because `Initialize()` is a `workflow`
    # method and those are not (yet) synchronously callable from a
    # `Workflow`. Because `initialize()` (this function) gets called
    # asynchronously with respect to other calls being made that fact
    # that we schedule here is semantically no different.
    await (
        ResembleGreeter.lookup("my-greeter").idempotently("initialize").
        schedule().Initialize(workflow)
    )


async def main():
    await Application(
        servicers=[ResembleGreeterServicer],
        legacy_grpc_servicers=[
            DeprecatedGreeterServicer, ProxyGreeterServicer
        ],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

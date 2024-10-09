import asyncio
import reboot.aio.memoize
from deprecated_greeter_servicer import DeprecatedGreeterServicer
from hello_legacy_grpc.v1.greeter_rbt import RebootGreeter
from proxy_greeter_servicer import ProxyGreeterServicer
from reboot.aio.applications import Application
from reboot.aio.external import ExternalContext
from reboot_greeter_servicer import RebootGreeterServicer


async def initialize(context: ExternalContext):
    # Schedule initialize on `RebootGreeter` so that it only happens
    # once via idempotency (but see caveats in
    # `RebootGreeterServicer.Initialize`).
    #
    # NOTE: we use `schedule()` because `Initialize()` is a `workflow`
    # method and those are not (yet) synchronously callable from a
    # `ExternalContext`. Because `initialize()` (this function) gets called
    # asynchronously with respect to other calls being made that fact
    # that we schedule here is semantically no different.
    await RebootGreeter.lookup(
        "my-greeter",
    ).idempotently().schedule().Initialize(context)


async def main():
    await Application(
        servicers=[RebootGreeterServicer] + reboot.aio.memoize.servicers(),
        legacy_grpc_servicers=[
            DeprecatedGreeterServicer, ProxyGreeterServicer
        ],
        initialize=initialize,
    ).run()


if __name__ == '__main__':
    asyncio.run(main())

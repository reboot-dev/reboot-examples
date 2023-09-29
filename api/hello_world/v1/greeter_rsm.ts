import type {
  PartialMessage
} from "@bufbuild/protobuf";
import {
  Deferred,
  Event,
  IQueryRequest,
  IQueryResponse,
  Mutation,
  QueryRequest,
  QueryResponse,
  ResponseOrError,
  filterSet,
  parseStreamedValue,
  popMutationMaybeFromLocalStorage,
  pushMutationMaybeToLocalStorage,
  retryForever,
  useResembleContext
} from "@reboot-dev/resemble-react";
import {
  Dispatch,
  MutableRefObject,
  SetStateAction,
  useEffect,
  useRef,
  useState,
} from "react";
import { v4 as uuidv4 } from "uuid";
// There are known bugs with the following input / output message imports:
// 1. It doesn't correctly handle input / output messages that don't have a
// corresponding const definition in the generated _pb,
// e.g. google.protobuf.Empty.
// 2. It will try to import the same message twice if any input message is the
// same as any output message.
// TODO: correctly handle messages like google.protobuf.Empty.
// TODO: create a set of input messages AND output messages and |map ..|unique
// over those to ensure there are no duplicates.
import {
GreetingsRequest, 
GreetRequest, 
GreetResponse, 
GreetingsResponse,
} from "./greeter_pb";


// Start of service specific code.
///////////////////////////////////////////////////////////////////////////

export interface GreeterApi {
  Greetings: (partialRequest?: PartialMessage<GreetingsRequest>) =>
  Promise<GreetingsResponse>;
  Greet: (partialRequest?: PartialMessage<GreetRequest>) =>
  Promise<GreetResponse>;
  useGreetings: (partialRequest?: PartialMessage<GreetingsRequest>) => {
   response: GreetingsResponse | undefined;
    isLoading: boolean;
    error: unknown;
    mutations: {
       Greet: (request: PartialMessage<GreetRequest>,
       optimistic_metadata?: any ) =>
      Promise<ResponseOrError<GreetResponse>>;
    };
      pendingGreetMutations: {
        request: GreetRequest;
        idempotencyKey: string;
        isLoading: boolean;
        error?: unknown;
        optimistic_metadata?: any;
      }[];
      failedGreetMutations: {
        request: GreetRequest;
        idempotencyKey: string;
        isLoading: boolean;
        error?: unknown;
      }[];
      recoveredGreetMutations: {
        request: GreetRequest;
        idempotencyKey: string;
        run: () => void;
      }[];
  };
}


export interface SettingsParams {
  actorId: string;
  storeMutationsLocallyInNamespace?: string;
}
export const Greeter = ({ actorId, storeMutationsLocallyInNamespace}: SettingsParams): GreeterApi => {
  const headers = new Headers();
  headers.set("Content-Type", "application/json");
  headers.append("x-resemble-service-name", "hello_world.v1.Greeter");
  headers.append("x-resemble-actor-id", actorId);
  headers.append("Connection", "keep-alive");

  const resembleContext = useResembleContext();

  const newRequest = (
    requestBody: any,
    path: string,
    method: "GET" | "POST",
    idempotencyKey?: string,
  ) => {
    if (idempotencyKey !== undefined) {
      headers.set("x-resemble-idempotency-key", idempotencyKey);
    }
    return new Request(`${resembleContext.client?.endpoint}${path}`, {
      method: method,
      headers: headers,
      body:
        Object.keys(requestBody).length !== 0
          ? JSON.stringify(requestBody)
          : null,
    });
  };

  const Greetings = async (partialRequest: PartialMessage<GreetingsRequest> = {}) => {
    const request = partialRequest instanceof GreetingsRequest ? partialRequest : new GreetingsRequest(partialRequest);
    const requestBody = request.toJson();
    // Invariant here is that we use the '/package.service.method'
    // path and HTTP 'POST' method.
    //
    // See also 'resemble/helpers.py'.
    const req = newRequest(requestBody, "/hello_world.v1.Greeter.Greetings", "POST");

    const response = await fetch(req);
    return await response.json();
  };

  const useGreetings = (partialRequest: PartialMessage<GreetingsRequest> = {}) => {
    const [response, setResponse] = useState<GreetingsResponse>();
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<unknown>();

    // NOTE: using "refs" here because we want to "remember" some
    // state, but don't want setting that state to trigger new renders (see
    // https://react.dev/learn/referencing-values-with-refs).
    // Using a ref here so that we don't render every time we set it.

    const observedIdempotencyKeys = useRef(new Set<string>());
    // NOTE: rather than starting with undefined for 'flushMutations'
    // we start with an event so any mutations that may get created
    // before we've started reading will get queued.
    const flushMutations = useRef<Event | undefined>(new Event());

    const abortController = useRef<AbortController>();
    // Helper function to get 'abortController' since it is immutable
    // and this way we don't need to do 'new AbortController()' on
    // every render.
    function getAbortController() {
      if (abortController.current === undefined) {
        abortController.current = new AbortController();
      }

      return abortController.current;
    }

    useEffect(() => {
      const abortController = getAbortController();
      return () => {
        abortController.abort();
      };
    }, []);

    const request = partialRequest instanceof GreetingsRequest
        ? partialRequest
        : new GreetingsRequest(partialRequest)

    // NOTE: using a ref for the 'request' and 'settings' (below) so
    // that it doesn't get changed after the first time calling 'usePing'.
    const requestRef = useRef(request);

    // We are using serialized string comparison here since we can't do value
    // equality of anonymous objects. We must use the proto library's toBinary()
    // since JavaScript's standard JSON library can't serialize every possible
    // field type (notably BigInt).
    const first_request_serialized = requestRef.current.toBinary().toString();
    const current_request_serialized = request.toBinary().toString();
    if (current_request_serialized !== first_request_serialized) {
      throw new Error("Changing the request is not supported!");
    }

    const settingsRef = useRef({actorId, storeMutationsLocallyInNamespace});
    // We are using string comparison here since we can't do value
    // equality of anonymous objects.
    if (JSON.stringify(settingsRef.current) !== JSON.stringify({actorId, storeMutationsLocallyInNamespace})) {
      throw new Error("Changing settings is not supported!");
    }

    const localStorageKeyRef = useRef(storeMutationsLocallyInNamespace);

    const queuedMutations = useRef<Array<() => void>>([]);

    function hasRunningMutations(): boolean {
      if (
      runningGreetMutations.current.length > 0) {
        return true;
      }
      return false;
    }


    const runningGreetMutations = useRef<Mutation<GreetRequest>[]>([]);
    const recoveredGreetMutations = useRef<
      [Mutation<GreetRequest>, () => void][]
    >([]);
    const shouldClearFailedGreetMutations = useRef(false);
    const [failedGreetMutations, setFailedGreetMutations] = useState<
      Mutation<GreetRequest>[]
    >([]);
    const queuedGreetMutations = useRef<[Mutation<GreetRequest>, () => void][]>(
      []
    );
    const recoverAndPurgeGreetMutations = (): [
      Mutation<GreetRequest>,
      () => void
    ][] => {
      if (localStorageKeyRef.current === undefined) {
        return [];
      }
      const suffix = Greet
      const value = localStorage.getItem(localStorageKeyRef.current + suffix);
      if (value === null) {
        return [];
      }

      localStorage.removeItem(localStorageKeyRef.current);
      const mutations: Mutation<GreetRequest>[] = JSON.parse(value);
      const recoveredGreetMutations: [
        Mutation<GreetRequest>,
        () => void
      ][] = [];
      for (const mutation of mutations) {
        recoveredGreetMutations.push([mutation, () => __Greet(mutation)]);
      }
      return recoveredGreetMutations;
    }
    const doOnceGreet = useRef(true)
    if (doOnceGreet.current) {
      doOnceGreet.current = false
      recoveredGreetMutations.current = recoverAndPurgeGreetMutations()
    }

    // User facing state that only includes the pending mutations that
    // have not been observed.
    const [unobservedPendingGreetMutations, setUnobservedPendingGreetMutations] =
      useState<Mutation<GreetRequest>[]>([]);

    useEffect(() => {
      shouldClearFailedGreetMutations.current = true;
    }, [failedGreetMutations]);

    async function __Greet(
      mutation: Mutation<GreetRequest>
    ): Promise<ResponseOrError<GreetResponse>> {
      try {
        // Invariant that we won't yield to event loop before pushing to
        // runningGreetMutations
        runningGreetMutations.current.push(mutation)
        return _Mutation<GreetRequest, GreetResponse>(
          // Invariant here is that we use the '/package.service.method'.
          //
          // See also 'resemble/helpers.py'.
          "/hello_world.v1.Greeter.Greet",
          mutation,
          mutation.request,
          mutation.idempotencyKey,
          setUnobservedPendingGreetMutations,
          getAbortController(),
          shouldClearFailedGreetMutations,
          setFailedGreetMutations,
          runningGreetMutations,
          flushMutations,
          queuedMutations,
          GreetRequest,
          GreetResponse.fromJson
        );
      } finally {
        runningGreetMutations.current = runningGreetMutations.current.filter(
          ({ idempotencyKey }) => mutation.idempotencyKey !== idempotencyKey
        );

        popMutationMaybeFromLocalStorage(
          localStorageKeyRef.current,
          "Greet",
          (mutationRequest: Mutation<Request>) =>
            mutationRequest.idempotencyKey !== mutation.idempotencyKey
        );


      }
    }
    async function _Greet(mutation: Mutation<GreetRequest>) {
      setUnobservedPendingGreetMutations(
        (mutations) => [...mutations, mutation]
      )

      // NOTE: we only run one mutation at a time so that we provide a
      // serializable experience for the end user but we will
      // eventually support mutations in parallel when we have strong
      // eventually consistent writers.
      if (
        hasRunningMutations() ||
        queuedMutations.current.length > 0 ||
        flushMutations.current !== undefined
      ) {
        const deferred = new Deferred<ResponseOrError<GreetResponse>>(() =>
          __Greet(mutation)
        );

        // Add to localStorage here.
        queuedGreetMutations.current.push([mutation, () => deferred.start()]);
        queuedMutations.current.push(() => {
          for (const [, run] of queuedGreetMutations.current) {
            queuedGreetMutations.current.shift();
            run();
            break;
          }
        });
        // Maybe add to localStorage.
        pushMutationMaybeToLocalStorage(localStorageKeyRef.current, "Greet", mutation);

        return deferred.promise;
      } else {
        // NOTE: we'll add this mutation to `runningGreetMutations` in `__Greet`
        // without yielding to event loop so that we are guaranteed atomicity with checking `hasRunningMutations()`.
        return await __Greet(mutation);
      }
    }

    async function Greet(
      partialRequest: PartialMessage<GreetRequest>, optimistic_metadata?: any
    ): Promise<ResponseOrError<GreetResponse>> {
      const idempotencyKey = uuidv4();
      const request = partialRequest instanceof GreetRequest ? partialRequest : new GreetRequest(partialRequest);

      const mutation = {
        request,
        idempotencyKey,
        optimistic_metadata,
        isLoading: false, // Won't start loading if we're flushing mutations.
      };

      return _Greet(mutation);
    }

    useEffect(() => {
      const loop = async () => {
        await retryForever(async () => {
          try {
            // Wait for any mutations to complete before starting to
            // read so that we read the latest state including those
            // mutations.
            if (runningGreetMutations.current.length > 0) {
              // TODO(benh): check invariant
              // 'flushMutations.current !== undefined' but don't
              // throw an error since that will just retry, instead
              // add support for "bailing" from a 'retry' by calling a
              // function passed into the lambda that 'retry' takes.
              await flushMutations.current?.wait();
            }

            const responses = ReactQuery(
              QueryRequest.create({
                method: "Greetings",
                request: requestRef.current.toBinary(),
              }),
              getAbortController().signal
            );

            for await (const response of responses) {
              setIsLoading(false);

              for (const idempotencyKey of response.idempotencyKeys) {
                observedIdempotencyKeys.current.add(idempotencyKey);
              }

              // Only keep around the idempotency keys that are
              // still pending as the rest are not useful for us.
              observedIdempotencyKeys.current = filterSet(
                observedIdempotencyKeys.current,
                (observedIdempotencyKey) =>
                  [
                  ...runningGreetMutations.current,
                  ].some(
                    (mutation) =>
                      observedIdempotencyKey === mutation.idempotencyKey
                  )
              );

              if (flushMutations.current !== undefined) {
                // TODO(benh): check invariant
                // 'pendingMutations.current.length === 0' but don't
                // throw an error since that will just retry, instead
                // add support for "bailing" from a 'retry' by calling a
                // function passed into the lambda that 'retry' takes.

                flushMutations.current = undefined;

                // Dequeue 1 queue and run 1 mutation from it.
                for (const run of queuedMutations.current) {
                  queuedMutations.current.shift();
                  run();
                  break;
                }
              }

              setUnobservedPendingGreetMutations(
              (mutations) =>
                mutations
                  .filter(
                    (mutation) =>
                      // Only keep mutations that are queued, pending or
                      // recovered.
                      queuedGreetMutations.current.some(
                        ([queuedGreetMutation]) =>
                          mutation.idempotencyKey ===
                          queuedGreetMutation.idempotencyKey
                      ) ||
                      runningGreetMutations.current.some(
                        (runningGreetMutations) =>
                          mutation.idempotencyKey ===
                          runningGreetMutations.idempotencyKey
                      )
                  )
                  .filter(
                    (mutation) =>
                      // Only keep mutations whose effects haven't been observed.
                      !observedIdempotencyKeys.current.has(
                        mutation.idempotencyKey
                      )
                  )
              )


              setResponse(GreetingsResponse.fromBinary(response.response));
            }
          } catch (e: unknown) {
            if (getAbortController().signal.aborted) {
              return;
            }

            setError(e);
            setIsLoading(true);

            // Run a mutation in the event that we are trying to read
            // from an unconstructed actor and the mutation will peform
            // the construction.
            //
            // TODO(benh): only do this if the reason we failed to
            // read was because the actor does not exist.
            for (const run of queuedMutations.current) {
              queuedMutations.current.shift();
              run();
              break;
            }

            // TODO(benh): check invariant
            // 'flushMutations.current === undefined' but don't
            // throw an error since that will just retry, instead
            // add support for "bailing" from a 'retry' by calling a
            // function passed into the lambda that 'retry' takes.
            flushMutations.current = new Event();

            throw e;
          }
        });
      };

      loop();
    }, []);

    return {
      response,
      isLoading,
      error,
      mutations: {
        Greet,
      },
      pendingGreetMutations: unobservedPendingGreetMutations,
      failedGreetMutations,
      recoveredGreetMutations: recoveredGreetMutations.current.map(
        ([mutation, run]) => ({ ...mutation, run: run })
      ),
    };
  };


  const Greet = async (partialRequest: PartialMessage<GreetRequest> = {}) => {
    const request = partialRequest instanceof GreetRequest ? partialRequest : new GreetRequest(partialRequest);
    const requestBody = request.toJson();
    // Invariant here is that we use the '/package.service.method'
    // path and HTTP 'POST' method.
    //
    // See also 'resemble/helpers.py'.
    const req = newRequest(requestBody, "/hello_world.v1.Greeter.Greet", "POST");

    const response = await fetch(req);
    return await response.json();
  };


  async function _Mutation<
    Request extends
GreetRequest,
    Response extends    GreetResponse  >(
    path: string,
    mutation: Mutation<Request>,
    request: Request,
    idempotencyKey: string,
    setUnobservedPendingMutations: Dispatch<
      SetStateAction<Mutation<Request>[]>
    >,
    abortController: AbortController,
    shouldClearFailedMutations: MutableRefObject<boolean>,
    setFailedMutations: Dispatch<SetStateAction<Mutation<Request>[]>>,
    runningMutations: MutableRefObject<Mutation<Request>[]>,
    flushMutations: MutableRefObject<Event | undefined>,
    queuedMutations: MutableRefObject<Array<() => void>>,
    requestType: { new (request: Request): Request },
    responseTypeFromJson: (json: any) => Response
  ): Promise<ResponseOrError<Response>> {

    try {
      return await retryForever(
        async () => {
          try {
            setUnobservedPendingMutations(
              (mutations) => {
                return mutations.map((mutation) => {
                  if (mutation.idempotencyKey === idempotencyKey) {
                    return { ...mutation, isLoading: true };
                  }
                  return mutation;
                });
              }
            );
            const req: Request =
              request instanceof requestType
                ? request
                : new requestType(request);

            const response = await fetch(
              newRequest(req.toJson(), path, "POST", idempotencyKey),
              { signal: abortController.signal }
            );

            if (!response.ok && response.headers.has("grpc-status")) {
              const grpcStatus = response.headers.get("grpc-status");
              let grpcMessage = response.headers.get("grpc-message");
              const error = new Error(
                `'hello_world.v1.Greeter' for '${actorId}' responded ` +
                  `with status ${grpcStatus}` +
                  `${grpcMessage !== null ? ": " + grpcMessage : ""}`
              );

              if (shouldClearFailedMutations.current) {
                shouldClearFailedMutations.current = false;
                setFailedMutations([
                  { request, idempotencyKey, isLoading: false, error },
                ]);
              } else {
                setFailedMutations((failedMutations) => [
                  ...failedMutations,
                  { request, idempotencyKey, isLoading: false, error },
                ]);
              }
              setUnobservedPendingMutations(
                (mutations) =>
                  mutations.filter(
                    (mutation) => mutation.idempotencyKey !== idempotencyKey
                  )
              );

              return { error } as ResponseOrError<Response>;
            }
            if (!response.ok) {
              throw new Error("Failed to fetch");
            }
            const jsonResponse = await response.json();
            return {
              response: responseTypeFromJson(jsonResponse),
            };
          } catch (e: unknown) {
            setUnobservedPendingMutations(
              (mutations) =>
                mutations.map((mutation) => {
                  if (mutation.idempotencyKey === idempotencyKey) {
                    return { ...mutation, error: e, isLoading: false };
                  } else {
                    return mutation;
                  }
                })
            );

            if (abortController.signal.aborted) {
              // TODO(benh): instead of returning 'undefined' as a
              // means of knowing that we've aborted provide a way
              // of "bailing" from a 'retry' by calling a function
              // passed into the lambda that 'retry' takes.
              return { error: new Error("Aborted") };
            } else {
              throw e;
            }
          }
        },
        {
          maxBackoffSeconds: 3,
        }
      );
    } finally {
      // NOTE: we deliberately DO NOT remove from
      // 'unobservedPendingMutations' but instead wait
      // for a response first so that we don't cause a render
      // before getting the updated state from the server.

      if (
        flushMutations.current !== undefined &&
        runningMutations.current.length === 0
      ) {
        flushMutations.current.set();
      } else {
        // Dequeue 1 queue and run 1 mutation from it.
        for (const run of queuedMutations.current) {
          queuedMutations.current.shift();
          run();
          break;
        }
      }
    }
  }

  async function* ReactQuery(
    request: IQueryRequest,
    signal: AbortSignal
  ): AsyncGenerator<IQueryResponse, void, unknown> {
    const response = await fetch(
      newRequest(QueryRequest.toJson(request), "/query", "POST"),
      { signal: signal }
    );

    if (response.body == null) {
      throw new Error("Unable to read body of response");
    }

    const reader = response.body
      .pipeThrough(new TextDecoderStream())
      .getReader();

    if (reader === undefined) {
      throw new Error("Not able to instantiate reader on response body");
    }

    while (true) {
      const { value, done } = await reader.read();
      if (done) {
        break;
      } else {
        yield QueryResponse.fromJson(JSON.parse(parseStreamedValue(value)));
      }
    }
  }

  return {
    Greetings,
    useGreetings,
    Greet,
  };
};



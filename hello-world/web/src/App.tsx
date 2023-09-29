// Add a comment: you can choose any id because the greeter will get constructed.
import { useState } from "react";
import css from "./App.module.css";
import { Greeter } from "./api/hello_world/v1/greeter_rsm";

const GREETER_ID = "greeter-hello-world";

const Greeting: React.FC<{ text: string }> = ({ text }) => {
  return <div className={css.greeting}>{text}</div>;
};

const App = () => {
  const [greeting, setGreeting] = useState("");
  const greeter = Greeter({ actorId: GREETER_ID });
  const { useGreetings, Greet } = greeter;

  const { response } = useGreetings();

  return (
    <div className={css.greetings}>
      <input
        type="text"
        placeholder="Hello, World!"
        className={css.textInput}
        onChange={(e) => setGreeting(e.target.value)}
      />
      <button className={css.button} onClick={() => Greet({ greeting })}>
        Greet
      </button>
      {response !== undefined &&
        response.greetings.length > 0 &&
        response.greetings.map((greeting: string) => (
          <Greeting text={greeting} />
        ))}
    </div>
  );
};

export default App;

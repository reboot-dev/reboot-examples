import {
  ResembleClient,
  ResembleClientProvider,
} from "@reboot-dev/resemble-react";
import ReactDOM from 'react-dom/client';
import App from './App';
import reportWebVitals from './reportWebVitals';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
const client = new ResembleClient("http://127.0.0.1:9991");

root.render(
  <ResembleClientProvider client={client}>
    <App />
  </ResembleClientProvider>
);

reportWebVitals();

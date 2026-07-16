import React from "react";
import ReactDOM from "react-dom/client";
import "antd/dist/reset.css";
import "./styles.css";
import App from "./App";
import { initializeAuthentication } from "./auth/keycloak";

const root = ReactDOM.createRoot(document.getElementById("root")!);

async function bootstrap() {
  try {
    const authenticated = await initializeAuthentication();
    if (!authenticated) {
      return;
    }
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
  } catch (error) {
    root.render(
      <main className="auth-error">
        <h1>Unable to start sign-in</h1>
        <p>{error instanceof Error ? error.message : "Identity provider configuration failed."}</p>
        <button type="button" onClick={() => window.location.reload()}>
          Retry
        </button>
      </main>
    );
  }
}

void bootstrap();

import Keycloak from "keycloak-js";

export const keycloak = new Keycloak({
  url: import.meta.env.VITE_KEYCLOAK_URL || "http://localhost:8180",
  realm: import.meta.env.VITE_KEYCLOAK_REALM || "trading-demo",
  clientId: import.meta.env.VITE_KEYCLOAK_CLIENT_ID || "trading-demo-frontend"
});

let initPromise: Promise<boolean> | undefined;

export function initializeAuthentication(): Promise<boolean> {
  if (initPromise) {
    return initPromise;
  }

  initPromise = keycloak.init({
    onLoad: "login-required",
    pkceMethod: "S256",
    checkLoginIframe: false
  });
  return initPromise;
}

export async function getAccessToken(): Promise<string> {
  if (!keycloak.authenticated) {
    await keycloak.login();
    throw new Error("Authentication is required");
  }

  try {
    await keycloak.updateToken(30);
  } catch {
    await keycloak.login();
    throw new Error("The login session has expired");
  }

  if (!keycloak.token) {
    throw new Error("No access token is available");
  }
  return keycloak.token;
}

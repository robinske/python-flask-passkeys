import {
  get,
  parseRequestOptionsFromJSON,
} from "https://cdn.jsdelivr.net/npm/@github/webauthn-json/dist/esm/webauthn-json.browser-ponyfill.js";

import { checkSupport, handleFormSubmit } from "./scripts.js";

checkSupport();

try {
  const passkeyFn = (publicKey) =>
    get(parseRequestOptionsFromJSON({ publicKey }));
  await handleFormSubmit("challenges", passkeyFn);
} catch (error) {
  flash(error.message, "error");
  console.error(`[Error] ${error.message}`);
}

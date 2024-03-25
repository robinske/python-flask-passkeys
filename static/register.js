import {
  create,
  parseCreationOptionsFromJSON,
} from "https://cdn.jsdelivr.net/npm/@github/webauthn-json/dist/esm/webauthn-json.browser-ponyfill.js";

import { checkSupport, flash, handleFormSubmit } from "./scripts.js";

checkSupport();

try {
  const passkeyFn = (publicKey) =>
    create(parseCreationOptionsFromJSON({ publicKey }));
  await handleFormSubmit("factors", passkeyFn);
} catch (error) {
  flash(error.message, "error");
  console.error(`[Error] ${error.message}`);
}

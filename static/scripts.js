import { supported } from "https://cdn.jsdelivr.net/npm/@github/webauthn-json/dist/esm/webauthn-json.browser-ponyfill.js";

let flash = (message, type) => {
  let element = document.getElementById("client-flash");
  element.className = "flash";
  element.classList.add(type);
  element.textContent = message;
  element.style.display = "block";
};

let checkSupport = () => {
  if (!supported()) {
    flash(
      "Passkeys not supported on this browser. More info: https://caniuse.com/passkeys",
      "error"
    );
  }
};

let handleFormSubmit = async (formType, passkeyFn) => {
  const form = document.getElementById(`create-${formType}`);
  form.addEventListener("submit", async function (event) {
    try {
      event.preventDefault();
      let formData = new FormData(event.target);

      let createResponse = await fetch(`/${formType}/create`, {
        method: "POST",
        body: formData,
      });

      let publicKey = await createResponse.json();
      console.log(`[Server] Public Key: ${JSON.stringify(publicKey, null, 2)}`);

      let credential = await passkeyFn(publicKey);
      console.log(
        `[Browser] Credential: ${JSON.stringify(credential, null, 2)}`
      );

      let verifyResponse = await fetch(`/${formType}/verify`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credential),
      });

      let verifyResponseJson = await verifyResponse.json();
      let jsonStr = JSON.stringify(verifyResponseJson, null, 2);
      console.log(`[Server] Verify Response: ${jsonStr}`);

      if (verifyResponse.ok) {
        flash(`Successfully processed.`, "success");

        let respDisplay = document.getElementById("json-response");
        respDisplay.style.display = "block";
        respDisplay.innerHTML = `<pre>${jsonStr}</pre>`;
      } else {
        throw new Error("Failed to verify the passkey on the server.");
      }
    } catch (error) {
      console.error(`[Error] ${error.message}`);
      flash(error.message, "error");
    }
  });
};

export { flash, checkSupport, handleFormSubmit };

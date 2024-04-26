import {
  create,
  get,
  parseCreationOptionsFromJSON,
  parseRequestOptionsFromJSON,
  supported,
} from "https://cdn.jsdelivr.net/npm/@github/webauthn-json/dist/esm/webauthn-json.browser-ponyfill.js";

let flash = (message, type) => {
  // clear old flash messages first
  let flashMsgs = document.getElementsByClassName("flash");
  for (let i = 0; i < flashMsgs.length; i++) {
    flashMsgs[i].style.display = "none";
  }

  let element = document.getElementById("flash-msg");
  element.classList.add(type);
  element.textContent = message;
  element.style.display = "block";
};

const router = {
  register: "/factors",
  login: "/challenges",
};

if (!supported()) {
  flash(
    "Passkeys not supported on this browser. More info: https://caniuse.com/passkeys",
    "error"
  );
}

let getPublicKey = async function (route, username = null) {
  let formData = new FormData();
  if (username !== null) {
    formData.append("username", username);
  }

  let response = await fetch(`${route}/create`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let errorJson = await response.json();
    throw new Error(errorJson.message);
  }

  let publicKey = await response.json();
  console.log(`[Server] Public Key: ${JSON.stringify(publicKey, null, 2)}`);
  return publicKey;
};

let verifyCredential = async function (credential, route) {
  console.log(`[Browser] Credential: ${JSON.stringify(credential, null, 2)}`);

  let verifyResponse = await fetch(`${route}/verify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credential),
  });

  let verifyResponseJson = await verifyResponse.json();

  // TODO the redirect happens too fast to see this - display on next page instead?
  let jsonStr = JSON.stringify(verifyResponseJson, null, 2);
  console.log(`[Server] Verify Response: ${jsonStr}`);

  if (
    verifyResponse.ok &&
    ["verified", "approved"].includes(verifyResponseJson.status)
  ) {
    flash(`Success!`, "success");
    window.location.replace(`/passkeys`);
  } else {
    throw new Error("Failed to verify the passkey on the server.");
  }
};

const form = document.getElementById(`auth`);
form.addEventListener("submit", async function (event) {
  try {
    event.preventDefault();
    let formType = event.submitter.id;
    let username = document.getElementById("username").value;
    let route = router[formType];
    let publicKey = await getPublicKey(route, username);

    let credential;
    switch (formType) {
      case "register":
        credential = await create(parseCreationOptionsFromJSON({ publicKey }));
        break;
      case "login":
        credential = await get(parseRequestOptionsFromJSON({ publicKey }));
        break;
      default:
        throw new Error(`Invalid form type: ${formType}`);
    }

    await verifyCredential(credential, route);
  } catch (error) {
    console.error(`[Error] ${error.message}`);
    flash(error.message, "error");
  }
});

// auto detect login and prompt for passkey
// https://web.dev/articles/webauthn-discoverable-credentials
let autoLogin = async function () {
  try {
    let route = router["login"];
    let publicKey = await getPublicKey(route);
    let credential = await get(parseRequestOptionsFromJSON({ publicKey }));
    await verifyCredential(credential, route);
  } catch (error) {
    console.error(`[Error] ${error.message}`);
    flash(error.message, "error");
  }
};

// TODO - do condintional mediation
// https://web.dev/articles/passkey-form-autofill
if (window.location.pathname === "/login") {
  autoLogin();
}

let loginLink = document.getElementById("login");
loginLink.addEventListener("click", function (event) {
  event.preventDefault();

  try {
    autoLogin();
  } catch (error) {
    window.location.replace("/login");
  }
});

// Sign in function
async function signIn() {
  const state = generateRandomString(32);
  const codeVerifier = generateRandomString(128);
  const codeChallenge = await generateCodeChallenge(codeVerifier);

  // Store state and verifier in sessionStorage
  sessionStorage.setItem("pkce_state", state);
  sessionStorage.setItem("pkce_code_verifier", codeVerifier);
  sessionStorage.setItem("remember_me", "true");

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: config.responseType,
    scope: config.scope,
    redirect_uri: config.redirectUri,
    state: state,
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
  });

  window.location.href = `${config.cognitoDomain}/login?${params.toString()}`;
}

function signOut() {
  // Clear tokens
  sessionStorage.clear();
  localStorage.removeItem(USER_TOKEN_STORAGE_KEY);

  // Redirect to Cognito logout
  const params = new URLSearchParams({
    client_id: config.clientId,
    logout_uri: config.redirectUri,
  });

  window.location.href = `${config.cognitoDomain}/logout?${params.toString()}`;
}

// Signup redirect
function signUp() {
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: config.responseType,
    scope: config.scope,
    redirect_uri: config.redirectUri,
  });

  window.location.href = `${config.cognitoDomain}/signup?${params.toString()}`;
}

// Exchange authorization code for tokens
async function exchangeCodeForTokens(code) {
  const codeVerifier = sessionStorage.getItem("pkce_code_verifier");

  const params = new URLSearchParams({
    grant_type: "authorization_code",
    client_id: config.clientId,
    code: code,
    redirect_uri: config.redirectUri,
    code_verifier: codeVerifier,
  });

  try {
    const response = await fetch(`${config.cognitoDomain}/oauth2/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: params.toString(),
    });

    if (!response.ok) {
      throw new Error("Token exchange failed");
    }

    const tokens = await response.json();

    // Clean up PKCE data
    sessionStorage.removeItem("pkce_state");
    sessionStorage.removeItem("pkce_code_verifier");

    return tokens;
  } catch (error) {
    console.error("Error exchanging code for tokens:", error);
    throw error;
  }
}

// Handle OAuth callback
async function handleCognitoCallback() {
  $("#welcome-loading").show();
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");
  const state = urlParams.get("state");
  const error = urlParams.get("error");

  function errorMessage(message) {
    $("#welcome-message")
      .removeClass("alert-light")
      .addClass("alert-danger")
      .find("span")
      .text(message);
    $("#welcome-loading").hide();
  }

  if (error) {
    errorMessage("Authentication failed: " + error);
    return;
  }

  if (code && state) {
    const savedState = sessionStorage.getItem("pkce_state");

    const hasMismatch = state !== savedState;

    if (hasMismatch) {
      errorMessage("Security error: State mismatch");
      return;
    }

    try {
      const tokens = await exchangeCodeForTokens(code);

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);

      const idToken = tokens.id_token;
      const payload = parseJwt(idToken);
      if (!payload) {
        errorMessage("Invalid token received");
        return;
      }

      const groups = payload["cognito:groups"] || [];

      // Store token in localStorage for use in the redirected page
      localStorage.setItem(USER_TOKEN_STORAGE_KEY, idToken);

      // Redirect based on role
      // Decide which page is the home page by the group
      if (groups.includes("admin")) {
        window.location.href = "/pages/manager.html"; // Redirect to agent home page
      } else if (groups.includes("agent")) {
        window.location.href = "/pages/agent.html"; // Redirect to admin home page
      } else {
        $("#welcome-message")
          .find("span")
          .text(
            `Welcome ${payload.email}!, To obtain appropriate permissions to use the system, please contact the administrator.`
          );
        $("#welcome-loading").hide();
      }
    } catch (error) {
      console.error("Error during token exchange:", error);
      errorMessage("Failed to complete authentication. Please try again.");
    }
  } else {
    $("#welcome-loading").hide();
  }
}

function getUserTokenData() {
  const idToken = localStorage.getItem(USER_TOKEN_STORAGE_KEY);
  if (idToken) {
    const payload = parseJwt(idToken);
    return payload;
  }
  return null;
}

function getUserEmail() {
  const user = getUserTokenData();
  if (user) return user.email;
}

function updateNavbar() {
  const userDropdown = document.getElementById("userProfileDropdown");

  const userImage = $(".user-profile-img");
  const userName = $(".user-name");

  const user = getUserTokenData();
  const isLoggedIn = user != null;
  if (!isLoggedIn) {
    signOut();
    return;
  }
  const groups = user["cognito:groups"] || [];
  const group = groups.length > 0 ? ` (${groups[0]}) ` : "";
  
  userName.text(`${user.email}${group}`);
  userImage.attr(
    "src",
    `https://ui-avatars.com/api/?name=${user.email}&background=0d6efd&color=fff`
  );
  userDropdown.style.display = "block";
  
}

// helper functions

// Base64 URL encode
function base64UrlEncode(buffer) {
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
  return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=/g, "");
}

// Generate code challenge for PKCE
async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hash = await crypto.subtle.digest("SHA-256", data);
  return base64UrlEncode(hash);
}

// Generate random string for PKCE
function generateRandomString(length) {
  const charset =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
  let result = "";
  const values = new Uint8Array(length);
  crypto.getRandomValues(values);
  for (let i = 0; i < length; i++) {
    result += charset[values[i] % charset.length];
  }
  return result;
}

// Parse JWT token
function parseJwt(token) {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload;
  } catch (e) {
    console.error("Error parsing JWT:", e);
    return null;
  }
}
// Configuration
const isLocalHost = location.hostname === "localhost" || location.hostname === "127.0.0.1";

const config = {
  cognitoDomain: 'https://us-east-1z6m8owbky.auth.us-east-1.amazoncognito.com',
  clientId: '3bu29jc53ei1bap4es6tlqm0f5',
  redirectUri: isLocalHost
    ? 'http://localhost:62786/index.html'
    : 'https://insurance-claim-damage-pages.s3.us-east-1.amazonaws.com/index.html',
  scope: 'email openid phone',
  responseType: 'code'
};

// Sign in function
async function signIn() {
  const state = generateRandomString(32);
  const codeVerifier = generateRandomString(128);
  const codeChallenge = await generateCodeChallenge(codeVerifier);

  // Store state and verifier in sessionStorage
  sessionStorage.setItem('pkce_state', state);
  sessionStorage.setItem('pkce_code_verifier', codeVerifier);
  sessionStorage.setItem('remember_me', 'true');

  // Build authorization URL
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: config.responseType,
    scope: config.scope,
    redirect_uri: config.redirectUri,
    state: state,
    code_challenge: codeChallenge,
    code_challenge_method: 'S256'
  });

  window.location.href = `${config.cognitoDomain}/login?${params.toString()}`;
}

function signOut() {
  // Clear tokens
  sessionStorage.clear();

  // Redirect to Cognito logout
  const params = new URLSearchParams({
    client_id: config.clientId,
    logout_uri: config.redirectUri
  });

  window.location.href = `${config.cognitoDomain}/logout?${params.toString()}`;
}

// Signup redirect
function signUp() {
  const params = new URLSearchParams({
    client_id: config.clientId,
    response_type: config.responseType,
    scope: config.scope,
    redirect_uri: config.redirectUri
  });

  window.location.href = `${config.cognitoDomain}/signup?${params.toString()}`;
}


// Check if user has a valid session (for "Remember Me" functionality)
async function checkExistingSession() {
  const token = localStorage.getItem('token');
  if (token) {
    try {
      const payload = parseJwt(token);
      const currentTime = Math.floor(Date.now() / 1000);

      // Check if token is still valid
      if (payload.exp && payload.exp > currentTime) {
        // Token is still valid, redirect to home page
        const groups = payload['cognito:groups'] || [];
        const homePageUrl = groups.includes('admin') ? '/pages/manager.html' : '/pages/agent.html';
        window.location.href = homePageUrl;
        return true;
      } else {
        // Token expired, try to refresh
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          await refreshAccessToken(refreshToken);
          return true;
        }
      }
    } catch (e) {
      console.error('Error checking session:', e);
    }
  }
  return false;
}

// Get valid access token (refresh if needed)
async function getValidAccessToken() {
  let accessToken = localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);

  // Check if token exists and is not expired
  if (accessToken && !isTokenExpired(accessToken)) {
    return accessToken;
  }

  // Try to refresh token
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    try {
      const newTokens = await refreshAccessToken(refreshToken);
      return newTokens.access_token;
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Redirect to login
      window.location.href = '/index.html';
      return null;
    }
  }

  // No valid token, redirect to login
  window.location.href = '/index.html';
  return null;
}

// Refresh access token using refresh token
async function refreshAccessToken(refreshToken) {
  const params = new URLSearchParams({
    grant_type: 'refresh_token',
    client_id: config.clientId,
    refresh_token: refreshToken
  });

  try {
    const response = await fetch(`${config.cognitoDomain}/oauth2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const tokens = await response.json();

    // Update stored tokens
    localStorage.setItem('token', tokens.id_token);
    localStorage.setItem('access_token', tokens.access_token);

    // Redirect to home page
    redirectToHomePage(tokens.id_token);

    return tokens;
  } catch (error) {
    console.error('Error refreshing token:', error);
    localStorage.clear();
    throw error;
  }
}

// Exchange authorization code for tokens
async function exchangeCodeForTokens(code) {
  const codeVerifier = sessionStorage.getItem('pkce_code_verifier');

  const params = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: config.clientId,
    code: code,
    redirect_uri: config.redirectUri,
    code_verifier: codeVerifier
  });

  try {
    const response = await fetch(`${config.cognitoDomain}/oauth2/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    if (!response.ok) {
      throw new Error('Token exchange failed');
    }

    const tokens = await response.json();

    // Clean up PKCE data
    sessionStorage.removeItem('pkce_state');
    sessionStorage.removeItem('pkce_code_verifier');

    return tokens;
  } catch (error) {
    console.error('Error exchanging code for tokens:', error);
    throw error;
  }
}

// Redirect to appropriate page based on user role
function redirectToHomePage(idToken) {
  const payload = parseJwt(idToken);
  if (!payload) {
    showError('Invalid token received');
    return;
  }

  const groups = payload['cognito:groups'] || [];

  // Store token in localStorage for use in the redirected page
  localStorage.setItem('token', idToken);

  // Decide which page is the home page by the group
  const homePageUrl = groups.includes('admin') ? '/pages/manager.html' : '/pages/agent.html';

  // Redirect to home page
  window.location.href = homePageUrl;
}

// Handle OAuth callback
async function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error = urlParams.get('error');

  if (error) {
    console.error('OAuth error:', error);
    showError('Authentication failed: ' + error);
    return;
  }

  if (code && state) {
    const savedState = sessionStorage.getItem('pkce_state');

    if (state !== savedState) {
      console.error('State mismatch');
      showError('Security error: State mismatch');
      return;
    }

    try {
      const tokens = await exchangeCodeForTokens(code);

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);

      // Redirect based on role
      redirectToHomePage(tokens.id_token);
    } catch (error) {
      console.error('Error during token exchange:', error);
      showError('Failed to complete authentication. Please try again.');
    }
  } else {
    // No code in URL, initiate sign-in
    await signIn();
  }
}


function getUserTokenData() {
  const idToken = localStorage.getItem(USER_TOKEN_STIRAGE_KEY);
  if (idToken) {
    const payload = JSON.parse(atob(idToken.split('.')[1]));
    return payload;
  }
  return null;
}

function getUserEmail() {
  const user = getUserTokenData();
  if (user)
    return user.email;
}

function getUserGroup() {
  const user = getUserTokenData();
  //if (user)
  //  return user.cognito: groups

}

let isLoggedIn = false;

function toggleUserState() {
  isLoggedIn = !isLoggedIn;
  updateNavbar();
}

function updateNavbar() {
  const userDropdown = document.getElementById('userProfileDropdown');

  const userImage = $('.user-profile-img');
  const userName = $('.user-name');

  const user = getUserTokenData();
  if (!user) {
    redirectToLogoutPage();
    return;
  }
  const groups = user['cognito:groups'] || [];
  const group = groups.length > 0 ? ` (${groups[0]}) ` : '';
  isLoggedIn = user != null;
  if (isLoggedIn) {
    userName.text(`${user.email}${group}`);
    userImage.attr('src', `https://ui-avatars.com/api/?name=${user.email}&background=0d6efd&color=fff`)
    userDropdown.style.display = 'block';
  } else {
    userDropdown.style.display = 'none';
  }
}

function handleLogout(event) {
  event.preventDefault();
  localStorage.removeItem(USER_TOKEN_STIRAGE_KEY);
  toggleUserState();
  redirectToLogoutPage();
}

function redirectToLogoutPage() {
  const myLoginPageUri = IS_LOCALHOST ?
    'http://localhost:62786/index.html' :
    'https://insurance-claim-damage-pages.s3.us-east-1.amazonaws.com/index.html';
  const cognitoHostedUIUrl = `https://us-east-1mtfe5dbmy.auth.us-east-1.amazoncognito.com/login?client_id=4r8iur2dg3h8t5ngh7qf4a3cm7&response_type=token&scope=email+openid&redirect_uri=${encodeURIComponent(myLoginPageUri)}`;
  window.location.href = cognitoHostedUIUrl
}



// helper functions

// Base64 URL encode
function base64UrlEncode(buffer) {
  const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));
  return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
}

// Generate code challenge for PKCE
async function generateCodeChallenge(verifier) {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return base64UrlEncode(hash);
}

// Generate random string for PKCE
function generateRandomString(length) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  let result = '';
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
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload;
  } catch (e) {
    console.error('Error parsing JWT:', e);
    return null;
  }
}

// Show error
function showError(message) {
  document.getElementById('loadingDiv').innerHTML = `
                  <div class="error">
                      <h2>Authentication Error</h2>
                      <p>${message}</p>
                      <button onclick="window.location.href='${config.redirectUri}'">Try Again</button>
                  </div>
              `;
}


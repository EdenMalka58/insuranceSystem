// Configuration
const config = {
  cognitoDomain: 'https://us-east-1z6m8owbky.auth.us-east-1.amazoncognito.com',
  clientId: '3bu29jc53ei1bap4es6tlqm0f5',
  redirectUri: location.hostname === "localhost" || location.hostname === "127.0.0.1" 
      ? 'http://localhost:62786/index.html' //64580
    : 'https://insurance-claim-damage-pages.s3.us-east-1.amazonaws.com/index.html',
  scope: 'email openid phone',
  responseType: 'code',
  baseAPI: "https://azy4fomrz8.execute-api.us-east-1.amazonaws.com/prod",
};

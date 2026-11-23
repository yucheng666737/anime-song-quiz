// Copy this file to config.js for local overrides, or let build-config.mjs generate config.js in CI.
// Do NOT commit real secrets to Git.
window.APP_CONFIG = {
  // Primary AnimeThemes GraphQL endpoint (supports CORS natively)
  graphqlUrl: "https://graphql.animethemes.moe/",
  // Optional legacy REST fallback or custom proxy endpoint
  apiBase: "",
  // Optional media proxy prefix (e.g. "/media?u=" when using local server.py)
  mediaProxyUrl: ""
};

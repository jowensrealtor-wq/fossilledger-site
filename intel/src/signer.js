// TikTok Shop Open API request signing.
//
// Algorithm (per TikTok Shop Partner Center "Sign your API request",
// mirrored by TikTok's official SDKs):
//   1. Take every query parameter EXCEPT `sign` and `access_token`,
//      sort keys alphabetically, concatenate as {key}{value}.
//   2. Prepend the request path (e.g. /product/202309/products/search).
//   3. If the request has a JSON body, append the raw body string.
//   4. Wrap the whole string with the app secret on both ends.
//   5. HMAC-SHA256 with the app secret as key; hex-encode the digest.
// The result goes in the `sign` query parameter; the shop access token is
// sent in the `x-tts-access-token` header.

import crypto from 'node:crypto';

export function signRequest({ appSecret, apiPath, query, body }) {
  const keys = Object.keys(query)
    .filter((k) => k !== 'sign' && k !== 'access_token')
    .sort();
  let input = apiPath;
  for (const k of keys) input += k + String(query[k]);
  if (body) input += body;
  input = appSecret + input + appSecret;
  return crypto.createHmac('sha256', appSecret).update(input).digest('hex');
}

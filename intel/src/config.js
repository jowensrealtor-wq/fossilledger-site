// Central configuration for the TikTok Shop Intelligence framework.
// All credentials come from the environment — never hardcoded, never committed.
//
// The framework runs in AFFILIATE mode by default (TTS_ROLE=affiliate):
// you are a creator promoting marketplace products for commission, not a
// seller. Seller-only endpoints are gated off with an explicit
// explanation rather than failing cryptically.
//
// Required for live data pulls (TikTok Shop Partner / Open API):
//   TTS_APP_KEY        — Partner Center app key
//   TTS_APP_SECRET     — Partner Center app secret (used for request signing)
//   TTS_ACCESS_TOKEN   — creator-authorized access token (affiliate mode)
//   TTS_SHOP_CIPHER    — only in seller mode (TTS_ROLE=seller): shop cipher
//                        returned during shop authorization
//
// Optional:
//   TTS_API_BASE       — override API base (default: https://open-api.tiktokglobalshop.com)
//   TTS_REFRESH_TOKEN  — enables automatic access-token refresh
//   ANTHROPIC_API_KEY  — enables in-engine prose generation for scripts;
//                        without it the engine emits a grounded script brief
//                        for the operator/agent to voice.

import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const PATHS = {
  root: path.resolve(__dirname, '..'),
  state: path.resolve(__dirname, '..', 'state'),
};

export function loadConfig(env = process.env) {
  return {
    role: env.TTS_ROLE === 'seller' ? 'seller' : 'affiliate',
    appKey: env.TTS_APP_KEY || null,
    appSecret: env.TTS_APP_SECRET || null,
    accessToken: env.TTS_ACCESS_TOKEN || null,
    refreshToken: env.TTS_REFRESH_TOKEN || null,
    shopCipher: env.TTS_SHOP_CIPHER || null,
    apiBase: env.TTS_API_BASE || 'https://open-api.tiktokglobalshop.com',
    authBase: env.TTS_AUTH_BASE || 'https://auth.tiktok-shops.com',
    anthropicApiKey: env.ANTHROPIC_API_KEY || null,
  };
}

// Reports exactly which credentials are missing for a live pull.
// The framework refuses to synthesize data when this is non-empty.
export function missingCredentials(cfg) {
  const required = cfg.role === 'seller'
    ? ['appKey', 'appSecret', 'accessToken', 'shopCipher']
    : ['appKey', 'appSecret', 'accessToken'];
  const envNames = {
    appKey: 'TTS_APP_KEY',
    appSecret: 'TTS_APP_SECRET',
    accessToken: 'TTS_ACCESS_TOKEN',
    shopCipher: 'TTS_SHOP_CIPHER',
  };
  return required.filter((k) => !cfg[k]).map((k) => envNames[k]);
}

// TikTok Shop Open API client — the ONLY permitted data source for the
// framework. No third-party aggregators, no synthetic benchmarks.
//
// Every response is wrapped in a provenance envelope:
//   { ok, endpoint, pulled_at, data }        on success
//   { ok: false, endpoint, error, detail }   on failure
// Downstream layers must carry provenance through to output so every
// surfaced number traces back to a real API response.
//
// NOTE: endpoint versions (e.g. /analytics/202405/...) rotate as TikTok
// ships new API versions. If a call returns code 40000-series "path not
// found", check Partner Center docs for the current version segment and
// update ENDPOINTS below — do not fall back to guessed data.

import { signRequest } from './signer.js';
import { missingCredentials } from './config.js';

// `audience` gates endpoints by role: affiliate-creator credentials cannot
// call seller-scoped analytics/order APIs, and the client says so instead
// of returning a confusing signature/permission error.
export const ENDPOINTS = {
  // ---- Affiliate creator (default role) ----
  // Marketplace products open for collaboration: commission rate, price,
  // point-in-time sold count — the affiliate's product intelligence feed.
  affiliateMarketplaceProducts: {
    method: 'POST', audience: 'affiliate',
    path: '/affiliate_creator/202405/marketplace_products/search',
  },
  // Products currently in the creator's showcase.
  affiliateShowcaseProducts: {
    method: 'GET', audience: 'affiliate',
    path: '/affiliate_creator/202405/showcases/products',
  },
  // Creator's own affiliate orders — commission/GMV ground truth.
  affiliateCreatorOrders: {
    method: 'GET', audience: 'affiliate',
    path: '/affiliate_creator/202410/orders/search',
  },
  // Open collaborations (partner surface, also readable in affiliate mode).
  affiliateOpenCollab: {
    method: 'GET', audience: 'affiliate',
    path: '/affiliate_creator/202405/open_collaborations/products/search',
  },

  // ---- Seller mode (TTS_ROLE=seller) ----
  shopVideoOverview: { method: 'GET', audience: 'seller', path: '/analytics/202405/shop_videos/overview' },
  shopVideoList: { method: 'GET', audience: 'seller', path: '/analytics/202405/shop_videos' },
  shopVideoProducts: { method: 'GET', audience: 'seller', path: (id) => `/analytics/202405/shop_videos/${id}/products` },
  shopProductPerformanceList: { method: 'GET', audience: 'seller', path: '/analytics/202405/shop_products/performance' },
  shopProductPerformance: { method: 'GET', audience: 'seller', path: (id) => `/analytics/202405/shop_products/${id}/performance` },
  shopPerformance: { method: 'GET', audience: 'seller', path: '/analytics/202405/shop/performance' },
  orderSearch: { method: 'POST', audience: 'seller', path: '/order/202309/orders/search' },
  productSearch: { method: 'POST', audience: 'seller', path: '/product/202309/products/search' },
};

export class TikTokShopClient {
  constructor(cfg) {
    this.cfg = cfg;
  }

  // Hard gate: refuses to operate without real credentials. This is the
  // primary no-fabrication guard — there is no offline/demo mode.
  credentialGap() {
    const missing = missingCredentials(this.cfg);
    if (missing.length === 0) return null;
    return {
      ok: false,
      error: 'DATA_UNAVAILABLE',
      detail:
        `Live TikTok Shop data requires credentials that are not configured: ${missing.join(', ')}. ` +
        'Set them in the environment (see intel/README.md → Setup). ' +
        'No estimates or placeholder metrics will be substituted.',
      missing,
    };
  }

  async call(name, { query = {}, body = null, pathArg = null } = {}) {
    const gap = this.credentialGap();
    const spec = ENDPOINTS[name];
    const apiPath = typeof spec.path === 'function' ? spec.path(pathArg) : spec.path;
    if (gap) return { ...gap, endpoint: apiPath };
    if (spec.audience === 'seller' && this.cfg.role !== 'seller') {
      return {
        ok: false,
        endpoint: apiPath,
        error: 'ROLE_MISMATCH',
        detail:
          'Seller-scoped endpoint; this framework is running in affiliate mode. ' +
          'Affiliate credentials cannot read shop analytics/orders. Set TTS_ROLE=seller with shop-authorized credentials only if you also operate the shop.',
      };
    }

    const q = {
      app_key: this.cfg.appKey,
      timestamp: Math.floor(Date.now() / 1000),
      ...query,
    };
    if (this.cfg.shopCipher) q.shop_cipher = this.cfg.shopCipher;
    const bodyStr = body ? JSON.stringify(body) : '';
    q.sign = signRequest({
      appSecret: this.cfg.appSecret,
      apiPath,
      query: q,
      body: bodyStr,
    });

    const url = new URL(this.cfg.apiBase + apiPath);
    for (const [k, v] of Object.entries(q)) url.searchParams.set(k, String(v));

    let res, json;
    try {
      res = await fetch(url, {
        method: spec.method,
        headers: {
          'content-type': 'application/json',
          'x-tts-access-token': this.cfg.accessToken,
        },
        body: bodyStr || undefined,
      });
      json = await res.json();
    } catch (err) {
      return {
        ok: false,
        endpoint: apiPath,
        error: 'NETWORK_ERROR',
        detail: String(err && err.message ? err.message : err),
      };
    }

    if (!res.ok || (json && json.code !== 0)) {
      return {
        ok: false,
        endpoint: apiPath,
        error: 'API_ERROR',
        detail: json && json.message ? `code=${json.code} ${json.message}` : `HTTP ${res.status}`,
        raw: json,
      };
    }
    return {
      ok: true,
      endpoint: apiPath,
      pulled_at: new Date().toISOString(),
      data: json.data,
    };
  }

  // ---- Typed pulls: affiliate mode (default) ----

  // Marketplace intelligence feed. Sold counts are point-in-time; the
  // metrics layer derives momentum by diffing successive stored pulls.
  marketplaceProducts({ keyword = null, categoryId = null, pageSize = 50, pageToken } = {}) {
    const query = { page_size: pageSize };
    if (pageToken) query.page_token = pageToken;
    const body = { sort_by: 'UNITS_SOLD_DESC' };
    if (keyword) body.keyword = keyword;
    if (categoryId) body.category_id = categoryId;
    return this.call('affiliateMarketplaceProducts', { query, body });
  }

  showcaseProducts({ pageSize = 50, pageToken } = {}) {
    const query = { page_size: pageSize };
    if (pageToken) query.page_token = pageToken;
    return this.call('affiliateShowcaseProducts', { query });
  }

  // The affiliate's own commission/GMV ground truth.
  affiliateOrders({ createTimeGe, createTimeLt, pageSize = 100, pageToken } = {}) {
    const query = { page_size: pageSize };
    if (createTimeGe) query.create_time_ge = createTimeGe;
    if (createTimeLt) query.create_time_lt = createTimeLt;
    if (pageToken) query.page_token = pageToken;
    return this.call('affiliateCreatorOrders', { query });
  }

  affiliateOpenCollaborations({ keyword = null, pageSize = 50, pageToken } = {}) {
    const query = { page_size: pageSize };
    if (keyword) query.keyword = keyword;
    if (pageToken) query.page_token = pageToken;
    return this.call('affiliateOpenCollab', { query });
  }

  // ---- Typed pulls: seller mode ----

  videoOverview({ startDateGe, endDateLt }) {
    return this.call('shopVideoOverview', {
      query: { start_date_ge: startDateGe, end_date_lt: endDateLt },
    });
  }

  videoList({ startDateGe, endDateLt, pageSize = 50, pageToken, sortField = 'gmv' }) {
    const query = {
      start_date_ge: startDateGe,
      end_date_lt: endDateLt,
      page_size: pageSize,
      sort_field: sortField,
      sort_order: 'DESC',
    };
    if (pageToken) query.page_token = pageToken;
    return this.call('shopVideoList', { query });
  }

  productPerformanceList({ startDateGe, endDateLt, pageSize = 50, pageToken }) {
    const query = { start_date_ge: startDateGe, end_date_lt: endDateLt, page_size: pageSize };
    if (pageToken) query.page_token = pageToken;
    return this.call('shopProductPerformanceList', { query });
  }

  productPerformance(productId, { startDateGe, endDateLt }) {
    return this.call('shopProductPerformance', {
      pathArg: productId,
      query: { start_date_ge: startDateGe, end_date_lt: endDateLt },
    });
  }

  orders({ createTimeGe, createTimeLt, pageSize = 100, pageToken }) {
    const query = { page_size: pageSize };
    if (pageToken) query.page_token = pageToken;
    return this.call('orderSearch', {
      query,
      body: { create_time_ge: createTimeGe, create_time_lt: createTimeLt },
    });
  }

  products({ pageSize = 100, pageToken } = {}) {
    const query = { page_size: pageSize };
    if (pageToken) query.page_token = pageToken;
    return this.call('productSearch', { query, body: { status: 'ACTIVATE' } });
  }

}

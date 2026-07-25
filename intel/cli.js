#!/usr/bin/env node
// TikTok Shop Intelligence Agent — CLI entry point.
//
//   node intel/cli.js daily-pull
//   node intel/cli.js script "<product name | SKU>" [--category supplements]
//   node intel/cli.js log-product --name "X" --category beauty --sold 4300 \
//        --commission 15 [--price 14.99 --url URL]   (no-API mode: numbers
//        read off the Affiliate Center screen)
//   node intel/cli.js competitive-pull <category>
//   node intel/cli.js analyze <category>
//   node intel/cli.js observe --category X --url URL --hook stat-lead --proof data-fact \
//        --views N [--likes N --shares N --comments N] [--compliance removed --trigger "phrase"]
//   node intel/cli.js report [weekly|monthly] [--category X]
//   node intel/cli.js status

import { loadConfig, missingCredentials } from './src/config.js';
import { TikTokShopClient } from './src/client.js';
import { dailyPull, renderDashboard } from './src/dashboard.js';
import { generateScript } from './src/script-engine.js';
import { competitivePull, logObservation, runAnalysisCycle } from './src/competitive.js';
import { buildReport } from './src/report.js';
import { readState } from './src/store.js';
import { logProductSnapshot, manualFeed } from './src/manual.js';
import { HOOK_TYPES, PROOF_TYPES } from './src/patterns.js';

const cfg = loadConfig();
const client = new TikTokShopClient(cfg);
const [cmd, ...rest] = process.argv.slice(2);
const flags = parseFlags(rest);

try {
  switch (cmd) {
    case 'daily-pull': {
      const snap = await dailyPull(client);
      console.log(renderDashboard(snap));
      break;
    }
    case 'script': {
      const product = flags._[0];
      if (!product) die('usage: intel script "<product | SKU>" [--category X]');
      const out = await generateScript(client, cfg, { product, category: flags.category });
      if (out.status === 'SCRIPT_READY') {
        console.log(out.script + '\n');
        console.log('--- provenance ---');
        for (const d of out.brief.data_points) console.log(`  "${d.claim}" ← ${d.source.endpoint} @ ${d.source.pulled_at}`);
      } else if (out.status === 'BRIEF_READY') {
        console.log(out.note + '\n');
        console.log(JSON.stringify(out.brief, null, 2));
      } else {
        console.log(`${out.status}: ${out.detail}`);
        process.exitCode = 1;
      }
      break;
    }
    case 'competitive-pull': {
      const category = flags._[0];
      if (!category) die('usage: intel competitive-pull <category>');
      const cycle = await competitivePull(client, category);
      console.log(JSON.stringify(cycle, null, 2));
      break;
    }
    case 'analyze': {
      const category = flags._[0];
      if (!category) die('usage: intel analyze <category>');
      console.log(JSON.stringify(runAnalysisCycle(category), null, 2));
      break;
    }
    case 'observe': {
      const entry = logObservation({
        category: flags.category,
        video_url: flags.url,
        hook_type: flags.hook,
        proof_type: flags.proof,
        views: flags.views ? Number(flags.views) : null,
        likes: flags.likes ? Number(flags.likes) : null,
        shares: flags.shares ? Number(flags.shares) : null,
        comments: flags.comments ? Number(flags.comments) : null,
        cta_text: flags.cta || null,
        compliance_status: flags.compliance || 'clean',
        trigger_phrase: flags.trigger || null,
      });
      console.log(`logged: ${entry.video_url} [${entry.category}] ${entry.hook_type}/${entry.proof_type}`);
      break;
    }
    case 'log-product': {
      const entry = logProductSnapshot({
        name: flags.name || flags._[0],
        category: flags.category,
        sold: flags.sold,
        commission: flags.commission,
        price: flags.price,
        url: flags.url,
      });
      console.log(
        `logged: ${entry.name} — ${entry.units_sold_total} sold` +
          `${entry.commission_rate != null ? `, ${entry.commission_rate}% commission` : ''} (${entry.source} @ ${entry.logged_at})`,
      );
      const readings = manualFeed().length;
      console.log(`products tracked: ${readings}. Log the same product again tomorrow to activate momentum ranking.`);
      break;
    }
    case 'report': {
      const cadence = flags._[0] === 'monthly' ? 'monthly' : 'weekly';
      console.log(buildReport({ cadence, category: flags.category || null }));
      break;
    }
    case 'status': {
      const missing = missingCredentials(cfg);
      console.log('TikTok Shop Intelligence Agent — status');
      console.log(`  role: ${cfg.role}${cfg.role === 'affiliate' ? ' (creator/commission mode — set TTS_ROLE=seller for shop analytics)' : ''}`);
      console.log(
        `  credentials: ${missing.length
          ? `MISSING ${missing.join(', ')} — API pulls disabled; running on operator-reported Affiliate Center readings (intel log-product). No synthetic fallback exists.`
          : 'configured'}`,
      );
      console.log(`  operator-reported products tracked: ${manualFeed().length}`);
      console.log(`  prose generation: ${cfg.anthropicApiKey ? 'Claude API' : 'brief-only (set ANTHROPIC_API_KEY for in-engine prose)'}`);
      console.log(`  pulls stored: ${readState('pulls', []).length}`);
      console.log(`  competitive cycles: ${readState('competitive', []).length}`);
      console.log(`  compliance incidents: ${readState('incidents', []).length}`);
      console.log(`  scripts generated: ${readState('scripts', []).length}`);
      console.log(`  hook types: ${HOOK_TYPES.join(', ')}`);
      console.log(`  proof types: ${PROOF_TYPES.join(', ')}`);
      break;
    }
    default:
      die(
        'commands: daily-pull | script <product> | log-product | competitive-pull <category> | analyze <category> | observe | report [weekly|monthly] | status',
      );
  }
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exitCode = 1;
}

function parseFlags(args) {
  const out = { _: [] };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      out[args[i].slice(2)] = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
    } else out._.push(args[i]);
  }
  return out;
}

function die(msg) {
  console.error(msg);
  process.exit(1);
}

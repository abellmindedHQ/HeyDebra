#!/usr/bin/env node

/**
 * test-call.js - CLI tool to initiate a HoldPlease call
 *
 * Usage:
 *   node test/test-call.js --number "+18005452200" --navigate "1,0,rep" --alert "+18135343383"
 *   node test/test-call.js --script lufthansa
 *   node test/test-call.js --number "+18001234567" --script generic-human
 *
 * Options:
 *   --number, -n     Phone number to call
 *   --script, -s     IVR script name from config/ivr-scripts.json
 *   --navigate, -v   Navigation string (e.g., "1,0,rep")
 *   --alert, -a      Phone number to alert (default: ALERT_PHONE_NUMBER env)
 *   --base-url, -b   Server base URL (default: BASE_URL env or http://localhost:3978)
 *   --dry-run, -d    Show what would happen without making the call
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');

// Parse CLI arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {
    number: null,
    script: null,
    navigate: null,
    alert: process.env.ALERT_PHONE_NUMBER || null,
    baseUrl: process.env.BASE_URL || 'http://localhost:3978',
    dryRun: false
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--number': case '-n':
        parsed.number = args[++i];
        break;
      case '--script': case '-s':
        parsed.script = args[++i];
        break;
      case '--navigate': case '-v':
        parsed.navigate = args[++i];
        break;
      case '--alert': case '-a':
        parsed.alert = args[++i];
        break;
      case '--base-url': case '-b':
        parsed.baseUrl = args[++i];
        break;
      case '--dry-run': case '-d':
        parsed.dryRun = true;
        break;
      case '--help': case '-h':
        showHelp();
        process.exit(0);
    }
  }

  return parsed;
}

function showHelp() {
  console.log(`
╔══════════════════════════════════════════════════╗
║              HoldPlease Test Call                ║
╚══════════════════════════════════════════════════╝

Usage:
  node test/test-call.js --number "+18005452200" --navigate "1,0,rep"
  node test/test-call.js --script lufthansa
  node test/test-call.js --number "+18001234567" --alert "+18135343383"

Options:
  --number, -n     Phone number to call (required unless --script provides one)
  --script, -s     IVR script name from config/ivr-scripts.json
  --navigate, -v   Navigation string (comma-separated: digits=DTMF, text=speech)
                   Example: "1,0,rep" = press 1, press 0, say "representative"
  --alert, -a      Phone number to alert when human detected
  --base-url, -b   Server base URL (default: http://localhost:3978)
  --dry-run, -d    Show call plan without dialing
  --help, -h       Show this help

Available IVR Scripts:`);

  try {
    const scripts = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'config', 'ivr-scripts.json'), 'utf-8'));
    for (const [name, config] of Object.entries(scripts)) {
      console.log(`  ${name.padEnd(20)} ${config.number || '(no default number)'}`);
      if (config.context) console.log(`  ${''.padEnd(20)} ${config.context}`);
    }
  } catch (err) {
    console.log('  (could not load scripts)');
  }

  console.log('');
}

async function main() {
  const args = parseArgs();

  // Load script if specified
  let scriptConfig = null;
  if (args.script) {
    try {
      const scripts = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'config', 'ivr-scripts.json'), 'utf-8'));
      scriptConfig = scripts[args.script];
      if (!scriptConfig) {
        console.error(`❌ Unknown script: ${args.script}`);
        console.error(`Available: ${Object.keys(scripts).join(', ')}`);
        process.exit(1);
      }
    } catch (err) {
      console.error(`❌ Could not load IVR scripts: ${err.message}`);
      process.exit(1);
    }
  }

  // Determine target number
  const targetNumber = args.number || (scriptConfig && scriptConfig.number);
  if (!targetNumber) {
    console.error('❌ No phone number provided. Use --number or --script with a default number.');
    process.exit(1);
  }

  // Determine navigation steps
  let navSteps = [];
  if (scriptConfig) {
    navSteps = scriptConfig.steps;
  } else if (args.navigate) {
    const { parseNavigateString } = require('../src/caller');
    navSteps = parseNavigateString(args.navigate);
  }

  // Display call plan
  console.log('');
  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║              HoldPlease Call Plan                ║');
  console.log('╠══════════════════════════════════════════════════╣');
  console.log(`║ Target:  ${targetNumber.padEnd(39)} ║`);
  console.log(`║ Alert:   ${(args.alert || 'NOT SET').padEnd(39)} ║`);
  console.log(`║ Script:  ${(args.script || 'custom').padEnd(39)} ║`);
  console.log(`║ Server:  ${args.baseUrl.padEnd(39)} ║`);
  console.log('╠══════════════════════════════════════════════════╣');

  if (navSteps.length > 0) {
    console.log('║ Navigation:                                      ║');
    for (const step of navSteps) {
      const desc = step.label || `${step.action}: ${step.digit || step.text || step.seconds + 's'}`;
      console.log(`║   → ${desc.padEnd(43)} ║`);
    }
  } else {
    console.log('║ Navigation: none (straight hold)                 ║');
  }

  if (scriptConfig && scriptConfig.context) {
    console.log('╠══════════════════════════════════════════════════╣');
    console.log(`║ Context: ${scriptConfig.context.substring(0, 39).padEnd(39)} ║`);
    if (scriptConfig.context.length > 39) {
      console.log(`║          ${scriptConfig.context.substring(39, 78).padEnd(39)} ║`);
    }
  }

  console.log('╚══════════════════════════════════════════════════╝');
  console.log('');

  if (args.dryRun) {
    console.log('🏁 DRY RUN - No call will be made.');
    process.exit(0);
  }

  // Check for required env vars
  const missing = [];
  if (!process.env.TWILIO_ACCOUNT_SID) missing.push('TWILIO_ACCOUNT_SID');
  if (!process.env.TWILIO_AUTH_TOKEN) missing.push('TWILIO_AUTH_TOKEN');
  if (!process.env.TWILIO_PHONE_NUMBER) missing.push('TWILIO_PHONE_NUMBER');
  if (!process.env.OPENAI_API_KEY) missing.push('OPENAI_API_KEY');

  if (missing.length > 0) {
    console.error(`❌ Missing environment variables: ${missing.join(', ')}`);
    console.error('   Copy .env.example to .env and fill in your credentials.');
    process.exit(1);
  }

  // Make the call via API
  console.log('📞 Initiating call...');
  try {
    const response = await fetch(`${args.baseUrl}/api/call`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        number: targetNumber,
        script: args.script,
        navigate: args.navigate,
        alertNumber: args.alert
      })
    });

    const result = await response.json();

    if (result.success) {
      console.log(`✅ Call initiated: ${result.callSid}`);
      console.log('');
      console.log('📡 Listening for human detection...');
      console.log('   (Check server logs for real-time updates)');
      console.log('   Press Ctrl+C to stop monitoring.');

      // Poll for updates
      const pollInterval = setInterval(async () => {
        try {
          const healthRes = await fetch(`${args.baseUrl}/health`);
          const health = await healthRes.json();
          process.stdout.write(`\r⏳ Active calls: ${health.activeCalls} | Uptime: ${Math.floor(health.uptime)}s`);
        } catch (err) {
          // Server might be busy
        }
      }, 5000);

      process.on('SIGINT', () => {
        clearInterval(pollInterval);
        console.log('\n\n👋 Stopped monitoring. Call continues in background.');
        process.exit(0);
      });

    } else {
      console.error(`❌ Call failed: ${result.error}`);
      process.exit(1);
    }
  } catch (err) {
    console.error(`❌ Could not reach server at ${args.baseUrl}: ${err.message}`);
    console.error('   Make sure the server is running: npm start');
    process.exit(1);
  }
}

main().catch(err => {
  console.error(`❌ Fatal error: ${err.message}`);
  process.exit(1);
});

/**
 * Shared utilities for HoldPlease
 */

function log(message) {
  const timestamp = new Date().toISOString();
  console.log(`${timestamp} ${message}`);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { log, sleep };

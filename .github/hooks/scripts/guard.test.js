#!/usr/bin/env node
// guard.test.js — Smoke tests for the Solo-Code Permission Guard
// Usage: node .github/hooks/scripts/guard.test.js

const { execSync } = require("child_process");
const path = require("path");

const GUARD = path.join(__dirname, "guard.js");

let passed = 0;
let failed = 0;

function runGuard(input) {
  try {
    const result = execSync(`node "${GUARD}"`, {
      input: JSON.stringify(input),
      encoding: "utf8",
      timeout: 5000,
    });
    return JSON.parse(result.trim());
  } catch (e) {
    // exit code != 0 still gives us stdout
    if (e.stdout) return JSON.parse(e.stdout.trim());
    throw e;
  }
}

function test(label, input, expectedDecision) {
  try {
    const result = runGuard(input);
    const decision = result?.hookSpecificOutput?.permissionDecision;
    if (decision === expectedDecision) {
      console.log(`  ✅ ${label}`);
      passed++;
    } else {
      console.log(`  ❌ ${label}`);
      console.log(`     Expected: ${expectedDecision} | Got: ${decision}`);
      console.log(`     Input: ${JSON.stringify(input)}`);
      failed++;
    }
  } catch (e) {
    console.log(`  ❌ ${label} — ERROR: ${e.message}`);
    failed++;
  }
}

console.log("\n🛡️  Solo-Code Permission Guard — Smoke Tests\n");

// --- Should ALLOW ---
console.log("── ALLOW cases ──────────────────────────────");
test("Empty input", "", "allow");
test(
  "Normal bash read",
  { toolName: "execute_command", toolInput: { command: "ls -la" } },
  "allow",
);
test(
  "npm install",
  { toolName: "execute_command", toolInput: { command: "npm install" } },
  "allow",
);
test(
  "git status",
  { toolName: "execute_command", toolInput: { command: "git status" } },
  "allow",
);
test(
  "git commit",
  {
    toolName: "execute_command",
    toolInput: { command: 'git commit -m "fix: update"' },
  },
  "allow",
);
test(
  "Create safe file",
  { toolName: "create_file", toolInput: { path: "src/index.ts" } },
  "allow",
);
test(
  "Read file",
  { toolName: "read_file", toolInput: { path: "README.md" } },
  "allow",
);
test("Unknown tool", { toolName: "some_random_tool", toolInput: {} }, "allow");
test("Malformed JSON string", "not-valid-json", "allow");

// --- Should ASK ---
console.log("\n── ASK cases (destructive) ───────────────────");
test(
  "rm -rf",
  { toolName: "execute_command", toolInput: { command: "rm -rf ./dist" } },
  "ask",
);
test(
  "rm -r",
  { toolName: "execute_command", toolInput: { command: "rm -r node_modules" } },
  "ask",
);
test(
  "rm --force",
  {
    toolName: "execute_command",
    toolInput: { command: "rm --force file.txt" },
  },
  "ask",
);
test(
  "del /f",
  { toolName: "execute_command", toolInput: { command: "del /f /s *.tmp" } },
  "ask",
);
test(
  "rmdir /s",
  { toolName: "execute_command", toolInput: { command: "rmdir /s /q build" } },
  "ask",
);
test(
  "DROP TABLE",
  {
    toolName: "execute_command",
    toolInput: { command: 'psql -c "DROP TABLE users"' },
  },
  "ask",
);
test(
  "TRUNCATE TABLE",
  {
    toolName: "execute_command",
    toolInput: { command: "TRUNCATE TABLE logs" },
  },
  "ask",
);
test(
  "git push --force",
  {
    toolName: "execute_command",
    toolInput: { command: "git push --force origin main" },
  },
  "ask",
);
test(
  "git reset --hard",
  {
    toolName: "execute_command",
    toolInput: { command: "git reset --hard HEAD~2" },
  },
  "ask",
);
test(
  "git clean -fdx",
  { toolName: "execute_command", toolInput: { command: "git clean -fdx" } },
  "ask",
);
test(
  "mkfs",
  { toolName: "execute_command", toolInput: { command: "mkfs.ext4 /dev/sdb" } },
  "ask",
);
test(
  "shred",
  {
    toolName: "execute_command",
    toolInput: { command: "shred -u secrets.txt" },
  },
  "ask",
);
test(
  "dd if=",
  {
    toolName: "execute_command",
    toolInput: { command: "dd if=/dev/zero of=/dev/sda" },
  },
  "ask",
);
test(
  "Write to .env",
  { toolName: "create_file", toolInput: { path: ".env.production" } },
  "ask",
);
test(
  "Write credentials",
  {
    toolName: "write_file",
    toolInput: { filePath: "config/credentials.json" },
  },
  "ask",
);
test(
  "Write .pem file",
  { toolName: "create_file", toolInput: { path: "certs/server.pem" } },
  "ask",
);
test(
  "Write .key file",
  { toolName: "create_file", toolInput: { path: "keys/private.key" } },
  "ask",
);
test(
  "delete_file tool",
  { toolName: "delete_file", toolInput: { path: "important.md" } },
  "ask",
);
test(
  "remove_file tool",
  { toolName: "remove_file", toolInput: { path: "data.json" } },
  "ask",
);
test(
  "deleteFile (camel)",
  { toolName: "deleteFile", toolInput: { path: "file.txt" } },
  "ask",
);

// --- Summary ---
console.log("\n─────────────────────────────────────────────");
const total = passed + failed;
const emoji = failed === 0 ? "🎉" : "⚠️ ";
console.log(
  `${emoji} Results: ${passed}/${total} passed${failed > 0 ? `, ${failed} FAILED` : ""}\n`,
);

process.exit(failed > 0 ? 1 : 0);

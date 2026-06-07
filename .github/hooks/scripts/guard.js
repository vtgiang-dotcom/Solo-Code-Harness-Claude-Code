#!/usr/bin/env node
// .github/hooks/scripts/guard.js
// Solo-Code Permission Guard — PreToolUse Hook
// Intercepts destructive tool calls and requires user confirmation.

const readline = require("readline");

// --- Destructive pattern definitions ---
const DESTRUCTIVE_COMMANDS = [
  /rm\s+-[rf]+/i,
  /rm\s+--force/i,
  /del\s+\/[fqs]/i,
  /rmdir\s+\/s/i,
  /rd\s+\/s/i,
  /DROP\s+TABLE/i,
  /TRUNCATE\s+TABLE/i,
  /TRUNCATE\s+\w+/i,
  /git\s+push\s+--force/i,
  /git\s+reset\s+--hard/i,
  /git\s+clean\s+-[fdx]+/i,
  /mkfs/i,
  /format\s+[a-z]:/i,
  /shred\s+/i,
  /dd\s+if=/i,
  />\s*\/dev\/[sh]/i,
  /sudo\s+/i,
  /chmod\s+(?:-R\s+)?777/i,
  /curl\s+.*\s*\|\s*(?:bash|sh)/i,
  /wget\s+.*\s*\|\s*(?:bash|sh)/i,
];

const SENSITIVE_PATH_PATTERNS = [
  /\.env(\.|$)/i,
  /credentials/i,
  /secrets?(\.|$)/i,
  /\.pem$/i,
  /\.key$/i,
  /\.pfx$/i,
  /id_rsa/i,
  /\.htpasswd/i,
];

const ALWAYS_ASK_TOOLS = [
  "delete_file",
  "remove_file",
  "deleteFile",
  "removeFile",
];

function allow() {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "allow",
      },
    }),
  );
  process.exit(0);
}

function ask(reason) {
  process.stdout.write(
    JSON.stringify({
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "ask",
        permissionDecisionReason: `[Solo-Code Permission Guard] ${reason}`,
      },
    }),
  );
  process.exit(0);
}

// --- Main ---
let inputData = "";

const rl = readline.createInterface({ input: process.stdin });
rl.on("line", (line) => {
  inputData += line;
});
rl.on("close", () => {
  try {
    if (!inputData.trim()) {
      allow();
      return;
    }

    const hook = JSON.parse(inputData);
    const toolName = (hook.toolName || hook.tool_name || "").toLowerCase();
    const toolInput = hook.toolInput || hook.tool_input || {};

    // 1. Always-ask tools
    if (ALWAYS_ASK_TOOLS.some((t) => toolName.includes(t.toLowerCase()))) {
      ask(
        `Tool "${toolName}" performs a file deletion. Confirm before proceeding.`,
      );
      return;
    }

    // 2. Sensitive file writes
    const filePath = (
      toolInput.path ||
      toolInput.file_path ||
      toolInput.filePath ||
      ""
    ).toLowerCase();
    if (filePath && SENSITIVE_PATH_PATTERNS.some((p) => p.test(filePath))) {
      ask(
        `Writing to sensitive file path "${filePath}". Confirm before proceeding.`,
      );
      return;
    }

    // 3. Destructive shell commands
    const command = (toolInput.command || toolInput.cmd || "").toLowerCase();
    if (command) {
      for (const pattern of DESTRUCTIVE_COMMANDS) {
        if (pattern.test(command)) {
          ask(
            `Command contains a potentially destructive operation: "${command.substring(0, 80)}...". Confirm before proceeding.`,
          );
          return;
        }
      }
    }

    // Safe — allow
    allow();
  } catch (e) {
    // Parse failure → allow (don't block on bad input)
    allow();
  }
});

#!/usr/bin/env python3
"""
Continual Learning Hook — SQLite-based cross-session learning for AI agents.

Two-tier memory:
  - Global (~/.claude/learnings.db) — cross-project tool patterns, failure insights
  - Local  (.claude/memory/learnings.db) — repo conventions, project-specific mistakes

Events:
  - sessionStart   → Load prior learnings, surface to agent context
  - postToolUse    → Log tool outcome for pattern analysis (fast, <5ms)
  - sessionEnd     → Analyze failure patterns, persist insights, compact old data

Design: zero-config. Databases auto-create on first run.
         Local memory only activates inside a git repo.
"""

import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ── Configuration ──────────────────────────────────────────────────────────

GLOBAL_DB = Path.home() / ".claude" / "learnings.db"
LOCAL_DIR = Path(".claude") / "memory"
LOCAL_DB = LOCAL_DIR / "learnings.db"

# Learning decay: entries older than this with low hit_count get pruned
DECAY_DAYS = 60
DECAY_MIN_HITS = 3

# Tool log retention
LOG_RETENTION_DAYS = 7

# Failure threshold: tool must fail > N times to trigger a learning
FAILURE_THRESHOLD = 2

# Max learnings to surface at session start (per scope)
MAX_SURFACE_LEARNINGS = 5

# Timeout for DB operations (seconds)
DB_TIMEOUT = 5


# ── Database Initialization ────────────────────────────────────────────────

def get_conn(db_path: Path) -> sqlite3.Connection | None:
    """Open (or create) a SQLite database with WAL mode for concurrency."""
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(db_path), timeout=DB_TIMEOUT)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        return conn
    except Exception:
        return None


def init_db(db_path: Path) -> None:
    """Create tables and indexes if they don't exist."""
    conn = get_conn(db_path)
    if conn is None:
        return
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                file_path TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                last_seen TEXT DEFAULT (datetime('now')),
                hit_count INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS tool_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT,
                result TEXT,
                error_message TEXT,
                ts TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS session_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                event TEXT,
                ts TEXT DEFAULT (datetime('now'))
            );
            CREATE INDEX IF NOT EXISTS idx_learnings_scope ON learnings(scope);
            CREATE INDEX IF NOT EXISTS idx_learnings_category ON learnings(category);
            CREATE INDEX IF NOT EXISTS idx_tool_log_ts ON tool_log(ts);
            CREATE INDEX IF NOT EXISTS idx_tool_log_result ON tool_log(result);
        """)
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


def is_git_repo() -> bool:
    """Check if we're inside a git repository."""
    try:
        git_dir = Path(".git")
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())
    except Exception:
        return False


def repo_name() -> str:
    """Get the repository name from the current directory."""
    try:
        cwd = Path.cwd()
        # Try reading from .git/config or just use directory name
        git_config = cwd / ".git" / "config"
        if git_config.exists():
            return cwd.name
    except Exception:
        pass
    return Path.cwd().name


# ── Session Start ──────────────────────────────────────────────────────────

def on_session_start() -> None:
    """Load prior learnings and surface them for the agent."""
    init_db(GLOBAL_DB)

    has_global = GLOBAL_DB.exists()
    has_local = LOCAL_DB.exists() and is_git_repo()

    if not has_global and not has_local:
        # Fresh start — nothing to surface
        emit_context("continual_learning", "active", {"status": "fresh"})
        return

    context_parts = []

    # Load global learnings
    if has_global:
        conn = get_conn(GLOBAL_DB)
        if conn:
            try:
                count = conn.execute("SELECT COUNT(*) FROM learnings").fetchone()[0]
                if count > 0:
                    rows = conn.execute(
                        """SELECT category, content, hit_count
                           FROM learnings
                           ORDER BY hit_count DESC, last_seen DESC
                           LIMIT ?""",
                        (MAX_SURFACE_LEARNINGS,),
                    ).fetchall()
                    if rows:
                        items = "\n".join(
                            f"  • [{r[0]}] {r[1]} (×{r[2]})" for r in rows
                        )
                        context_parts.append(
                            f"Global learnings ({count} total):\n{items}"
                        )
            except Exception:
                pass
            finally:
                conn.close()

    # Load local (repo-specific) learnings
    if has_local:
        conn = get_conn(LOCAL_DB)
        if conn:
            try:
                count = conn.execute("SELECT COUNT(*) FROM learnings").fetchone()[0]
                if count > 0:
                    rows = conn.execute(
                        """SELECT category, content, hit_count
                           FROM learnings
                           ORDER BY hit_count DESC, last_seen DESC
                           LIMIT ?""",
                        (MAX_SURFACE_LEARNINGS,),
                    ).fetchall()
                    if rows:
                        items = "\n".join(
                            f"  • [{r[0]}] {r[1]} (×{r[2]})" for r in rows
                        )
                        context_parts.append(
                            f"Repo learnings for {repo_name()} ({count} total):\n{items}"
                        )
            except Exception:
                pass
            finally:
                conn.close()

    if context_parts:
        full_context = "\n\n".join(context_parts)
        # Write to stderr so it appears in the agent's context
        print(f"\n🧠 Continual learning — prior knowledge loaded:\n{full_context}\n", file=sys.stderr)
        emit_context("continual_learning", "loaded", {
            "global_count": has_global,
            "local_count": has_local,
            "learnings_summary": full_context,
        })
    else:
        emit_context("continual_learning", "active", {"status": "building"})


# ── Post Tool Use ──────────────────────────────────────────────────────────

def on_post_tool_use() -> None:
    """Log tool outcome for later pattern analysis."""
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    tool_name = input_data.get("toolName", "")
    if not tool_name:
        return

    # Determine result type
    tool_result = input_data.get("toolResult", {})
    result_type = tool_result.get("resultType", "unknown")

    # Capture error message for failure analysis
    error_message = None
    if result_type == "failure" or result_type == "error":
        error_output = tool_result.get("stderr", "") or tool_result.get("stdout", "") or tool_result.get("output", "")
        if isinstance(error_output, str) and error_output:
            # Truncate long error messages
            error_message = error_output[:500]

    init_db(GLOBAL_DB)
    conn = get_conn(GLOBAL_DB)
    if conn is None:
        return

    try:
        conn.execute(
            "INSERT INTO tool_log (tool_name, result, error_message) VALUES (?, ?, ?)",
            (tool_name, result_type, error_message),
        )
        conn.commit()
    except Exception:
        pass
    finally:
        conn.close()


# ── Session End ────────────────────────────────────────────────────────────

def on_session_end() -> None:
    """Analyze patterns, persist insights, compact old data."""
    if not GLOBAL_DB.exists():
        return

    conn = get_conn(GLOBAL_DB)
    if conn is None:
        return

    try:
        # Count recent tool usage
        total = conn.execute(
            """SELECT COUNT(*) FROM tool_log
               WHERE ts > datetime('now', ?)""",
            (f'-{LOG_RETENTION_DAYS} days',),
        ).fetchone()[0]

        failures = conn.execute(
            """SELECT COUNT(*) FROM tool_log
               WHERE result IN ('failure', 'error')
                 AND ts > datetime('now', ?)""",
            (f'-{LOG_RETENTION_DAYS} days',),
        ).fetchone()[0]

        # Detect repeated failure patterns
        fail_tools = conn.execute(
            """SELECT tool_name, COUNT(*) as cnt, error_message
               FROM tool_log
               WHERE result IN ('failure', 'error')
                 AND ts > datetime('now', '-24 hours')
               GROUP BY tool_name
               HAVING COUNT(*) > ?""",
            (FAILURE_THRESHOLD,),
        ).fetchall()

        # Store failure patterns as learnings
        for tool, cnt, err_msg in fail_tools:
            learning_content = f'Tool "{tool}" frequently fails (×{cnt} in 24h)'
            if err_msg:
                # Truncate error for the learning content
                truncated = err_msg[:200]
                learning_content += f' — last error: {truncated}'

            # Upsert: increment hit_count if similar learning exists
            existing = conn.execute(
                "SELECT id FROM learnings WHERE content LIKE ?",
                (f'%Tool "{tool}" frequently fails%',),
            ).fetchone()

            if existing:
                conn.execute(
                    "UPDATE learnings SET hit_count = hit_count + 1, last_seen = datetime('now') WHERE id = ?",
                    (existing[0],),
                )
            else:
                conn.execute(
                    """INSERT INTO learnings (scope, category, content, source)
                       VALUES ('global', 'tool_insight', ?, ?)""",
                    (learning_content, f"auto:{datetime.now(timezone.utc).strftime('%Y%m%d')}"),
                )

        # Compact: prune old tool logs
        conn.execute(
            "DELETE FROM tool_log WHERE ts < datetime('now', ?)",
            (f'-{LOG_RETENTION_DAYS} days',),
        )

        # Decay: prune old low-value learnings
        conn.execute(
            """DELETE FROM learnings
               WHERE last_seen < datetime('now', ?)
                 AND hit_count < ?""",
            (f'-{DECAY_DAYS} days', DECAY_MIN_HITS),
        )

        conn.commit()

        # Summary
        summary = f"🧠 Session reflected — tools: {total}, failures: {failures}"
        if fail_tools:
            tool_names = ", ".join(t for t, _, _ in fail_tools)
            summary += f"\n  ⚠️ Stored failure patterns for: {tool_names}"

        print(f"\n{summary}\n", file=sys.stderr)
        emit_context("continual_learning", "reflected", {
            "tools_total": total,
            "tools_failures": failures,
            "patterns_stored": len(fail_tools),
        })

    except Exception:
        pass
    finally:
        conn.close()


# ── Context Emission ───────────────────────────────────────────────────────

def emit_context(tag: str, event: str, data: dict) -> None:
    """Emit a structured context line that Claude Code can parse."""
    output = {
        "hook": "continual-learning",
        "tag": tag,
        "event": event,
        "data": data,
    }
    # Print JSON to stdout — Claude Code captures this as hook output
    print(json.dumps(output, ensure_ascii=False, default=str))


# ── Dispatch ───────────────────────────────────────────────────────────────

def main() -> None:
    event = sys.argv[1] if len(sys.argv) > 1 else ""

    handlers = {
        "sessionStart": on_session_start,
        "sessionEnd": on_session_end,
        "postToolUse": on_post_tool_use,
    }

    handler = handlers.get(event)
    if handler:
        handler()
    else:
        print(f"Usage: continual-learning.py <sessionStart|postToolUse|sessionEnd>", file=sys.stderr)
        print(f"Unknown event: {event}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

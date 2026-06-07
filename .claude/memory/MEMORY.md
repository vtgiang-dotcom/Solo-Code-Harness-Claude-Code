# Memory Index

> Persistent cross-session memory. The AI reads this at session start.

## Project
- [[project-conventions]] — Git workflow, code style, security

## Rules
- [[CLAUDE.md]] — Master rulebook with behavior rules, tool usage, security
- [[harness-design-intent]] — Why rules are long and must not be shortened (DeepSeek compensation)

## Tech Stack
- **Runtime**: Claude Code CLI + DeepSeek API (anthropic-compatible)
- **Models**: deepseek-v4-flash (simple tasks), deepseek-v4-pro (complex tasks)
- **Tools**: Python 3.10+ (scripts), Node 18+ (MCP + guard tests), PowerShell (launcher)
- **MCP**: sequential-thinking, memory, context7, playwright

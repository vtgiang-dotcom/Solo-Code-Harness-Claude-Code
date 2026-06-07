# Solo-Code-Harness — Specification (SPEC)

> Cac yeu cau HARD cua harness. Dung de verify + tai tao.

## 0. Ban chat & pham vi

- Harness la bo **cau hinh + rule + skill + script** bien Claude Code thanh "Solo-Code Engineer co ky luat".
- Khong phai app chay doc lap.

### 0.1 Ranh gioi LOAI TRU

| LOAI TRU | Vi du | Ly do |
|---|---|---|
| **Infrastructure runtime** | Docker, VM sandbox | Host OS + Claude Code da co lap process |
| **External server/protocol** | MCP memory server, OTEL | Claude Code + MCP da co session |
| **Package registry** | Plugin marketplace | Git repo da la registry |

**Nguyen tac**: Neu mot tinh nang can `pip install`, `npm install`, `docker run` → **KHONG thuoc harness**.

## 1. Cau truc thu muc [HARD]

Phai ton tai: `.claude/` `.github/` `.vscode/`

## 2. File cau hinh hop le [HARD]

- `.claude/settings.json` phai parse JSON hop le
- `.claude/CLAUDE.md` phai ton tai

## 3. Permission Guard [HARD]

- `.claude/settings.json` deny rules chan: rm -rf, DROP TABLE, git push --force, rmdir, del, Remove-Item
- `.github/hooks/scripts/guard.test.js` — 29/29 smoke tests

## 4. Script automation [HARD]

- `security_scan.py`: quet secret, loai tru .venv/node_modules
- Tat ca Python script phai pass `ruff check .` (0 loi)

## 5. Gitleaks [HARD]

- Phai co `.gitleaks.toml`
- Chay gitleaks → no leaks

## 6. Rulebook [SOFT]

`.claude/CLAUDE.md` phai co:
- Request classification (Question / Simple / Complex / Destructive / Review)
- Destructive op guard
- Socratic Gate
- Plan → implement → verify
- Git commit convention
- Model Selection (DeepSeek flash/pro)

## 7. Skills [SOFT]

10 skills trong `.claude/skills/`, moi skill co frontmatter day du: name, description, allowed-tools.

## 8. Memory [SOFT]

`.claude/memory/` — persistent cross-session memory.

## 9. Model Selection [SOFT]

- `claudecode.ps1` — smart launcher, interactive model choice
- `claudecode-pro.ps1` — pro shortcut

## 10. Rang buoc khi tai tao

- KHONG sua verify.sh hay test files de cho qua
- Pass tat ca quality gates: ruff, garden, test_integration, test_harness, security_scan

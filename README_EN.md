# ClawHub Publish Helper for OpenClaw

One-command publish helper for ClawHub skills.

[中文版本](README_CN.md)

---

## ✨ Features

- ✅ **Validate Skill Structure** - Check SKILL.md, scripts/, config/
- ✅ **Required Files Check** - Auto-detect missing files
- ✅ **Auto Retry** - Exponential backoff on rate limits
- ✅ **Rate Limit Handling** - Auto-wait 5min × attempt count
- ✅ **Publish Logging** - Log to publish-log.md

---

## 🚀 Installation

```bash
cd /root/.openclaw/workspace/skills
git clone https://github.com/williamwg2025/openclaw-clawhub-publish.git clawhub-publish
chmod +x clawhub-publish/publish.sh
```

---

## 📖 Usage

### Publish Skill

```bash
# Publish skill
cd clawhub-publish
./publish.sh model-switch

# Dry run (simulate)
./publish.sh auto-backup --dry-run

# View help
./publish.sh --help
```

### Example Output

```
============================================================
              🦞 ClawHub Publish Helper                     
============================================================

[INFO] Validating skill: model-switch
[SUCCESS] ✓ SKILL.md exists
[SUCCESS] ✓ scripts/ directory exists
[SUCCESS] ✓ config/ directory exists
[SUCCESS] Skill validation passed

[INFO] Publish attempt #1/5
[SUCCESS] Published: model-switch

============================================================
  ✅ Publish Success!
============================================================
```

---

## ⚙️ Configuration

Edit parameters at script top:

```bash
MAX_ATTEMPTS=5       # Max retry attempts
BASE_WAIT=300        # Base wait time (seconds)
```

---

## 📋 Logs

Publish logs saved at:
`/root/.openclaw/workspace/skills/clawhub-publish/publish-log.md`

---

## 🛠️ Troubleshooting

### Validation Failed

Ensure skill directory contains:
- `SKILL.md` (required)
- `scripts/` directory (recommended)
- `README.md` (recommended)

### Publish Failed

1. Check network connection
2. Verify ClawHub login: `npx clawhub whoami`
3. Check logs: `cat publish-log.md`

### Rate Limited

Script auto-waits and retries. If persistent:
- Wait 10-15 minutes
- Or publish manually: `npx clawhub publish <skill>`

---

## 📄 License

MIT-0

---

**Author:** @williamwg2025  
**Version:** 1.0.0

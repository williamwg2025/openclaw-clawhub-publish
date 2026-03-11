# ClawHub Publish Helper for OpenClaw

一键发布技能到 ClawHub，自动处理限率和错误。

[English Version](README.md)

---

## ✨ 功能特性

- ✅ **验证技能结构** - 检查 SKILL.md, scripts/, config/
- ✅ **必需文件检查** - 自动检测缺失文件
- ✅ **自动重试** - 指数退避处理限率
- ✅ **限率处理** - 自动等待 5 分钟 × 重试次数
- ✅ **发布日志** - 记录到 publish-log.md

---

## 🚀 安装

```bash
cd /root/.openclaw/workspace/skills
git clone https://github.com/williamwg2025/openclaw-clawhub-publish.git clawhub-publish
chmod +x clawhub-publish/publish.sh
```

---

## 📖 使用

### 发布技能

```bash
# 发布技能
cd clawhub-publish
./publish.sh model-switch

# 模拟运行
./publish.sh auto-backup --dry-run

# 查看帮助
./publish.sh --help
```

### 示例输出

```
============================================================
              🦞 ClawHub Publish Helper                     
============================================================

[INFO] 验证技能：model-switch
[SUCCESS] ✓ SKILL.md 存在
[SUCCESS] ✓ scripts/ 目录存在
[SUCCESS] ✓ config/ 目录存在
[SUCCESS] 技能验证通过

[INFO] 发布尝试 #1/5
[SUCCESS] 发布成功：model-switch

============================================================
  ✅ 发布成功！
============================================================
```

---

## ⚙️ 配置

编辑脚本顶部参数：

```bash
MAX_ATTEMPTS=5       # 最大重试次数
BASE_WAIT=300        # 基础等待时间（秒）
```

---

## 📋 日志

发布日志保存在：
`/root/.openclaw/workspace/skills/clawhub-publish/publish-log.md`

---

## 🛠️ 故障排查

### 验证失败

确保技能目录包含：
- `SKILL.md`（必需）
- `scripts/` 目录（推荐）
- `README.md`（推荐）

### 发布失败

1. 检查网络连接
2. 确认 ClawHub 登录：`npx clawhub whoami`
3. 查看日志：`cat publish-log.md`

### 持续限率

脚本会自动重试。如持续限率：
- 等待 10-15 分钟
- 或手动发布：`npx clawhub publish <skill>`

---

## 📄 许可证

MIT-0

---

**作者：** @williamwg2025  
**版本：** 1.0.0

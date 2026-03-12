# ClawHub Publish Helper for OpenClaw

一键发布技能到 ClawHub，自动处理限率和错误。

[English Version](README.md)

---

## ✨ 功能特性

- ✅ **发布前检查** - 自动检查 ClawHub 审查要求（NEW!）
- ✅ **验证技能结构** - 检查 SKILL.md, scripts/, config/
- ✅ **必需文件检查** - 自动检测缺失文件
- ✅ **脚本完整性** - 验证文档中提到的脚本都存在
- ✅ **配置一致性** - 检查配置与代码是否匹配
- ✅ **安全检查** - 路径、外部依赖、安全说明
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

### 发布前检查（推荐）

```bash
# 运行完整检查
python3 scripts/pre-publish-check.py <skill-folder>

# 示例：检查 auto-backup 技能
python3 scripts/pre-publish-check.py ../auto-backup

# 严格模式（警告也视为错误）
python3 scripts/pre-publish-check.py ../auto-backup --strict
```

### 发布技能

```bash
# 发布技能（自动运行发布前检查）
cd clawhub-publish
./publish.sh model-switch

# 模拟运行
./publish.sh auto-backup --dry-run
```

### 单独使用检查工具

```bash
# 检查当前目录
python3 scripts/pre-publish-check.py .

# 检查其他技能
python3 scripts/pre-publish-check.py ~/.openclaw/workspace/skills/auto-backup
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

## 🛠️ 脚本说明

### publish.sh
主发布脚本，自动运行发布前检查并发布到 ClawHub。

### scripts/pre-publish-check.py
发布前自动检查工具，检查 ClawHub 审查要求：
- ✓ 必需文件检查（SKILL.md, scripts/, README.md）
- ✓ SKILL.md frontmatter 验证（name, version, license 等）
- ✓ 脚本文件完整性（文档中提到的脚本都必须存在）
- ✓ 外部依赖检查（git clone 等）
- ✓ 路径安全检查（不使用 /root 硬编码）
- ✓ 配置与代码一致性
- ✓ 安全说明检查

**检查项详解：**

| 检查项 | 说明 | 严重性 |
|--------|------|--------|
| 必需文件 | SKILL.md, README.md 必须存在 | 🔴 错误 |
| Frontmatter | name, displayName, version, description, license, acceptLicenseTerms | 🔴 错误 |
| 脚本完整性 | 文档中提到的脚本文件必须存在 | 🔴 错误 |
| 外部依赖 | 不应要求 git clone 外部仓库 | 🟡 警告 |
| 路径安全 | 使用 ~/ 而非 /root | 🟡 警告 |
| 配置一致性 | 配置文件中声明的功能代码中需实现 | 🟡 警告 |
| 安全说明 | 应包含加密、权限、存储、网络等说明 | 🟡 警告 |

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

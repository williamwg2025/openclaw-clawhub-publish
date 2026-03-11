# ClawHub Publish Helper

一键发布技能到 ClawHub，自动处理限率和错误。

---

## 功能

- ✅ 验证技能结构（SKILL.md, scripts/, config/）
- ✅ 检查必需文件
- ✅ 自动重试（指数退避）
- ✅ 限率检测与处理
- ✅ 发布日志记录

---

## 使用

```bash
# 进入技能目录
cd /root/.openclaw/workspace/skills/clawhub-publish

# 赋予执行权限
chmod +x publish.sh

# 发布技能
./publish.sh model-switch

# 模拟运行（不实际发布）
./publish.sh auto-backup --dry-run

# 查看帮助
./publish.sh --help
```

---

## 示例

### 发布 Model Switch 技能

```bash
./publish.sh model-switch
```

**输出：**
```
============================================================
              🦞 ClawHub Publish Helper                     
============================================================

[INFO] 验证技能结构：/root/.openclaw/workspace/skills/model-switch
[SUCCESS] ✓ SKILL.md 存在
[SUCCESS] ✓ scripts/ 目录存在
[SUCCESS] ✓ README.md 存在
[SUCCESS] 技能结构验证通过

[INFO] 发布尝试 #1/5
[SUCCESS] 发布成功：model-switch

============================================================
  ✅ 发布成功！
============================================================

日志文件：/root/.openclaw/workspace/skills/clawhub-publish/publish-log.md
```

### 处理限率

如果 ClawHub API 限率，脚本会自动：
1. 检测限率错误
2. 等待 5 分钟 × 重试次数
3. 自动重试（最多 5 次）

```
[INFO] 发布尝试 #1/5
[WARNING] 检测到限率错误
[INFO] 等待 300 秒后重试...
[INFO] 发布尝试 #2/5
[SUCCESS] 发布成功：model-switch
```

---

## 配置

编辑脚本顶部的参数：

```bash
MAX_ATTEMPTS=5       # 最大重试次数
BASE_WAIT=300        # 基础等待时间（秒）
```

---

## 日志

发布日志保存在：
`/root/.openclaw/workspace/skills/clawhub-publish/publish-log.md`

日志格式：
```markdown
# ClawHub Publish Log

**Started:** 2026-03-11T09:20:00+08:00

---

## Publish Attempts

### Attempt 1 - 2026-03-11T09:20:00+08:00
**SUCCESS** - Published: model-switch
```

---

## 可用技能

查看当前可用的技能：

```bash
./publish.sh --help
```

或手动查看：
```bash
ls /root/.openclaw/workspace/skills/
```

---

## 故障排查

### 技能验证失败

确保技能目录包含：
- `SKILL.md`（必需）
- `scripts/` 目录（推荐）
- `README.md`（推荐）

### 发布失败

1. 检查网络连接
2. 确认 ClawHub 登录状态：`npx clawhub whoami`
3. 查看详细日志：`cat publish-log.md`

### 持续限率

如果多次重试后仍限率：
- 等待 10-15 分钟后重试
- 或手动发布：`npx clawhub publish <skill>`

---

*最后更新：2026-03-11*

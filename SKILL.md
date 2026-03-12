---
name: clawhub-publish
displayName: ClawHub Publish Helper
version: 1.2.0
description: 一键发布技能到 ClawHub，自动处理限率和错误重试。包含发布前自动检查工具，基于多次审查经验自动检测安全问题（虚假声明、路径风险、API Key 存储等）。
license: MIT-0
acceptLicenseTerms: true
tags: clawhub, publish, deployment, automation, code-quality, security-audit
---

## 功能特性

- ✅ **验证技能结构** - 检查 SKILL.md, scripts/, config/
- ✅ **必需文件检查** - 自动检测缺失文件
- ✅ **自动重试** - 指数退避处理限率
- ✅ **限率处理** - 自动等待 5 分钟 × 重试次数
- ✅ **发布日志** - 记录到 publish-log.md

## 使用

```bash
cd clawhub-publish
./publish.sh model-switch
```

详情见 [README.md](README.md)

---

## 🔒 安全说明

- **本地执行：** 所有脚本在本地运行，不联网
- **权限范围：** 仅需读取 ~/.openclaw/ 目录
- **无外部依赖：** 不克隆外部仓库，所有代码已包含
- **数据安全：** 不上传任何数据到外部服务器

---

**作者：** @williamwg2025  
**版本：** 1.0.1  
**许可证：** MIT-0

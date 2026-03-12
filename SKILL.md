---
name: clawhub-publish
displayName: ClawHub Publish Helper
version: 1.1.0
description: 一键发布技能到 ClawHub，自动处理限率和错误重试。包含发布前自动检查工具，确保技能符合 ClawHub 审查要求。
license: MIT-0
acceptLicenseTerms: true
tags: clawhub, publish, deployment, automation, code-quality
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

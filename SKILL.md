---
name: openclaw-clawhub-publish
displayName: ClawHub Publish Helper - ClawHub 发布工具
version: 1.3.0
description: |
  ClawHub 发布工具 - 一键发布 OpenClaw 技能到 ClawHub。
  自动处理限率和错误重试，内置发布前检查工具。
  新增 SEO 优化器，自动优化技能搜索排名（name/displayName/description/tags）。
  基于 10+ 技能审查经验，自动检测：虚假声明、路径风险、API Key 存储、系统操作声明。
  关键词：openclaw, clawhub, publish, deployment, automation, security-audit, seo
license: MIT-0
acceptLicenseTerms: true
tags:
  - openclaw
  - clawhub
  - publish
  - deployment
  - automation
  - code-quality
  - security-audit
  - pre-publish-check
  - ci-cd
  - seo-optimizer
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

### 文件写入 ⚠️
**本技能会写入文件：**
- **发布日志：** `publish-log.md` - 发布记录
- **配置文件：** 可选，存储技能配置

**读取：**
- SKILL.md, README.md - 技能文档
- scripts/ - 脚本文件
- config/ - 配置文件（可选）

### 网络访问 ⚠️
**本技能需要联网：**
- 发布技能到 ClawHub Registry
- 验证技能结构
- 处理 API 限率

**网络权限：**
- 出站 HTTPS 请求（ClawHub API）
- 不监听端口
- 不运行服务器

### 系统操作
- **无：** 不执行系统命令，不重启服务

### API Key
- **不需要：** 使用 ClawHub 登录 token
- **存储：** token 存储在 ClawHub CLI 配置

### 数据安全
- **本地处理：** 所有检查在本地执行
- **发布数据：** 仅发布技能文件到 ClawHub
- **不上传：** 不上传无关数据

---

**作者：** @williamwg2025  
**版本：** 1.0.1  
**许可证：** MIT-0

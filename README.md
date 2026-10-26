# 小林大模型面试题阅读站

原作者：公众号@小林面试笔记。原网站：https://xiaolinnote.com/ai/

阅读网址：https://picof.github.io/xiaolin-ai-interview-offline/

阅读快照包含 138 个 HTML 页面、819 个图片文件。保留教程正文、代码、表格、图示、署名和水印。`site/` 是可独立打开的静态站点，GitHub Actions 负责验证并部署到 GitHub Pages。

## 本地浏览与验证

直接打开 `site/index.html`，或从仓库根目录执行：

```sh
python -m http.server 8000 --directory site
python scripts/build.py --check-only
```

Python 3.10 及以上版本即可，无第三方依赖。`python scripts/build.py` 先验证所有本地引用、锚点、页面和图片数量，再复制到 `_site/`。

## GitHub Actions 与 Pages

工作流位于 `.github/workflows/pages.yml`。推送 `main` 或在 Actions 中手动运行，执行链接、锚点与体积验证。本站已设置 `PAGES_ENABLED=true`，验证通过后会上传 Pages 工件并部署。

确认 Pages 可用后，在 **Settings → Secrets and variables → Actions → Variables** 添加仓库变量 `PAGES_ENABLED=true`，工作流才会上传一天后过期的 Pages 工件并部署。未设置此变量时，部署任务会明确显示为跳过。

在仓库 **Settings → Pages → Build and deployment → Source** 中选择 **GitHub Actions**。必须先确认账号套餐支持当前仓库可见性的 GitHub Pages：私人仓库要求 GitHub Pro、Team 或 Enterprise；GitHub Free 的私人仓库无法启用 Pages。源仓库设为私人并不代表 Pages 网址也私人，默认 Pages 阅读网址公开可访问。

本仓库经用户授权设为公开，使用公开仓库的 GitHub Actions 与 GitHub Pages。

## 文件及原图说明

在线阅读版只包含 HTML、CSS、JavaScript、图片和阅读说明。离线 ZIP、原始 HTML 备份和完整 JSON 清单不进入站点。

540 个原名为 `.bin` 的图片按其真实格式改为 `.png`、`.webp` 或 `.bmp`，便于服务器返回正确的 MIME 类型。819 个图片内容逐字节与离线版一致，没有压缩、裁切或重绘。

站点约 997.5 MiB。官方 `actions/deploy-pages` 的 1 GB 阈值为 1,073,741,824 字节；构建脚本检查内容及 TAR 包大小，超过阈值即停止。不要向 `site/` 添加 PDF、ZIP 或完整备份。

参考文档：

- https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://docs.github.com/en/billing/concepts/product-billing/github-actions
- https://github.com/actions/deploy-pages/blob/main/src/internal/deployment.js

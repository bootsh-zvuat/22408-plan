# 22408 每日计划 · 部署说明

这是一个纯静态页面，`index.html` 自带全部计划数据与逻辑，不依赖接口、不需要构建。

## 一、GitHub Pages（推荐给"手机随时看"）

1. 新建仓库（Public），例如 `22408-plan`。
2. 把本目录的 `index.html` 推到仓库根目录：
   ```bash
   cd deploy
   git init -b main
   git add index.html
   git commit -m "add 22408 daily plan"
   git remote add origin https://github.com/<你的用户名>/22408-plan.git
   git push -u origin main
   ```
3. 仓库 Settings → Pages → Source 选 `Deploy from a branch`，分支 `main` / 目录 `/ (root)`，保存。
4. 约 1 分钟后访问 `https://<你的用户名>.github.io/22408-plan/`。

## 二、其他更快的静态托管

- **Netlify Drop**：打开 https://app.netlify.com/drop，把 `index.html` 拖进去，立刻得到网址。
- **Cloudflare Pages**：Create project → Direct Upload → 上传 `index.html`。
- **Vercel**：`npx vercel deploy --prod`（需登录）。

## 三、本机使用

双击 `index.html` 即可，数据存在当前浏览器的 localStorage。

## 四、数据更新

计划内容写在 `../math2-2028.json` 与 `../cs408-2028.json`，改完在上一级目录执行：

```bash
python3 build_v2.py
cp 22408每日计划.html deploy/index.html
```

再推一次仓库即可。

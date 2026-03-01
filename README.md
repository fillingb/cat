# 猫咪品相评估 H5 应用

极简风格的手机网页应用：上传猫咪照片，选择品种，由 AI（Gemini 1.5 Flash）评估品相并给出等级与价格区间。

## 技术栈

- **后端**: Python FastAPI + Google Gemini 1.5 Flash
- **前端**: Vite + Vue 3 + Tailwind CSS（H5 适配、暖色极简 UI）

## 项目结构

```
d:\cat\
├── main.py              # FastAPI 后端，图片上传与 Gemini 调用
├── requirements.txt     # Python 依赖
├── package.json         # 前端依赖
├── vite.config.js       # Vite 配置（代理 /api 到后端）
├── index.html
├── src/
│   ├── main.js
│   ├── App.vue          # 首页、品种选择、拍照/上传、结果页
│   ├── index.css        # Tailwind 入口
│   └── utils/
│       └── compress.js  # 前端图片压缩
└── README.md
```

## 本地运行

### 1. 后端

```bash
cd d:\cat
pip install -r requirements.txt
# 设置 API Key（二选一）
# set GEMINI_API_KEY=你的密钥
# 或直接修改 main.py 中的 API_KEY
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端

```bash
cd d:\cat
npm install
npm run dev
```

浏览器访问：http://localhost:5173（手机可连同一 WiFi 用电脑 IP:5173 访问）。

### 3. API Key

- 在 [Google AI Studio](https://aistudio.google.com/apikey) 申请 Gemini API Key。
- 在 `main.py` 中把 `YOUR_GEMINI_API_KEY_HERE` 替换为你的 Key，或设置环境变量 `GEMINI_API_KEY`。
- 未配置时接口会返回模拟数据，便于前端联调。

## 功能说明

- **首页**：品种下拉（布偶猫、英国短毛猫、美国短毛猫、其他）+「拍照上传」「相册选择」。
- **上传前**：前端对图片压缩（最长边 1200px、质量 0.82），减轻上传与接口压力。
- **评估**：后端接收图片与品种，调用 Gemini 按头部、五官、毛色打分，并返回等级（宠物级/繁育级/赛级）与价格区间。
- **结果页**：卡片展示等级、价格、三项分数（进度条）与评语，支持「再评估一只」。

## 生产部署

- 前端：`npm run build`，将 `dist` 部署到静态站点或 Nginx。
- 后端：用 `uvicorn main:app --host 0.0.0.0 --port 8000` 或 Gunicorn 等部署。
- 若前后端不同域，在前端项目根目录建 `.env.production`，设置 `VITE_API_BASE=你的后端地址`，并确保后端开启 CORS（当前已允许 `*`，生产可收紧为前端域名）。

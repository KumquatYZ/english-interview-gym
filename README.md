<p align="center">
  <img src="docs/icon.png" width="110" alt="English Interview Gym — logo">
</p>

<h1 align="center">English Interview Gym<br>英语面试健身房</h1>

<p align="center">
  <b>每天 20 分钟，和 AI 面试官开口对练，把"日常英语"练成"面试流利"。</b><br>
  <b>语音模拟面试 · 实时提示 · 点词速查 · 即时纠错 · 复盘打卡 —— 本地运行，数据不出你的电脑。</b>
</p>

<p align="left">
  <a href="README_en.md"><b>English</b></a> | <a href="README.md"><b>中文</b></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License MIT">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg" alt="Python 3.12">
  <img src="https://img.shields.io/badge/BYOK-bring%20your%20own%20API%20key-orange.svg" alt="BYOK">
  <img src="https://img.shields.io/badge/Data-100%25%20local-brightgreen.svg" alt="Local data">
</p>

<p align="center">
  <img src="docs/overview.png" width="1100" alt="功能总览：模拟面试 · 实时提示 · 点词速查 · 复盘报告 · 打卡进度">
</p>

## 目录

- [这是什么](#这是什么)
- [快速开始](#快速开始)
- [在手机上使用（可选）](#在手机上使用可选)
- [模型需求与推荐](#模型需求与推荐)
- [功能详解](#功能详解)
  - [模拟面试](#模拟面试)
  - [示范答案与实时提示](#示范答案与实时提示)
  - [点词速查](#点词速查)
  - [即时反馈与评分](#即时反馈与评分)
  - [复盘报告与错题本](#复盘报告与错题本)
  - [打卡与进度](#打卡与进度)
  - [收藏夹与每日复习](#收藏夹与每日复习)
  - [题目卡片墙](#题目卡片墙)
  - [简历导入](#简历导入)
- [配置手册](#配置手册)
- [自定义与扩展](#自定义与扩展)
- [目录结构](#目录结构)
- [隐私说明](#隐私说明)
- [内容来源与免责声明](#内容来源与免责声明)
- [常见问题](#常见问题)
- [开源协议](#开源协议)

## 这是什么

一个跑在你电脑上的英语面试训练器。核心循环只有一件事——**开口说**：

> AI 面试官语音提问 → 你开口回答（自动转写）→ 即时纠错、评分、教你更好的说法 → 追问或下一题

每次练习自动计入打卡与趋势统计；每道题都能回看历史、重练、看到进步曲线。它针对三类常见困境：

- **没人陪练**——3 种 AI 面试官人格 × 82 道高频题（HR 初面 / 技术面 / 压力面），随时开始，永不嫌你烦；
- **不知道怎么说**——每题附带 30–45 秒示范答案（「🧩 通用版」开箱即用；导入简历解锁「🎯 定制版」），全站单词点击即查，卡壳时还有「照读示范」模式兜底；
- **练完没反馈**——每轮纠错 / 升级 / 改写三张卡片 + 1–10 分；整场结束生成五维复盘报告与错题本。

| 功能 | 能干嘛 | 入口 |
|---|---|---|
| 🎙️ 模拟面试 | 4 种角色 × 5 套题库，语音问答、自然追问 | 首页「选择你的 AI 导师」 |
| 💼 会议练习 | 会议主持人角色（Olivia）+ 原创会议题库：外企会议通用 / 美妆行业 | 首页选题集（💼 / 💄） |
| 💡 示范答案 | 每题 30–45 秒示范：通用版 / 定制版 | 对话页「📖 示范答案」 |
| 🔍 点词速查 | 音标 · 语境释义 · 例句 · 发音 · 收藏 | 全站任意单词 |
| ✍️ 即时反馈 | Correction / Upgrade / Revision + 1–10 分 | 每轮回答后自动出现 |
| 📋 复盘报告 | 五维评分 + 下次重点 + 错题本 | 右上角「复盘」 |
| 🔥 打卡与进度 | 连续天数 · 每日目标圆环 · 复习进度 · 14 天日历 | 首页打卡面板 |
| ⭐ 收藏夹 · 每日复习 | 词库分页管理（排序 / 删除）+ 按比例随机温故 | 首页「⭐ 收藏夹」 |
| 🗂 题目卡片墙 | 120 题卡片：状态 / 最高分 / 趋势 / 单题历史 | 首页「选择题集」 |
| 📄 简历导入 | 解锁基于你真实经历的定制版答案 | 「📄 我的简历」 |

## 快速开始

> 📖 **界面使用手册**（21 页，含全部界面截图，边看边练）：[DOCX 下载](docs/USER-GUIDE.docx) · [PDF 下载](docs/USER-GUIDE.pdf)

两条路，选一条就行：**方式一（推荐，零安装）** 下载免安装包，双击就能用；**方式二** 从源码运行（macOS / 想自己改代码的人）。

### 方式一（推荐，零安装）：免安装包

**第 1 步 · 下载** —— 到 [**Releases 页面**](https://github.com/KumquatYZ/english-interview-gym/releases) 下载对应平台**最新版**的包（压缩包文件名带版本号，认准最新）：

| 平台 | 文件 | 怎么打开 |
|---|---|---|
| **Windows 10 / 11** | [`EnglishInterviewGym-v0.16.2-win64.zip`](https://github.com/KumquatYZ/english-interview-gym/releases/download/v0.16.2/EnglishInterviewGym-v0.16.2-win64.zip) | 解压 → 双击 `EnglishInterviewGym.exe` → 打开「英语面试健身房」**独立应用窗口**（无命令行黑框） |
| **macOS（Apple 芯片）** | [`EnglishInterviewGym-v0.16.2-macos.zip`](https://github.com/KumquatYZ/english-interview-gym/releases/download/v0.16.2/EnglishInterviewGym-v0.16.2-macos.zip) | 解压 → 双击「启动.command」（首次被系统拦截：右键 →「打开」） |

> 📦 每个压缩包的**文件名都带版本号**（如 `…-v0.16.2-win64.zip`），一眼就能辨别新旧；全部历史版本都在 [Releases 页](https://github.com/KumquatYZ/english-interview-gym/releases)。

都是一次性绿色便携版：不装 Python、不碰命令行；**所有内容（程序、API Key、练习记录、日志、缓存）都存在程序文件夹内**——删掉文件夹 = 完全卸载，不会向 C 盘用户目录写入任何数据。

> macOS 解压提示：推荐用系统自带方式解压（访达里直接双击 zip）。启动请**双击「启动.command」**（会自动去除系统隔离标记）。如果弹出 **“已损坏，应移到废纸篓”** 一类对话框：**请点【取消】，不要点“移到废纸篓”**——那是 macOS 对未签名应用的拦截提示，点“移到废纸篓”会删掉程序文件（删了也没关系，重新解压即可）。v0.15.11 起安装包已做全面兼容，正常使用不会再遇到该弹窗。

**第 2 步 · 配置**（首次必做，约 3 分钟）

打开界面 → 右上角「**⚙️ 设置**」→ 填两组：

| 区域 | 填什么 | 说明 |
|---|---|---|
| 💬 对话服务 | 接口地址 + API Key + 模型 | 任何 OpenAI 兼容服务均可（例：DeepSeek 官方 `https://api.deepseek.com` + `deepseek-chat`） |
| 🎙️ 语音服务 | 识别 / 合成的接口地址 + 模型（+ 可选语音 Key） | Windows **必填**（没有本地兜底，不填录音后无法转写）；填法照抄 [语音服务单独买（推荐搭配）](#语音服务单独买推荐搭配) 里的表格 |

> 💡 对话与语音可以来自**不同服务商**：比如对话用 DeepSeek 官方（便宜，但没有语音模型），语音单独买 TokenHub / MiniMax / 硅基流动 / OpenAI —— 语音 Key 留空 = 自动复用对话 Key。各家「端点 + 模型 + 音色」的现成填法见 [语音服务单独买（推荐搭配）](#语音服务单独买推荐搭配)。

**第 3 步 · 第一次练习（约 10 分钟）**

1. 首页「选择你的 AI 导师」→ 点导师**试听音色**，选定人格（练开会英语选 Olivia）；
2. 「选择题集」→ 先进 `baseline-8`（8 题热身）；练会议选「外企会议通用 16 题」或「美妆行业会议 22 题」；
3. 点任意题卡 → 「🎙 从这题开练」→ 点麦克风（或按空格）开口；
4. 说完再点一次麦克风 → 看转写、反馈卡与评分 → 继续下一题；
5. 练完点右上角「复盘」生成整场报告。

### 更新与卸载（免安装包）

**更新到新版本**：
1. 下载新压缩包（文件名带版本号，认准最新）；
2. 推荐解压到**新文件夹**使用；也可直接覆盖旧文件夹后再启动——**v0.16.1 起会自动补齐新增题库 / 角色**（不覆盖你已有的文件和自定义）；
3. 想保留练习记录与 API Key：把旧文件夹里的 `data/`、`.env`、`config.local.yaml` 复制进新文件夹即可（不复制 = 全新开始）。

**彻底卸载（Windows / macOS 通用）**：绿色免安装版——程序、API Key、练习数据、日志、浏览器缓存**全部都在程序文件夹内**（Windows 版连 WebView 缓存也写在文件夹里的 `webview_data/`）。**删除该文件夹 = 完全卸载**，不会向 C 盘用户目录（如 AppData）写入任何数据。删除前想保留记录可先备份 `data/`；创建过桌面快捷方式的话一并删除即可。

**确认当前版本**：界面 → 「⚙️ 设置」右下角显示版本号（如 `版本 0.16.2`）。

### 方式二（可选）：从源码运行（macOS / 开发者）

**环境要求**：macOS（Apple Silicon 体验最佳）+ Python 3.12 + `ffmpeg`（`brew install ffmpeg`）+ 一个 API Key（自备，任何 OpenAI 兼容服务均可）。

```bash
git clone https://github.com/KumquatYZ/english-interview-gym.git
cd english-interview-gym
python3 -m venv .venv            # 装了 uv 也可以：uv venv .venv --python 3.12
.venv/bin/pip install -r app/requirements.txt

cp app/.env.example app/.env     # 填入 API_KEY=你的key、API_BASE_URL=你的服务地址
                                 # 对话 Key 必填；语音 Key 可选（SPEECH_API_KEY，不填则复用对话 Key）
                                 # 或运行交互式配置助手：python3 scripts/setup_env.py

bash scripts/run_server.sh       # 或直接双击「打开训练系统.command」
```

打开 http://127.0.0.1:8765（首次使用请允许浏览器访问麦克风）。

**其它脚本（可选）**：

```bash
.venv/bin/python scripts/check_stack.py       # 逐链路体检：对话 / 语音识别 / 语音合成
.venv/bin/python scripts/baseline_report.py   # 练习周报
```

## 在手机上使用（可选）

**最简方式（推荐）**：打开「**⚙️ 设置 → 📱 手机访问 → 启用**」——自动生成证书并开启 HTTPS 通道，界面会给出手机访问地址与完整的安装指引（Mac / Windows 免安装版同样适用）。

想让 iPhone **在任何网络下**都能连回（而不是仅同一 Wi-Fi），建议 Mac 与 iPhone 同时安装 [Tailscale](https://tailscale.com/download)（免费、私有组网，登录同一账号即可）——检测到 Tailscale 时，手机访问会自动使用它，且只在你的私有网络内可达。

**手机首次设置（一次性）**：

- 安装证书：用 Safari 打开「设置」里显示的地址（提示"证书无效" → 继续访问）→ 再打开 `该地址/ca.crt` 下载描述文件 → 「设置 → 通用 → VPN与设备管理」安装 → 「通用 → 关于本机 → 证书信任设置」开启完全信任；
- Safari 打开同一地址 → 「分享 → **添加到主屏幕**」——之后从主屏图标进入即全屏独立窗口，与 App 体验一致。

> 说明：手机是"瘦客户端"——会话与数据仍保存在运行本应用的电脑上（保持开机联网即可）。命令行用户也可用 `bash scripts/gen_https_cert.sh` + `scripts/https_proxy.py` 流程（与界面内一键启用等价）。

## 模型需求与推荐

本应用**一次完整练习会用到三类模型**——不只是聊天模型。三类模型**可以分开配置**：对话与语音（识别/合成）支持使用**不同服务商、不同 Key**（例如对话用 DeepSeek 官方、语音单独买一家语音服务），见下方 [语音服务单独买（推荐搭配）](#语音服务单独买推荐搭配)。常用搭配示例：

| 用途 | 用在哪里 | 推荐模型（示例） | 参考价（人民币，按量后付费） |
|---|---|---|---|
| 💬 对话模型 | 提问追问、示范答案、纠错评分、复盘报告、点词释义 | **DeepSeek-V4.1-Flash**（`deepseek/deepseek-flash`，默认）；备选 **GLM-5.3-Flash**（`glm-5.3-flash`） | DeepSeek：¥1–2 输入 / ¥4–8 输出；GLM：¥0.8 / ¥2.8（每百万 tokens，闲时/高峰） |
| 🎙️ 语音识别 ASR | 把你的口述回答转成文字 | **Hy-ASR-3.0-Preview**（`hy-asr-3.0-preview`，默认）；备选 `wand-asr-v1` | Hy-ASR：¥0.00022/秒（约 ¥0.79/小时）；WAND：¥0.0005/秒 |
| 🔊 语音合成 TTS | 面试官提问的语音 | **MiniMax-Speech-2.8-Turbo**（`minimax-speech-2.8-turbo`，默认，内置 4 种英文音色）；`-hd` 音质更好 | Turbo：¥2/万字符；HD：¥3.5/万字符 |

**成本估算（20 分钟/天，全部走云端）**：对话 ≈ ¥0.1/天 + 识别 ≈ ¥0.26/天 + 合成 ≈ ¥0.2–0.4/天 ≈ **合计 ¥0.6–0.8/天，约 ¥20/月**（按量后付费；实际以服务商账单为准；晚间练习多落在闲时计费时段，单价更低）。

**两条语音链路可以零成本本地化（macOS）**：

- `asr.driver: local` —— mlx-whisper 本机识别（Apple Silicon，免费）；
- `tts.driver: macos_say` —— macOS 内置 `say` 朗读（免费，音色偏机械）。

两者同时启用后，训练成本只剩对话模型 **≈ ¥0.1/天**。

**注意事项**：

- 语音调用若报 `402 / 401007`：多为服务商侧未开通相关能力（常见为需开启"后付费"），按其控制台提示处理一次即可；
- 计价规则以服务商为准（DeepSeek 系列常见为工作日 9:00–12:00、14:00–18:00 高峰时段 ×2 价，其余时段及周末闲时）；
- 默认 fallback 链含 `kimi-k3`（单价较高，仅主模型失败时触发），在意成本可自行调整 `llm.fallback_models`。

换模型：改 `app/config.yaml` 的 `llm.model` / `asr.model` / `tts.cloud_model` 即可（均支持 fallback 链）。

### 语音服务单独买（推荐搭配）

**为什么**：很多聊天服务商（比如 DeepSeek 官方）**没有语音模型**，而语音（识别/合成）是本应用的核心。所以软件把「对话」和「语音」做成两套独立配置——对话用一家、语音用另一家，互不影响：

- **对话服务**：API Key + Base URL + 模型（如 DeepSeek 官方）；
- **语音服务**：单独的端点 + 模型 +（可选）语音专用 Key。**语音 Key 留空时自动复用对话 Key**——同一家服务商（比如都用 TokenHub）则无需重复填。

配置入口：界面「⚙️ 设置 → 🎙️ 语音服务」，或 `app/.env`（`SPEECH_API_KEY`）+ `app/config.yaml`（`asr.*` / `tts.*`）。
**端点协议按地址自动识别**：含 `/audio/transcriptions`、`/audio/speech` 的走 OpenAI 兼容协议；其余按 TokenHub / MiniMax 系协议。

**常见语音服务（均可直接接入，自备账号）：**

| 服务 | 识别 ASR | 合成 TTS | 入口 |
|---|---|---|---|
| 腾讯云 TokenHub | ✅ `hy-asr-3.0-preview` | ✅ MiniMax 系（`minimax-speech-2.8-turbo`） | https://console.cloud.tencent.com/tokenhub |
| MiniMax 开放平台 | – | ✅ `speech-2.8-turbo` / `-hd`（英文音色口碑好） | https://platform.minimaxi.com |
| 硅基流动 SiliconFlow | ✅ `FunAudioLLM/SenseVoiceSmall` 等（有免费模型） | ✅ `FunAudioLLM/CosyVoice2-0.5B` / fish-speech 等 | https://siliconflow.cn |
| OpenAI | ✅ `whisper-1` / `gpt-4o-transcribe` | ✅ `gpt-4o-mini-tts` | https://platform.openai.com |
| 阿里云百炼 / 火山引擎 / 讯飞 | ✅ | ✅ | 各家控制台（选 OpenAI 兼容模式） |

**填法示例**（三行分别是：识别接口地址 + 识别模型；合成接口地址 + 合成模型 + 音色）：

| 服务 | 识别（接口地址 / 模型） | 合成（接口地址 / 模型 / 音色） |
|---|---|---|
| TokenHub | `https://tokenhub.tencentmaas.com/v1/wand/asrproxy/sync_transcribe` / `hy-asr-3.0-preview` | `https://tokenhub.tencentmaas.com/v1/wand/minimax-tts/sync_tts` / `minimax-speech-2.8-turbo` / `English_Graceful_Lady` |
| MiniMax 官方 | —（官方暂无 ASR） | `https://api.minimaxi.com/v1/t2a_v2` / `speech-2.8-turbo` / `English_Graceful_Lady` |
| 硅基流动 | `https://api.siliconflow.cn/v1/audio/transcriptions` / `FunAudioLLM/SenseVoiceSmall` | `https://api.siliconflow.cn/v1/audio/speech` / `FunAudioLLM/CosyVoice2-0.5B` / `FunAudioLLM/CosyVoice2-0.5B:alex` |
| OpenAI | `https://api.openai.com/v1/audio/transcriptions` / `whisper-1` | `https://api.openai.com/v1/audio/speech` / `gpt-4o-mini-tts` / `alloy` |

> **音色 ID 随服务商而异**：TokenHub / MiniMax 用 `English_Graceful_Lady`、`English_Trustworth_Man`、`English_ManWithDeepVoice` 等；OpenAI 用 `alloy`、`nova` 等。
> 语音服务可与对话不同家：在「语音服务 Key」里填语音那家的 Key 即可（留空则复用对话 Key）。
> TokenHub 语音若报 `402 / 401007`：到控制台开通一次"后付费"；各家价格以官网为准。

## 功能详解

### 模拟面试

**能干嘛**：和面试官"你一句我一句"地真实对话——面试官语音提问，你开口回答，自动转写成文字，然后是追问或下一题。

- 4 种角色（`materials/personas/`）：`hr-friendly` 外企 HR 初面（行为面）、`tech-lead` 技术主管面（研究深挖）、`stress` 压力面（终面）、`meeting-host` 会议主持人（跨部门会议）；每个角色都写明了定位、评估维度与追问策略，并内置一段真实对话 few-shot——也可以照格式换成你自己的目标岗位；
- 5 套题库：`baseline-8`（8 题热身）、`interview-core`（14 题核心）、`mnc-60`（60 题大厂高频）、`meetings-core`（外企会议通用 16 题）、`cosmetics-meetings`（美妆行业会议 22 题，行业话题取材于公开报道、题目原创）。

**怎么用**：首页选人格 → 选题集 → 点题卡「🎙 从这题开练」→ 点麦克风（或按空格）→ 答完再点一次 → 看反馈 → 下一题。对话页顶部可选「自己说 / 照读示范」两种模式；中途「跳过这题」；随时「复盘」结束整场。

**怎么配置**：
- 单题回答时长上限：`app/config.yaml` → `session.max_answer_seconds`（默认 120 秒）；
- 换音色：`app/config.yaml` → `tts.voices`（每个人格一个音色）；
- 加自己的题 / 题库：见[自定义与扩展](#自定义与扩展)。

### 示范答案与实时提示

**能干嘛**：任何一题都可以先看"这题可以怎么说"——一份 30–45 秒（约 60–100 词）、**对标真实企业面试标准**的示范答案（结论先行、证据与数字、去客套与学生腔）：

- 「🧩 通用版」：开箱即用，含 `[方括号]` 占位符，替换成自己的信息即可；
- 「🎯 定制版」：导入简历后解锁，用你真实经历和数字组织答案（见[简历导入](#简历导入)）。

**怎么用**：对话页点「📖 示范答案」→ 在「🧩 通用版 / 🎯 定制版」标签间切换 → 想跟读时点「🎧 照读这段」进入照读模式。

**怎么配置**：无需配置；定制版取决于是否导入简历。

### 点词速查

**能干嘛**：对话、示范答案、反馈卡片、复盘报告里的**任意英文单词**点一下，弹出音标、词性、**结合当前语境**的释义、例句与发音；一键「⭐ 收藏生词」。同一个词在不同语境会给出不同解释。

**怎么用**：单击单词 → 看释义卡 → 🔊 听发音 → ⭐ 收藏。收藏的词进入「⭐ 收藏夹」，可每日复习、可管理。

**怎么配置**：无需配置；查询结果缓存在 `data/gloss_cache.json`，重复查询秒回。

### 即时反馈与评分

**能干嘛**：每次回答后自动给出三张卡片——

- **Correction** 纠错：语法 / 用词 / 时态；
- **Upgrade** 升级：口语表达 → 面试官期待的地道表达；
- **Revision** 改写：润色后的完整回答，可直接跟读。

外加 1–10 综合分。用「照读示范」模式回答时，还会给出**照读准确率**（漏读 / 添词逐词对照）。

**怎么用**：答完自动出现，不必操作；卡片里的单词同样可以点词速查、⭐ 收藏。

**怎么配置**：无需配置。

### 复盘报告与错题本

**能干嘛**：结束一场后生成「本场复盘」：内容 / 结构 / 语法 / 词汇 / 流利度五个维度评分 + 下次重点建议 + 练习清单；反复出现的错误自动汇入错题本，方便专项复练。

**怎么用**：右上角「复盘」→ 10–20 秒生成报告（同时存入 `data/reports/`）。

**怎么配置**：无需配置。

### 打卡与进度

**能干嘛**：把"开口量"像健身一样记录：连续打卡天数、每日目标圆环（默认 20 分钟）、最近 14 天分钟数日历、统计卡片；连续 3 / 7 / 14 / 30 / 50 / 100 天有庆祝动画。

**怎么用**：首页打卡面板自动更新；练完即计入今天。

**怎么配置**：每日目标改 `app/config.yaml` → `session.daily_goal_minutes`（默认 20）。

### 收藏夹与每日复习

**能干嘛**：收藏的生词以**词典式词库**管理——每页 8 条、翻页浏览、可切换「最新 / A–Z」排序、两步确认删除；「🔁 今日复习」每天按预设比例从收藏词中随机抽一批，**优先**从未复习、上次没记住、久未复习的词：先回忆 → 看释义 → 标记「😵 没记住 / 😎 记住了」，没记住的词当轮再巩固一遍，并优先出现在第二天的复习里。完成情况同步到打卡面板的「今日复习 x/y 词」。

**怎么用**：首页「⭐ 收藏夹」→「📚 词库」翻页浏览 / 排序 / 删除 / 点单词查释义；「🔁 今日复习」→ 开始复习 → 回忆 → 显示释义 → 标记结果。

**怎么配置**：`app/config.yaml` → `review.ratio`（每天复习比例，默认 0.3）、`review.min_per_day`（默认 5）、`review.max_per_day`（默认 30）。

### 题目卡片墙

**能干嘛**：每个题集以卡片墙展开：配图 + 中文短标题 + 练习状态 + 最高分。点开卡片看**单题历史**——每次作答的日期、模式（自由说 / 照读）、时长、语速（WPM）、得分，以及一条分数趋势线；也可以直接从这题重练。

**怎么用**：首页「选择题集」→ 卡片墙；底部「▶ 继续练习」自动跳到第一道未练的题（练完一轮变为「▶ 再练一遍」）。

**怎么配置**：题目配图放在 `materials/question-bank/images/<题集>/<题号>.png`，题卡墙自动显示（内置题集已附带配图）。

### 简历导入

**能干嘛**：上传简历（`.docx` / `.pdf` / 直接粘贴文本），示范答案解锁「🎯 定制版」——用你的真实经历、项目与数字组织答案。简历只保存在本机。

**怎么用**：右上角「📄 我的简历」→ 选择文件或粘贴文字 → 保存；随时可删除（删除后退回仅有通用版）。

**怎么配置**：也可以手动编辑 `materials/profile.md`（格式参考 `materials/profile.example.md`）。

## 配置手册

### 环境变量（`app/.env`）

| 变量 | 必填 | 用途 |
|---|---|---|
| `API_KEY` | ✅ | 对话服务 Key（聊天模型） |
| `API_BASE_URL` | – | 对话服务接口地址（指向你的 OpenAI 兼容服务） |
| `SPEECH_API_KEY` | – | 语音服务专用 Key（可与对话不同服务商；留空 = 复用 `API_KEY`） |

### 应用配置（`app/config.yaml`）

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `llm.base_url` | 留空 | 你的 OpenAI 兼容接口地址（也可用 `API_BASE_URL`） |
| `llm.model` | `deepseek/deepseek-flash` | 主对话模型 |
| `llm.fallback_models` | 见文件 | 主模型失败时的备选链 |
| `asr.driver` | `auto` | `auto` / `cloud`（云端识别）/ `local`（mlx-whisper，仅 macOS） |
| `asr.endpoint` / `tts.endpoint` | 留空 | 云端语音接口地址；留空自动使用本地模式 |
| `tts.driver` | `cloud` | `cloud` / `macos_say`（离线兜底） |
| `tts.voices` | 见文件 | 每个人格一个音色 |
| `review.ratio` | `0.3` | 每天复习词数比例（= 收藏单词总量 × 该比例） |
| `review.min_per_day` / `review.max_per_day` | `5` / `30` | 每日复习词数下限 / 上限 |
| `session.daily_goal_minutes` | `20` | 每日目标（分钟），影响打卡圆环 |
| `session.max_answer_seconds` | `120` | 单题回答时长上限 |
| `server.port` | `8765` | 服务端口 |
| `tools.ffmpeg` | `ffmpeg` | ffmpeg 可执行文件路径 |

### 运行数据（`data/`，全部仅本地）

| 路径 | 内容 |
|---|---|
| `data/sessions/*.jsonl` | 每场训练的逐轮记录（含评分） |
| `data/reports/` | 复盘报告 |
| `data/errorbook.jsonl` | 错题本 |
| `data/favorites.jsonl` | 收藏的生词与句子 |
| `data/reviews.jsonl` | 单词复习记录（每日温故作答） |
| `data/review_decks.json` | 每日复习计划缓存（按天固定） |
| `data/gloss_cache.json` | 点词速查缓存 |
| `data/audio/` | 录音文件 |

## 自定义与扩展

- **题目 / 题库**——普通 YAML，直接改或新增 `materials/question-bank/` 下的文件：

  ```yaml
  key: my-bank
  title: 我的题库
  questions:
    - id: q1
      round: HR 初面
      category: 开场
      text: "Tell me about yourself."
      intent: 考察意图
      hint: 答题思路
      followups:
        - "What's the one thing you want me to remember?"
  ```

- **题目配图**——PNG 放进 `materials/question-bank/images/<题库key>/<题号>.png`，题卡墙自动显示；
- **面试官人格**——`materials/personas/*.md`，在 `### system` 块里定义角色与提问风格（内置三人格已含定位、评估维度与真实面试对话 few-shot，按格式改即可）；
- **故事库**——复制 `materials/stories/template.md`，攒 5–8 个打磨过的个人故事，面试答案更扎实。

## 目录结构

```text
english-interview-gym/
├── 打开训练系统.command          # macOS 双击一键启动
├── app/
│   ├── config.yaml              # 应用配置（模型 / 语音 / 打卡目标）
│   ├── .env.example             # 环境变量模板（复制为 .env 后填 Key）
│   ├── requirements.txt
│   ├── server/                  # FastAPI 后端：会话 · 模型调用 · 语音识别 · 语音合成 · 报告
│   └── web/                     # 单页前端（无框架构建，开箱即用）
├── materials/
│   ├── personas/                # 3 种面试官人格
│   ├── question-bank/           # 3 套题库（YAML）+ 配图 + 元信息
│   ├── stories/                 # 个人故事库（模板 + 说明）
│   ├── wordlist/                # 生词表
│   └── profile.example.md       # 简历模板（复制为 profile.md 手写）
├── scripts/                     # setup_env · run_server · check_stack · baseline_report
├── data/                        # 运行数据（仅本地，gitignore）
└── docs/                        # RUNBOOK 运行手册 · PRACTICE-PLAN 练习计划 · 图片资源
```

## 隐私说明

- **100% 本地运行**：服务只监听 `127.0.0.1`，训练数据（录音 / 转写 / 报告 / 生词）全部保存在本机 `data/`，不会上传到任何第三方；
- **最小化外发**：回答的音频与文本只发送到**你自己配置的** API 接口（用于转写与反馈），密钥只存在本机 `app/.env`；
- **无遥测**：没有统计上报、没有账号体系；
- **公开仓库零个人信息**：`app/.env`、`materials/profile.md`、`data/` 均被 .gitignore 忽略，不随仓库分发。

## 内容来源与免责声明

- **来源**：题库题目（`materials/question-bank/`）整理自**互联网公开渠道**（社区面经、公开面试题汇总、公开招聘信息与岗位要求等），收录时已做通用化改写；每题的考察意图与答题提示为本项目自行撰写；
- **不主张权利**：本项目不对题目原始出处主张任何权利，也不保证与任何具体公司、机构的实际面试题库对应；
- **使用范围**：题库等文字内容仅供**个人学习交流**，请勿用于商业用途；代码部分以 MIT 协议开源；
- **侵权处理**：如任何权利人认为仓库内容（题目、配图等）侵犯了您的权益，请通过 [Issues](../../issues) 联系，我们将在核实后**立即下架相关内容**。

## 常见问题

| 症状 | 处理 |
|---|---|
| 提交后报 `402 / 401007` | 服务商侧语音模型未开通（常见为需开"后付费"）；或把 `asr.driver` 设为 `local` |
| 麦克风不可用 | 必须用 `http://127.0.0.1` 打开（不要用局域网 IP）；浏览器允许麦克风权限 |
| 端口被占用 | 改 `app/config.yaml` 的 `server.port`，同步改 `scripts/run_server.sh` 里的 `--port` |
| 想换音色 / 换模型 / 换服务商 | 对话：`API_BASE_URL` + `llm.model` 指向任意 OpenAI 兼容服务；语音可整组独立配置（端点 + 模型 + 音色 + 可选 `SPEECH_API_KEY`），支持 TokenHub / MiniMax 系与 OpenAI 兼容端点 |
| 想尽量免费 / 全本地跑 | 语音本地化：`asr.driver: local` + `tts.driver: macos_say`（仅 macOS，免费）；对话模型需一个 OpenAI 兼容服务（云端或本地推理服务均可） |

## 开源协议

本项目基于 [MIT License](LICENSE) 发布，欢迎 Issue 与 PR。题库等内容的来源与使用要求见[内容来源与免责声明](#内容来源与免责声明)。

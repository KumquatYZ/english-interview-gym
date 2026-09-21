<p align="center">
  <img src="docs/icon.png" width="110" alt="English Interview Gym — logo">
</p>

<h1 align="center">English Interview Gym</h1>

<p align="center">
  <b>Speak with AI interviewers for 20 minutes a day — turn everyday English into interview fluency.</b><br>
  <b>Voice mock interviews · live hints · click-to-lookup · instant corrections · streaks &amp; stats — 100% local, your data never leaves your computer.</b>
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
  <img src="docs/overview.png" width="1100" alt="Overview: mock interviews · live hints · tap-to-translate · feedback reports · streaks">
</p>

## Contents

- [What is this](#what-is-this)
- [Quick start](#quick-start)
- [Use it on your phone (optional)](#use-it-on-your-phone-optional)
- [Model requirements & recommendations](#model-requirements--recommendations)
- [Feature guide](#feature-guide)
  - [Mock interviews](#mock-interviews)
  - [Sample answers &amp; hints](#sample-answers--hints)
  - [Click-to-lookup](#click-to-lookup)
  - [Instant feedback &amp; scoring](#instant-feedback--scoring)
  - [Session review &amp; errorbook](#session-review--errorbook)
  - [Streaks &amp; progress](#streaks--progress)
  - [Favourites &amp; daily review](#favourites--daily-review)
  - [Question card wall](#question-card-wall)
  - [Resume import](#resume-import)
- [Configuration](#configuration)
- [Customize &amp; extend](#customize--extend)
- [Project structure](#project-structure)
- [Privacy](#privacy)
- [Content sources & disclaimer](#content-sources--disclaimer)
- [FAQ](#faq)
- [License](#license)

## What is this

A self-hosted English interview trainer that runs on your own computer. The core loop is one thing only — **speaking out loud**:

> The AI interviewer asks (voice) → you answer out loud (transcribed) → instant corrections, a score, and a better way to say it → follow-up or next question

Every session feeds your streaks and stats; every question keeps a history, so you can re-practice it and watch a real improvement curve. Built for three common problems:

- **No one to practice with** — 3 AI interviewer personas × 82 curated questions (HR screen / technical / stress interview), available any time;
- **You don't know what to say** — every question ships with a 30–45 s sample answer (a **generic framework** version out of the box; import your resume to unlock a **personalized** version), every word across the app is one tap away from a definition, and a **read-aloud mode** covers the "I'm completely stuck" case;
- **No feedback after practice** — each answer gets Correction / Upgrade / Revision cards plus a 1–10 score; each session ends with a five-dimension review report and an errorbook.

| Feature | What it does | Where |
|---|---|---|
| 🎙️ Mock interviews | 4 roles × 5 question sets, voice Q&A with natural follow-ups | Home → "Choose your AI tutor" |
| 💼 Meeting practice | Meeting-host persona (Olivia) + original meeting banks: general meetings / beauty industry | Home → pick a set (💼 / 💄) |
| 💡 Sample answers | A 30–45 s model answer per question: generic / personalized | Chat → "📖 Sample answer" |
| 🔍 Click-to-lookup | IPA · contextual meaning · examples · pronunciation · favourites | Any word, anywhere |
| ✍️ Instant feedback | Correction / Upgrade / Revision + 1–10 score | Automatic after each answer |
| 📋 Review report | Five-dimension scoring + next-focus + errorbook | Top-right "Review" |
| 🔥 Streaks & progress | Streak days · daily goal ring · review progress · 14-day calendar | Home check-in panel |
| ⭐ Favourites & daily review | Paged word library (sort / delete) + ratio-based daily recall | Home → "⭐ Favourites" |
| 🗂 Question card wall | 120 cards: status / best score / trend / per-question history | Home → "Choose a question set" |
| 📄 Resume import | Unlocks personalized answers grounded in your real experience | "📄 My resume" |

## Quick start

> 📖 **User guide** (21 pages, all screenshots included): [DOCX download](docs/USER-GUIDE.docx) · [PDF download](docs/USER-GUIDE.pdf)

Two paths — pick one: **Option A (recommended, zero install)**: download the portable build, double-click, done. **Option B**: run from source (macOS / if you want to modify the code).

### Option A (recommended, zero install): portable build

**Step 1 · Download** — grab the **latest** build for your platform from the [**Releases page**](https://github.com/KumquatYZ/english-interview-gym/releases) (zip filenames include the version number):

| Platform | File | How to open |
|---|---|---|
| **Windows 10 / 11** | [`EnglishInterviewGym-v0.16.1-win64.zip`](https://github.com/KumquatYZ/english-interview-gym/releases/download/v0.16.1/EnglishInterviewGym-v0.16.1-win64.zip) | Unzip → double-click `EnglishInterviewGym.exe` → a standalone **app window** opens (no console window) |
| **macOS (Apple Silicon)** | [`EnglishInterviewGym-v0.16.1-macos.zip`](https://github.com/KumquatYZ/english-interview-gym/releases/download/v0.16.1/EnglishInterviewGym-v0.16.1-macos.zip) | Unzip → double-click 启动.command (if macOS blocks it the first time: right-click → Open) |

> 📦 Every zip **includes its version in the filename** (e.g. `…-v0.16.1-win64.zip`) so you can tell builds apart at a glance; all past versions live on the [Releases page](https://github.com/KumquatYZ/english-interview-gym/releases).

Both are green, portable builds: no Python, no terminal. **Everything (program, API keys, practice data, logs, browser cache) lives inside the app folder** — delete the folder for a complete uninstall; nothing is written to your C: drive user directories.

> macOS unzip tip: prefer the system extractor (just double-click the zip in Finder). Launch by **double-clicking 启动.command** (it strips the system quarantine flag automatically). If you see a **"'X' is damaged and can't be opened. You should move it to the Trash."** dialog: **click Cancel, NOT "Move to Trash"** — that is macOS blocking an unsigned app, and "Move to Trash" deletes app files (if that happens, just re-extract). From v0.15.11 on, the package is fully hardened and the dialog will not appear in normal use.

**Step 2 · Configure** (first run, ~3 minutes)

Open the app → top-right "**⚙️ 设置 (Settings)**" → fill in two groups:

| Group | What to fill | Notes |
|---|---|---|
| 💬 Chat service | Base URL + API key + model | Any OpenAI-compatible service (e.g. DeepSeek official: `https://api.deepseek.com` + `deepseek-chat`) |
| 🎙️ Speech service | ASR / TTS endpoints + models (+ optional speech key) | **Required on Windows** (no local fallback — otherwise recordings won't transcribe); copy-ready values: see [Buying speech separately (recommended combos)](#buying-speech-separately-recommended-combos) |

> 💡 Chat and speech can come from **different vendors**: e.g. chat with DeepSeek official (cheap, but no speech models) and buy speech separately from TokenHub / MiniMax / SiliconFlow / OpenAI — leaving the speech key empty reuses the chat key. Copy-ready endpoint/model/voice values: [Buying speech separately (recommended combos)](#buying-speech-separately-recommended-combos).

**Step 3 · Your first session (~10 minutes)**

1. "选择你的 AI 导师 / Pick your AI tutor" → tap a tutor to **preview the voice**, pick a persona (pick Olivia for meeting practice);
2. "选择题集 / Question sets" → start with `baseline-8` (8-question warm-up); for meetings pick "外企会议通用 16 题" or "美妆行业会议 22 题";
3. Open any question → "🎙 从这题开练 / Practice this" → tap the mic (or press Space) and speak;
4. Tap the mic again when done → review the transcript, feedback cards and score → next question;
5. When finished, click "复盘 / Review" (top-right) for the full session report.

### Updating & uninstalling (portable build)

**Updating to a new version**:
1. Download the new zip (filename includes the version number — grab the latest);
2. Best practice: extract into a **new folder**; you may also extract over the old folder and relaunch — **from v0.16.1 on, missing question sets/personas are filled in automatically** (your existing files and customisations are never overwritten);
3. To keep your practice history and API keys: copy `data/`, `.env` and `config.local.yaml` from the old folder into the new one (skip this for a fresh start).

**Complete uninstall (Windows / macOS)**: this is a green portable build — program, API keys, practice data, logs and the browser cache **all live inside the app folder** (on Windows even the WebView cache is stored in `webview_data/` inside the folder). **Delete the folder = fully uninstalled**; nothing is written to your C: drive user directories (e.g. AppData). Back up `data/` first if you want to keep your records; delete any desktop shortcut you created.

**Check your version**: in the app → "⚙️ Settings", the version is shown in the bottom corner (e.g. `版本 0.16.1`).

### Option B (optional): run from source (macOS / developers)

**Requirements**: macOS (Apple Silicon recommended) + Python 3.12 + `ffmpeg` (`brew install ffmpeg`) + an API key (bring your own — any OpenAI-compatible service).

```bash
git clone https://github.com/KumquatYZ/english-interview-gym.git
cd english-interview-gym
python3 -m venv .venv            # or with uv: uv venv .venv --python 3.12
.venv/bin/pip install -r app/requirements.txt

cp app/.env.example app/.env     # set API_KEY=your-key, API_BASE_URL=your-service-url
                                 # chat key required; speech key optional (SPEECH_API_KEY, falls back to the chat key)
                                 # or run the interactive helper: python3 scripts/setup_env.py

bash scripts/run_server.sh       # or double-click 打开训练系统.command
```

Open http://127.0.0.1:8765 (allow microphone access on first use).

**Other scripts (optional)**:

```bash
.venv/bin/python scripts/check_stack.py       # health-check chat / ASR / TTS end to end
.venv/bin/python scripts/baseline_report.py   # practice weekly report
```

## Use it on your phone (optional)

**Easiest path (recommended)**: open "**⚙️ 设置 (Settings) → 📱 手机访问 (Mobile access) → Enable**" — the app generates certificates and starts the HTTPS channel automatically, then shows the phone URL plus step-by-step setup (works for the macOS / Windows portable builds too).

For an iPhone that should reach it **from any network** (not just the same Wi-Fi), install [Tailscale](https://tailscale.com/download) on both the Mac and the iPhone (free, private mesh VPN — just sign in with the same account). When Tailscale is detected, mobile access uses it automatically and stays reachable inside your private network only.

**One-time phone setup**:

- Install the certificate: open the URL shown in Settings with Safari ("not private" warning → continue) → then open `<url>/ca.crt` to download the profile → "Settings → General → VPN & Device Management" install → "General → About → Certificate Trust Settings" enable full trust;
- Open the same URL in Safari → "Share → **Add to Home Screen**" — launch from that icon for a full-screen, app-like experience.

> Note: the phone is a thin client — sessions and data stay on the computer running the app (keep it on and online). CLI users can also use `bash scripts/gen_https_cert.sh` + `scripts/https_proxy.py` (equivalent to the in-app one-click enable).

## Model requirements &amp; recommendations

A full session uses **three kinds of models** — not just a chat model. They **can be configured separately**: chat and speech (ASR/TTS) may come from **different vendors with different keys** (e.g. chat with DeepSeek's official API, speech bought from another vendor) — see [Buying speech separately (recommended combos)](#buying-speech-separately-recommended-combos). Common combos:

| Role | Where it's used | Recommended models (examples) | Reference price (CNY, pay-as-you-go) |
|---|---|---|---|
| 💬 Chat model | Follow-ups, sample answers, corrections & scoring, review reports, word glosses | **DeepSeek-V4.1-Flash** (`deepseek/deepseek-flash`, default); alternative **GLM-5.3-Flash** (`glm-5.3-flash`) | DeepSeek: ¥1–2 in / ¥4–8 out; GLM: ¥0.8 / ¥2.8 (per million tokens, off-peak/peak) |
| 🎙️ Speech recognition (ASR) | Transcribing your spoken answers | **Hy-ASR-3.0-Preview** (`hy-asr-3.0-preview`, default); alternative `wand-asr-v1` | Hy-ASR: ¥0.00022/s (~¥0.79/h); WAND: ¥0.0005/s |
| 🔊 Speech synthesis (TTS) | The interviewer's voice | **MiniMax-Speech-2.8-Turbo** (`minimax-speech-2.8-turbo`, default, 4 English voices included); `-hd` for higher quality | Turbo: ¥2 / 10k characters; HD: ¥3.5 / 10k characters |

**Cost estimate (20 min/day, everything in the cloud)**: chat ≈ ¥0.1/day + ASR ≈ ¥0.26/day + TTS ≈ ¥0.2–0.4/day ≈ **¥0.6–0.8/day, about ¥20/month** (pay-as-you-go; your actual bill depends on your provider. Evening practice usually falls into off-peak windows, where prices are lower).

**Both speech legs can run for free locally (macOS)**:

- `asr.driver: local` — on-device recognition with mlx-whisper (Apple Silicon, free);
- `tts.driver: macos_say` — macOS built-in `say` (free, robotic voice).

With both enabled, the only cost left is the chat model: **≈ ¥0.1/day**.

**Notes**:

- If a speech call returns `402 / 401007`: your provider likely hasn't enabled the speech models (commonly a "postpaid billing" toggle) — follow its console prompt once;
- Pricing is set by your provider (DeepSeek models commonly charge 2x during weekday 9:00–12:00 and 14:00–18:00 Beijing time; other hours are off-peak);
- The default fallback chain includes `kimi-k3` (pricier; only used if the primary model fails) — adjust `llm.fallback_models` if you care about cost.

To switch models, edit `app/config.yaml`: `llm.model` / `asr.model` / `tts.cloud_model` (all support fallback chains).

### Buying speech separately (recommended combos)

**Why**: many chat vendors (e.g. DeepSeek's official API) have **no speech models**, while speech (ASR/TTS) is core to this app. So chat and speech are two independent configurations — use one vendor for chat, another for speech, completely decoupled:

- **Chat service**: API key + base URL + model (e.g. DeepSeek official);
- **Speech service**: its own endpoints + models + (optional) speech-only key. **Leave the speech key empty to reuse the chat key** — no duplication needed if both use the same vendor (e.g. both TokenHub).

Where to configure: in-app "⚙️ 设置 (Settings) → 🎙️ 语音服务", or `app/.env` (`SPEECH_API_KEY`) + `app/config.yaml` (`asr.*` / `tts.*`).
**Protocols are auto-detected from the endpoint URL**: endpoints containing `/audio/transcriptions` or `/audio/speech` use the OpenAI-compatible protocol; everything else uses the TokenHub / MiniMax-style protocol.

**Common speech services (all directly supported; bring your own account):**

| Service | ASR | TTS | Where |
|---|---|---|---|
| Tencent Cloud TokenHub | ✅ `hy-asr-3.0-preview` | ✅ MiniMax family (`minimax-speech-2.8-turbo`) | https://console.cloud.tencent.com/tokenhub |
| MiniMax platform | – | ✅ `speech-2.8-turbo` / `-hd` (well-regarded English voices) | https://platform.minimaxi.com |
| SiliconFlow (硅基流动) | ✅ `FunAudioLLM/SenseVoiceSmall` etc. (free models available) | ✅ `FunAudioLLM/CosyVoice2-0.5B` / fish-speech etc. | https://siliconflow.cn |
| OpenAI | ✅ `whisper-1` / `gpt-4o-transcribe` | ✅ `gpt-4o-mini-tts` | https://platform.openai.com |
| Alibaba Bailian / Volcengine / iFlytek | ✅ | ✅ | their consoles (choose OpenAI-compatible mode) |

**Configuration examples** (columns: ASR endpoint + ASR model; TTS endpoint + TTS model + voice):

| Service | ASR (endpoint / model) | TTS (endpoint / model / voice) |
|---|---|---|
| TokenHub | `https://tokenhub.tencentmaas.com/v1/wand/asrproxy/sync_transcribe` / `hy-asr-3.0-preview` | `https://tokenhub.tencentmaas.com/v1/wand/minimax-tts/sync_tts` / `minimax-speech-2.8-turbo` / `English_Graceful_Lady` |
| MiniMax (official) | — (no ASR yet) | `https://api.minimaxi.com/v1/t2a_v2` / `speech-2.8-turbo` / `English_Graceful_Lady` |
| SiliconFlow | `https://api.siliconflow.cn/v1/audio/transcriptions` / `FunAudioLLM/SenseVoiceSmall` | `https://api.siliconflow.cn/v1/audio/speech` / `FunAudioLLM/CosyVoice2-0.5B` / `FunAudioLLM/CosyVoice2-0.5B:alex` |
| OpenAI | `https://api.openai.com/v1/audio/transcriptions` / `whisper-1` | `https://api.openai.com/v1/audio/speech` / `gpt-4o-mini-tts` / `alloy` |

> **Voice IDs differ per vendor**: TokenHub / MiniMax use `English_Graceful_Lady`, `English_Trustworth_Man`, `English_ManWithDeepVoice`, etc.; OpenAI uses `alloy`, `nova`, etc.
> Speech can come from a different vendor than chat — just put that vendor's key in the "speech service key" field (empty = reuse the chat key).
> If a TokenHub speech call returns `402 / 401007`: enable "postpaid billing" once in its console; pricing is set by each vendor.

## Feature guide

### Mock interviews

**What it does**: a real back-and-forth conversation — the interviewer speaks a question, you answer out loud, and your speech is transcribed automatically before the follow-up or next question.

- 4 roles (`materials/personas/`): `hr-friendly` (corporate HR screen), `tech-lead` (technical deep-dive), `stress` (pressure round), `meeting-host` (cross-functional meetings); each ships with its positioning, evaluation focus, probing strategy and a realistic dialogue few-shot — adapt them to your own target role;
- 5 question sets: `baseline-8` (8 warm-up questions), `interview-core` (14 core questions), `mnc-60` (60 high-frequency big-tech questions), `meetings-core` (16 general business-meeting questions), `cosmetics-meetings` (22 beauty-industry meeting questions; topics drawn from public industry coverage, all questions originally written).

**How to use**: pick a persona → pick a set → "🎙 Practise from this question" → click the mic (or press Space) → click again to finish → read the feedback → next question. Two answering modes are available in the chat header ("speak freely / read the sample aloud"); you can skip a question or end the session with "Review" at any time.

**How to configure**:
- Max answer length: `app/config.yaml` → `session.max_answer_seconds` (default 120 s);
- Voices: `app/config.yaml` → `tts.voices` (one voice per persona);
- Your own questions/sets: see [Customize &amp; extend](#customize--extend).

### Sample answers &amp; hints

**What it does**: before answering any question, see how it *could* be answered — a 30–45 s (about 60–100 words) model answer **benchmarked to real corporate-interview expectations** (lead with the answer, back it with evidence and numbers, no flattery or student-speak):

- **🧩 Generic version**: works out of the box, with `[bracketed]` placeholders you replace with your own details;
- **🎯 Personalized version**: unlocked after importing your resume — built from your real experience and numbers (see [Resume import](#resume-import)).

**How to use**: in the chat, click "📖 Sample answer" → switch between the two tabs → click "🎧 Read this aloud" to enter read-aloud mode.

**How to configure**: none needed; the personalized version depends on whether you imported a resume.

### Click-to-lookup

**What it does**: tap **any English word** in the conversation, sample answers, feedback cards or review reports and get IPA, part of speech, a **context-aware** meaning, an example sentence and pronunciation; one click saves it to your vocabulary. The same word gets different glosses in different contexts.

**How to use**: click a word → read the card → 🔊 hear it → ⭐ save it. Saved words go to "⭐ Favourites" where they can be reviewed daily and managed.

**How to configure**: none needed; lookups are cached in `data/gloss_cache.json`, so repeat lookups are instant.

### Instant feedback &amp; scoring

**What it does**: every answer automatically gets three cards:

- **Correction** — grammar / word choice / tense fixes;
- **Upgrade** — turns casual English into the polished phrasing interviewers expect;
- **Revision** — a full polished rewrite you can read back.

Plus a 1–10 overall score. In read-aloud mode you also get a **reading accuracy** score (word-level missed / extra words against the script).

**How to use**: it appears automatically after each answer; words inside the cards are clickable and savable too.

**How to configure**: none.

### Session review &amp; errorbook

**What it does**: end a session to generate a "Review": scores across content / structure / grammar / vocabulary / fluency, a next-focus suggestion and a drill list; mistakes that keep recurring are collected into an errorbook for focused re-practice.

**How to use**: top-right "Review" → the report takes 10–20 s to generate (also saved to `data/reports/`).

**How to configure**: none.

### Streaks &amp; progress

**What it does**: tracks your "speaking volume" like a fitness app: streak days, a daily goal ring (20 minutes by default), a 14-day minutes calendar and stat cards; hitting 3 / 7 / 14 / 30 / 50 / 100 consecutive days triggers a celebration.

**How to use**: the check-in panel on the home page updates automatically; every finished session counts toward today.

**How to configure**: change `app/config.yaml` → `session.daily_goal_minutes` (default 20).

### Favourites &amp; daily review

**What it does**: saved words live in a dictionary-style library — 8 entries a page with paging, a "Newest / A–Z" sort toggle and two-step delete. The "🔁 Daily review" tab draws a batch of words every day at a configurable ratio, prioritising words never reviewed, failed last time, or long unseen. Recall first, then reveal the meaning, then mark "😵 missed / 😎 got it"; missed words come back for a second pass in the same session and are scheduled first for tomorrow. Progress feeds the check-in panel's "Today's review x/y" line.

**How to use**: home → "⭐ Favourites" → "📚 Library" to browse / sort / delete / look up words; "🔁 Daily review" → Start → recall → reveal → mark.

**How to configure**: `app/config.yaml` → `review.ratio` (daily share of your saved words, default 0.3), `review.min_per_day` (default 5), `review.max_per_day` (default 30).

### Question card wall

**What it does**: each question set opens as a wall of illustrated cards (title, status, best score). Open a card for its **per-question history** — date, mode (free / read-aloud), duration, speaking rate (WPM), score — with a score trend line; you can restart practice from any question.

**How to use**: home → "Choose a question set" → card wall; the "▶ Continue" button jumps to your first unpractised question (it becomes "▶ Practise again" once the set is finished).

**How to configure**: drop a PNG at `materials/question-bank/images/<set>/<question-id>.png` and it shows up on the card wall (the bundled sets already include illustrations).

### Resume import

**What it does**: upload your resume (`.docx` / `.pdf` / paste text) to unlock the **🎯 personalized** sample answers, built from your real experience, projects and numbers. The resume is stored on your machine only.

**How to use**: top-right "📄 My resume" → choose a file or paste text → save; delete it any time (you simply fall back to generic versions).

**How to configure**: you can also edit `materials/profile.md` by hand (see `materials/profile.example.md` for the format).

## Configuration

### Environment variables (`app/.env`)

| Variable | Required | Purpose |
|---|---|---|
| `API_KEY` | ✅ | Chat service key (LLM) |
| `API_BASE_URL` | – | Chat service base URL (your OpenAI-compatible service) |
| `SPEECH_API_KEY` | – | Speech-service-only key (may differ from chat; empty = reuse `API_KEY`) |

### App settings (`app/config.yaml`)

| Setting | Default | Notes |
|---|---|---|
| `llm.base_url` | empty | Your OpenAI-compatible base URL (or use `API_BASE_URL`) |
| `llm.model` | `deepseek/deepseek-flash` | Main chat model |
| `llm.fallback_models` | see file | Fallback chain if the main model fails |
| `asr.driver` | `auto` | `auto` / `cloud` (cloud ASR) / `local` (mlx-whisper, macOS only) |
| `asr.endpoint` / `tts.endpoint` | empty | Cloud speech endpoints; when empty, local mode is used |
| `tts.driver` | `cloud` | `cloud` / `macos_say` (offline fallback) |
| `tts.voices` | see file | One voice per persona |
| `review.ratio` | `0.3` | Daily review share (= saved words × this ratio) |
| `review.min_per_day` / `review.max_per_day` | `5` / `30` | Daily review floor / ceiling |
| `session.daily_goal_minutes` | `20` | Daily goal (minutes), drives the check-in ring |
| `session.max_answer_seconds` | `120` | Max length of one answer |
| `server.port` | `8765` | Server port |
| `tools.ffmpeg` | `ffmpeg` | Path to the ffmpeg binary |

### Runtime data (`data/`, local only)

| Path | Contents |
|---|---|
| `data/sessions/*.jsonl` | Per-round records of every session (with scores) |
| `data/reports/` | Review reports |
| `data/errorbook.jsonl` | Errorbook |
| `data/favorites.jsonl` | Saved words &amp; sentences |
| `data/reviews.jsonl` | Word review records (daily recall answers) |
| `data/review_decks.json` | Daily review plan cache (fixed per day) |
| `data/gloss_cache.json` | Click-to-lookup cache |
| `data/audio/` | Recordings |

## Customize &amp; extend

- **Questions / question sets** — plain YAML; edit or add files under `materials/question-bank/`:

  ```yaml
  key: my-bank
  title: My question set
  questions:
    - id: q1
      round: HR screen
      category: Intro
      text: "Tell me about yourself."
      intent: Why they ask this.
      hint: How to structure your answer.
      followups:
        - "What's the one thing you want me to remember?"
  ```

- **Question illustrations** — drop a PNG at `materials/question-bank/images/<set>/<question-id>.png` and it appears on the card wall;
- **Interviewer personas** — `materials/personas/*.md` (the built-in three include positioning, evaluation focus and a realistic dialogue few-shot — edit them for your own role);
- **Story bank** — copy `materials/stories/template.md` to build 5–8 polished personal stories that make your answers concrete.

## Project structure

```text
english-interview-gym/
├── 打开训练系统.command          # one-click launcher (macOS double-click)
├── app/
│   ├── config.yaml              # app settings (models / speech / daily goal)
│   ├── .env.example             # env template (copy to .env and add your key)
│   ├── requirements.txt
│   ├── server/                  # FastAPI backend: sessions · LLM · ASR · TTS · reports
│   └── web/                     # single-page frontend (no build step)
├── materials/
│   ├── personas/                # 3 interviewer personas
│   ├── question-bank/           # 3 question sets (YAML) + illustrations + meta
│   ├── stories/                 # personal story bank (template + guide)
│   ├── wordlist/                # word list
│   └── profile.example.md       # resume template (copy to profile.md and edit)
├── scripts/                     # setup_env · run_server · check_stack · baseline_report
├── data/                        # runtime data (local only, gitignored)
└── docs/                        # RUNBOOK · PRACTICE-PLAN · image assets
```

## Privacy

- **100% local**: the server only listens on `127.0.0.1`; all training data (recordings, transcripts, reports, vocabulary) lives in `data/` on your machine and is never uploaded to any third party;
- **Minimal outbound calls**: audio and text of your answers are sent only to the API endpoint **you** configured (for transcription and feedback); your key stays in `app/.env` on your machine;
- **No telemetry**: no analytics, no accounts;
- **Zero personal data in the public repo**: `app/.env`, `materials/profile.md` and `data/` are gitignored and never shipped.

## Content sources & disclaimer

- **Sources**: the question banks (`materials/question-bank/`) are compiled from **public internet sources** (community interview write-ups, public question round-ups, public job postings and requirements). Wording was generalized during compilation; the per-question analysis and hints are written by this project;
- **No claims**: this project claims no rights over the original sources and does not guarantee any correspondence to the actual question banks of any specific company;
- **Usage**: the question text is for **personal study** only — please don't use it commercially. The code is open-sourced under MIT;
- **Takedown**: if you believe any content in this repository (questions, illustrations, etc.) infringes your rights, please contact us via [Issues](../../issues) — we will verify and **take the relevant content down promptly**.

## FAQ

| Symptom | Fix |
|---|---|
| `402 / 401007` on submit | Your provider hasn't enabled the speech models (usually a "postpaid billing" toggle); or set `asr.driver: local` |
| Microphone unavailable | Open via `http://127.0.0.1` (not a LAN IP); allow microphone permission in the browser |
| Port in use | Change `server.port` in `app/config.yaml` and the `--port` flag in `scripts/run_server.sh` |
| Different voices / models / vendors | Chat: `API_BASE_URL` + `llm.model` for any OpenAI-compatible service; speech is a fully independent group (endpoints + models + voices + optional `SPEECH_API_KEY`) supporting TokenHub/MiniMax-style and OpenAI-compatible endpoints |
| Want it (mostly) free / fully local | Local speech: `asr.driver: local` + `tts.driver: macos_say` (macOS only, free); the chat model still needs an OpenAI-compatible service (cloud or a local inference server) |

## License

MIT — see [LICENSE](LICENSE). Content sources and usage terms: see [Content sources & disclaimer](#content-sources--disclaimer).

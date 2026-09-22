"""EngTraining FastAPI 入口。

启动：cd app && ../.venv/bin/python -m uvicorn server.main:app --host 127.0.0.1 --port 8765
（或直接 bash scripts/run_server.sh）
"""
import json
import re
import shutil
import threading
import time
from pathlib import Path

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from . import config, llm, mobile, prompts, store, tts
from . import session as sess

WEB = config.web_dir()


@asynccontextmanager
async def _lifespan(_app):
    try:
        shutil.rmtree(config.data_dir() / "tmp", ignore_errors=True)  # 清理上次异常退出的中间文件
    except Exception:  # noqa: BLE001
        pass
    mobile.autostart()  # 上次启用了手机访问则自动恢复（失败静默）
    yield


app = FastAPI(title="EngTraining", version="0.16.3", lifespan=_lifespan)


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "version": app.version,
        "llm_model": config.get("llm.model"),
        "asr_driver": config.get("asr.driver"),
        "tts_driver": config.get("tts.driver"),
        "max_answer_seconds": config.get("session.max_answer_seconds", 120),
        "api_key_set": bool(config.api_key()),
        "api_configured": bool(config.api_key() and (config.env("API_BASE_URL") or config.get("llm.base_url", ""))),
        "can_quit": bool(getattr(app.state, "quit_callback", None)),
        "frozen": config.is_frozen(),
    }


def _mask_key(k: str) -> str:
    if not k:
        return ""
    return (k[:6] + "…" + k[-4:]) if len(k) > 14 else "已设置"


def _settings_payload() -> dict:
    return {
        "version": app.version,
        "frozen": config.is_frozen(),
        "env_file": str(config.env_path()),
        "config_file": str(config.config_local_path()),
        "api_key_set": bool(config.api_key()),
        "api_key_masked": _mask_key(config.api_key()),
        "api_base_url": config.env("API_BASE_URL") or config.get("llm.base_url", "") or "",
        "llm_model": config.get("llm.model", "") or "",
        "asr_endpoint": config.get("asr.endpoint", "") or "",
        "asr_model": config.get("asr.model", "") or "",
        "tts_endpoint": config.get("tts.endpoint", "") or "",
        "tts_model": config.get("tts.cloud_model", "") or "",
        "tts_voice": config.get("tts.cloud_voice_id", "") or "",
        "speech_key_set": bool(config.env("SPEECH_API_KEY", "")),
        "speech_key_masked": _mask_key(config.env("SPEECH_API_KEY", "")) if config.env("SPEECH_API_KEY", "") else "",
        "can_quit": bool(getattr(app.state, "quit_callback", None)),
    }


@app.get("/api/settings")
def settings_get():
    return _settings_payload()


@app.post("/api/settings")
def settings_set(payload: dict):
    """写入用户设置：API Key / 接口地址 → .env；模型与语音端点 → config.local.yaml。保存后立即生效。"""
    try:
        env_up = {}
        if "api_key" in payload:
            env_up["API_KEY"] = str(payload.get("api_key") or "").strip()
        if "api_base_url" in payload:
            env_up["API_BASE_URL"] = str(payload.get("api_base_url") or "").strip()
        if "speech_api_key" in payload:
            env_up["SPEECH_API_KEY"] = str(payload.get("speech_api_key") or "").strip()
        if env_up:
            config.save_env(env_up)
        cfg_up: dict = {}

        def _put(section: str, key: str, val) -> None:
            v = str(val or "").strip()
            if v:
                cfg_up.setdefault(section, {})[key] = v

        _put("llm", "model", payload.get("llm_model"))
        _put("asr", "endpoint", payload.get("asr_endpoint"))
        _put("asr", "model", payload.get("asr_model"))
        _put("tts", "endpoint", payload.get("tts_endpoint"))
        _put("tts", "cloud_model", payload.get("tts_model"))
        _put("tts", "cloud_voice_id", payload.get("tts_voice"))
        if cfg_up:
            config.save_config(cfg_up)
        llm.reset()
        return {"ok": True, "settings": _settings_payload()}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/selftest/llm")
def selftest_llm():
    """对话服务自检：基础对话 + 一次真实反馈生成，返回原始返回片段（排障用）。"""
    out: dict = {"ok": False, "version": app.version}
    out["model"] = config.get("llm.model", "") or ""
    out["base"] = config.env("API_BASE_URL") or config.get("llm.base_url", "") or ""
    try:
        client = llm.get_llm()
    except Exception as e:  # noqa: BLE001
        out["error"] = f"初始化失败：{str(e)[:300]}"
        return out
    try:
        plain = client.chat(
            [{"role": "user", "content": "Reply with exactly the two letters: OK"}],
            temperature=0,
            max_tokens=8,
        )
        out["plain"] = (plain or "").strip()[:120]
    except Exception as e:  # noqa: BLE001
        out["error"] = f"基础对话失败：{str(e)[:400]}"
        return out
    try:
        fb = client.chat_json(
            prompts.feedback_messages(
                prompts.load_persona("hr-friendly"),
                "Tell me about yourself.",
                "I am a chemistry PhD student working on AI for science.",
                [],
                mode="free",
                script="",
            )
        )
        if isinstance(fb, dict):
            out["feedback_keys"] = ", ".join(list(fb.keys()))[:300]
        else:
            out["feedback_keys"] = f"（不是对象：{type(fb).__name__}）"
        out["feedback_preview"] = json.dumps(fb, ensure_ascii=False)[:500]
        out["ok"] = True
    except Exception as e:  # noqa: BLE001
        out["error"] = f"反馈生成失败：{str(e)[:400]}"
    return out


@app.post("/api/quit")
def quit_app():
    """完全退出程序（仅打包版：启动器注入回调；开发模式请按 Ctrl+C）。"""
    cb = getattr(app.state, "quit_callback", None)
    if not cb:
        raise HTTPException(400, "当前进程不支持在此退出（开发模式请按 Ctrl+C）")
    threading.Thread(target=cb, daemon=True).start()
    return {"ok": True}


@app.get("/api/personas")
def personas():
    return prompts.list_personas()


@app.get("/api/question-sets")
def question_sets():
    return prompts.list_question_sets()


@app.post("/api/session/start")
def session_start(payload: dict):
    try:
        return sess.start(payload.get("persona", "hr-friendly"), payload.get("set", "baseline-8"), start_idx=payload.get("start", 0))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


@app.get("/api/session/{sid}")
def session_get(sid: str):
    try:
        return sess.get_state(sid)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(404, str(e))


@app.post("/api/session/{sid}/answer")
async def session_answer(
    sid: str,
    audio: UploadFile = File(...),
    mode: str = Form("free"),
    script: str = Form(""),
):
    d = config.data_dir() / "audio" / sid
    d.mkdir(parents=True, exist_ok=True)
    ext = Path(audio.filename or "a.webm").suffix or ".webm"
    dst = d / f"{int(time.time() * 1000)}{ext}"
    with dst.open("wb") as f:
        shutil.copyfileobj(audio.file, f)
    try:
        return sess.submit_answer(sid, dst, mode=mode, script=script)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/session/{sid}/suggestion")
def session_suggestion(sid: str, refresh: int = 0):
    try:
        return sess.get_suggestion(sid, refresh=bool(refresh))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.post("/api/session/{sid}/skip")
def session_skip(sid: str):
    try:
        return sess.skip_current(sid)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, str(e))


@app.post("/api/session/{sid}/end")
def session_end(sid: str):
    try:
        return sess.end(sid)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/sessions")
def sessions_list():
    return store.list_sessions()


@app.get("/api/gloss")
def gloss_get(word: str, context: str = ""):
    try:
        return sess.gloss(word, context)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.post("/api/favorite")
def favorite_add(payload: dict):
    try:
        store.append_favorite(
            {
                "type": payload.get("type", "word"),
                "text": (payload.get("text") or "")[:800],
                "note": (payload.get("note") or "")[:400],
                "ipa": (payload.get("ipa") or "")[:80],
                "session": payload.get("session", ""),
            }
        )
        return {"ok": True}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.post("/api/favorite/delete")
def favorite_delete(payload: dict):
    try:
        store.delete_favorite((payload.get("text") or "")[:800], payload.get("kind") or "word")
        return {"ok": True}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/favorites")
def favorites_list():
    return store.list_favorites()


@app.get("/api/review")
def review_get():
    try:
        return store.review_today()
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.post("/api/review/answer")
def review_answer(payload: dict):
    try:
        return store.append_review_answer(payload.get("word") or "", bool(payload.get("ok")))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/stats")
def stats_get():
    return store.stats()


@app.get("/api/tts")
def tts_get(text: str, persona: str = ""):
    try:
        data = tts.synth(text, persona=persona or None)
        return Response(content=data, media_type="audio/mpeg")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.get("/api/set/{set_key}")
def set_detail(set_key: str):
    """题集详情：每题标题/图片/练习统计/历史（供题目卡片墙）。"""
    try:
        qset = prompts.load_question_set(set_key)
        meta = (prompts.load_question_meta() or {}).get(set_key) or {}
        hist = store.attempts_by_question()
        img_dir = config.materials_dir() / "question-bank" / "images" / set_key
        out = []
        for i, q in enumerate(qset.get("questions") or []):
            qid = q.get("id") or f"q{i + 1}"
            qtext = (q.get("text") or "").strip()
            atts = hist.get(qtext, [])
            m = meta.get(qid) or {}
            img = f"/media/{set_key}/{qid}.png" if (img_dir / f"{qid}.png").exists() else None
            best = max([a.get("score") for a in atts if a.get("score")], default=None)
            out.append(
                {
                    "i": i, "id": qid, "text": qtext,
                    "round": q.get("round"), "category": q.get("category"), "tag": q.get("tag"),
                    "intent": q.get("intent"), "hint": q.get("hint"), "title": m.get("title"),
                    "img": img, "attempts": len(atts), "last_at": atts[0].get("ts") if atts else None,
                    "best_score": best, "history": atts[:20],
                }
            )
        done = sum(1 for x in out if x["attempts"] > 0)
        return {"key": set_key, "title": qset.get("title", set_key), "note": qset.get("note", ""),
                "done": done, "count": len(out), "questions": out}
    except Exception as e:  # noqa: BLE001
        raise HTTPException(404, str(e))


_CFB_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _docx_plain_text(raw: bytes) -> str:
    """汇总 docx 内全部文字（正文 + 表格 + 文本框 + 页眉页脚 + 脚注），不依赖 python-docx。"""
    import io
    import re
    import zipfile

    def _unescape(s: str) -> str:
        return (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                .replace("&apos;", "'").replace("&amp;", "&"))

    try:
        zf = zipfile.ZipFile(io.BytesIO(raw))
    except Exception as e:  # noqa: BLE001
        raise ValueError("无法读取 .docx（文件损坏，或不是真正的 Word 文档）") from e
    with zf:
        parts = [n for n in zf.namelist()
                 if re.fullmatch(r"word/(document|header\d*|footer\d*|footnotes|endnotes)\.xml", n)]
        parts.sort(key=lambda n: (n != "word/document.xml", n))
        lines = []
        for n in parts:
            xml = zf.read(n).decode("utf-8", errors="ignore")
            for para in xml.split("</w:p>"):
                para = re.sub(r"<w:(?:br|cr)\s*/>", "\n", para)
                txt = "".join(_unescape(m.group(1))
                              for m in re.finditer(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", para, re.S))
                if txt.strip():
                    lines.extend(x for x in txt.splitlines() if x.strip())
        return "\n".join(lines)


def _pdf_plain_text(raw: bytes) -> str:
    """PDF → 纯文本：pypdf 与 pdfminer.six 双引擎，取文字更多的结果（部分中文/特殊字体 PDF 单引擎读不出）。"""
    import io

    pypdf_txt = ""
    pypdf_err = None
    try:
        import pypdf

        r = pypdf.PdfReader(io.BytesIO(raw))
        pypdf_txt = "\n".join((pg.extract_text() or "") for pg in r.pages)
    except Exception as e:  # noqa: BLE001
        pypdf_err = e
    pdfminer_txt = ""
    try:
        from pdfminer.high_level import extract_text as _pm_extract

        pdfminer_txt = _pm_extract(io.BytesIO(raw)) or ""
    except Exception:  # noqa: BLE001
        pass

    best = pypdf_txt
    if len(pdfminer_txt.strip()) > len(pypdf_txt.strip()):
        best = pdfminer_txt
    if len(best.strip()) < 30:
        if pypdf_err is not None and not pdfminer_txt.strip():
            raise ValueError(f"无法读取 PDF（文件损坏或加密？）：{pypdf_err}") from pypdf_err
        raise ValueError("PDF 中没有可提取的文字（可能是扫描件/图片版）。请改用 Word 版简历，或直接把文字粘贴进来")
    return best


def _extract_resume_text(filename: str, raw: bytes) -> str:
    """简历文件 → 纯文本（支持 docx / pdf / txt / md；含文本框/表格/页眉）。"""
    name = (filename or "").lower()
    if name.endswith(".doc") or raw[:8] == _CFB_MAGIC:
        raise ValueError("旧版 .doc 格式暂不支持：请在 Word / WPS 里「另存为 → .docx」后再导入")
    if name.endswith(".docx"):
        return _docx_plain_text(raw)
    if name.endswith(".pdf"):
        return _pdf_plain_text(raw)
    if name.endswith((".txt", ".md")):
        for enc in ("utf-8-sig", "gb18030", "utf-16"):
            try:
                return raw.decode(enc)
            except (UnicodeDecodeError, UnicodeError):
                continue
        return raw.decode("utf-8", errors="ignore")
    raise ValueError("不支持的文件类型（支持 docx / pdf / txt / md），也可以直接把文字粘贴进来")


@app.get("/api/profile")
def profile_status():
    """个人资料状态（本地保存；导入后示范答案将额外提供「定制版」）。"""
    t = prompts.load_profile()
    return {"has_profile": bool(t), "chars": len(t), "head": t[:150]}


@app.post("/api/profile/text")
def profile_set_text(payload: dict):
    text = (payload.get("text") or "").strip()
    if len(text) < 30:
        raise HTTPException(400, "内容太短（至少 30 字）")
    (config.materials_dir() / "profile.md").write_text(text, encoding="utf-8")
    return {"ok": True, "chars": len(text)}


@app.post("/api/profile/upload")
async def profile_upload(file: UploadFile = File(...)):
    raw = await file.read()
    if len(raw) > 8 * 1024 * 1024:
        raise HTTPException(400, "文件过大（上限 8MB）")
    try:
        text = _extract_resume_text(file.filename or "", raw).strip()
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(400, f"解析失败：{e}")
    if len(text) < 30:
        raise HTTPException(400, f"解析出的文本太短（{len(text)} 字，至少 30 字）：请检查文件内容，或直接粘贴文字")
    (config.materials_dir() / "profile.md").write_text(text, encoding="utf-8")
    return {"ok": True, "chars": len(text)}


@app.delete("/api/profile")
def profile_delete():
    p = config.materials_dir() / "profile.md"
    if p.exists():
        p.unlink()
    return {"ok": True}


@app.get("/")
def index():
    # no-cache + 按资源 mtime 自动注入 ?v= 版本号：改前端后刷新即生效，无需手动改版本
    html = (WEB / "index.html").read_text(encoding="utf-8")
    ver = int(max((WEB / "app.js").stat().st_mtime, (WEB / "style.css").stat().st_mtime))
    html = re.sub(r"\?v=\d+", f"?v={ver}", html)
    return Response(html, media_type="text/html", headers={"Cache-Control": "no-cache"})


@app.get("/manifest.webmanifest")
def webmanifest():
    """PWA manifest（「添加到主屏幕」用；含 iPhone 图标与独立窗口配置）。"""
    p = WEB / "manifest.webmanifest"
    if not p.exists():
        raise HTTPException(404, "manifest not found")
    return Response(p.read_text(encoding="utf-8"), media_type="application/manifest+json", headers={"Cache-Control": "no-cache"})


@app.get("/ca.crt")
def ca_cert():
    """手机安装用：本机 HTTPS 的自签 CA 证书（手机访问启用后自动生成）。"""
    p = mobile.ca_path()
    if not p.exists():
        raise HTTPException(404, "no ca.crt（先在「⚙️ 设置 → 手机访问」里启用）")
    return FileResponse(str(p), media_type="application/x-x509-ca-cert", filename="ca.crt")


@app.get("/api/mobile")
def mobile_status():
    return mobile.status()


@app.post("/api/mobile/enable")
def mobile_enable(payload: dict = None):
    """一键启用手机访问：自动生成证书（如需）+ 启动 HTTPS 通道。"""
    try:
        port = int((payload or {}).get("port") or 8443)
        return mobile.start(port=port)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, str(e))


@app.post("/api/mobile/disable")
def mobile_disable():
    return mobile.stop()


app.mount("/static", StaticFiles(directory=str(WEB)), name="static")

# 题目配图静态资源（本地）
_MEDIA_DIR = config.materials_dir() / "question-bank" / "images"
_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_MEDIA_DIR)), name="media")

"""会话编排：出题 → 作答(ASR) → 即时反馈 → 追问 → 收场深评。

说明：会话状态暂存在内存（单用户桌面场景足够）；所有记录实时落盘到
data/sessions/<sid>.jsonl，服务重启后旧会话不能继续作答但记录可查。
"""
import json
import time
from pathlib import Path

from . import asr, config, metrics, prompts, store
from .llm import get_llm

_STATE: dict = {}


def _load_or_raise(sid: str) -> dict:
    if sid not in _STATE:
        raise KeyError("会话不在内存中（服务重启后请开新会话；旧记录仍在 data/sessions/）")
    return _STATE[sid]


def _persona(st: dict) -> dict:
    return prompts.load_persona(st["persona"])


def _current_question(st: dict):
    if st["pending_followup"]:
        return st["pending_followup"], True
    if st["idx"] < len(st["questions"]):
        return st["questions"][st["idx"]]["text"], False
    return None, False


def _state_payload(st: dict) -> dict:
    q, fu = _current_question(st)
    meta = {}
    if not fu and st["idx"] < len(st["questions"]):
        meta = st["questions"][st["idx"]] or {}
    return {
        "sid": st["sid"],
        "persona": st["persona"],
        "persona_title": st["persona_title"],
        "set": st["set"],
        "idx": st["idx"],
        "total": len(st["questions"]),
        "question": q,
        "is_followup": fu,
        "round": meta.get("round"),
        "category": meta.get("category"),
        "intent": meta.get("intent"),
        "hint": meta.get("hint"),
        "done": st["idx"] >= len(st["questions"]) and not fu,
    }


def start(persona_key: str, set_key: str, start_idx: int = 0) -> dict:
    persona = prompts.load_persona(persona_key)
    qset = prompts.load_question_set(set_key)
    questions = qset.get("questions") or []
    if not questions:
        raise ValueError("empty question set")
    start_idx = max(0, min(int(start_idx or 0), len(questions) - 1))
    sid = store.new_session_id()
    st = {
        "sid": sid,
        "persona": persona_key,
        "persona_title": persona["title"],
        "set": set_key,
        "questions": questions,
        "idx": start_idx,
        "followups_done": 0,
        "pending_followup": None,
        "answers": [],
        "started": time.time(),
    }
    store.append(
        sid,
        {"type": "meta", "session": sid, "persona": persona_key, "persona_title": persona["title"], "set": set_key, "n_questions": len(questions)},
    )
    _STATE[sid] = st
    return _state_payload(st)


def get_suggestion(sid: str, refresh: bool = False) -> dict:
    """为当前问题生成/取回「定制版 + 通用版」示范答案（缓存 + 落盘 + 泄漏/长度检测重试）。"""
    import json
    import re

    st = _load_or_raise(sid)
    qtext, is_fu = _current_question(st)
    if not qtext:
        raise ValueError("no active question")

    def _ok(t: str, max_words: int) -> bool:
        """粗筛：排除思考草稿/任务复述/超长答案/naive 腔；方括号占位符（通用版）按允许处理。"""
        t = (t or "").strip()
        if len(t) < 40:
            return False
        core = re.sub(r"\[[^\]]*\]", "", t)
        if any("\u4e00" <= c <= "\u9fff" for c in core):
            return False  # 英文答案中混入中文 → 泄漏
        low = core.lower()
        bad = ("候选人资料", "无 markdown", "任务说明", "任务要求",
               "i need to write", "let me think", "the user wants", "need produce", "we should produce")
        if any(b in low for b in bad):
            return False
        naive = ("very passionate about", "passionate about your company", "i will work hard",
                 "i want to learn a lot", "great company", "quick learner",
                 "thank you for the question", "that's a great question", "hard worker")
        if any(b in low for b in naive):
            return False  # naive 腔：空洞热情 / 学生腔 / 客套铺垫
        return len(re.findall(r"[A-Za-z']+", core)) <= max_words

    key = f"{st['idx']}:{'f' if is_fu else 'q'}"
    sug = st.setdefault("suggestions", {})
    if isinstance(sug.get(key), str):  # 兼容旧内存缓存
        sug[key] = {"personal": "", "generic": sug[key]}
    if refresh or key not in sug:
        profile = prompts.load_profile()
        ptitle = st.get("persona_title") or ""
        result = None
        msgs = prompts.suggestion_messages(qtext, profile, ptitle)
        for _ in range(3):
            try:
                obj = get_llm().chat_json(msgs, temperature=0.6, max_tokens=1600)
            except Exception:
                obj = None
            if isinstance(obj, dict):
                personal = str(obj.get("personal") or "").strip() if profile else ""
                generic = str(obj.get("generic") or "").strip()
                ok_p = _ok(personal, 125) if profile else True
                if ok_p and _ok(generic, 105):
                    result = {"personal": personal, "generic": generic}
                    break
            msgs = prompts.suggestion_messages(qtext, profile, ptitle) + [
                {"role": "assistant", "content": json.dumps(obj or {}, ensure_ascii=False)[:1200]},
                {"role": "user", "content": "不合格。要求：JSON 对象（含 \"generic\"；有个人资料时另含 \"personal\"）；纯英文、精炼（generic ≤95 词、personal ≤110 词）、口语化、不复述任务说明、不含中文；严禁空洞热情与学生腔（如 passionate about your company / learn a lot / work hard / great company）。请重写。"},
            ]
        if result is None:
            raise ValueError("示范答案生成异常，请点「换一版」重试")
        sug[key] = result
        store.append(sid, {"type": "suggestion", "q_key": key, "question": qtext,
                           "text": result["personal"], "generic": result["generic"]})
    return {"personal": sug[key].get("personal") or None, "generic": sug[key]["generic"], "q_key": key}


def get_state(sid: str) -> dict:
    return _state_payload(_load_or_raise(sid))


def submit_answer(sid: str, audio_path: Path, mode: str = "free", script: str = "") -> dict:
    st = _load_or_raise(sid)
    qtext, is_fu = _current_question(st)
    if not qtext:
        raise ValueError("no active question")
    mode = mode if mode in ("free", "read") else "free"
    script = (script or "").strip()[:4000]
    asr_res = asr.transcribe(audio_path)
    transcript = asr_res.get("text") or ""
    met = metrics.compute(transcript, asr_res.get("duration_ms") or 0, asr_res.get("sentences") or [])
    sd = metrics.script_diff(transcript, script) if (mode == "read" and script) else None
    # 反馈生成：失败时降级为「显式报错」而不是整个请求失败
    # （否则前端只弹 2 秒 toast，用户会以为"没有反馈、直接跳下一题"）
    # v0.15.12：新增反馈对象校验——模型返回空对象 / 非对象时同样显式报错并记录原始输出，
    # 杜绝前端渲染出"看起来什么都没有、点了也没反应"的空白卡片。
    fb = None
    fb_error = None
    fb_raw = None
    try:
        fb = get_llm().chat_json(
            prompts.feedback_messages(
                _persona(st),
                qtext,
                transcript,
                [{"question": a["question"], "transcript": a["transcript"]} for a in st["answers"]],
                mode=mode,
                script=script if mode == "read" else "",
            )
        )
        if isinstance(fb, list) and len(fb) == 1 and isinstance(fb[0], dict):
            fb = fb[0]  # 兼容个别服务把对象包在单元素数组里
        if fb is not None and not isinstance(fb, dict):
            fb_raw = json.dumps(fb, ensure_ascii=False)[:800]
            fb_error = f"模型返回的不是 JSON 对象（{type(fb).__name__}）；原始输出已记录（可发给开发者排查）"
            fb = None
        elif isinstance(fb, dict) and not any(
            fb.get(k) for k in ("verdict", "content_gap", "polished", "score", "language_point", "upgrade")
        ):
            fb_raw = json.dumps(fb, ensure_ascii=False)[:800]
            fb_error = "模型返回了空的反馈对象（没有任何内容字段）；原始输出已记录（可发给开发者排查）"
            fb = None
    except Exception as e:  # noqa: BLE001
        fb_error = str(e)[:400] or f"{e.__class__.__name__}（无详细信息）"
    if fb_error:
        store.append(sid, {"type": "feedback_error", "session": sid, "question": qtext,
                           "error": fb_error, "raw": fb_raw})
    rec = {
        "type": "answer",
        "session": sid,
        "n": len(st["answers"]) + 1,
        "question": qtext,
        "is_followup": is_fu,
        "mode": mode,
        "script": script if mode == "read" else "",
        "script_diff": sd,
        "transcript": transcript,
        "duration_ms": asr_res.get("duration_ms"),
        "metrics": met,
        "feedback": fb,
        "feedback_error": fb_error,
        "feedback_raw": fb_raw,
        "asr_driver": asr_res.get("driver"),
        "asr_usage": asr_res.get("usage"),
    }
    st["answers"].append(rec)
    store.append(sid, rec)
    # 错题本
    entries = []
    for key, default_type in (("language_point", "grammar"), ("upgrade", "vocab")):
        item = (fb or {}).get(key)
        if isinstance(item, dict) and item.get("original") and item.get("better"):
            entries.append(
                {
                    "session": sid,
                    "type": item.get("type") or default_type,
                    "original": item.get("original"),
                    "correction": item.get("better"),
                    "note": item.get("explain", ""),
                    "source": key,
                }
            )
    if entries:
        store.append_errorbook(entries)
    # 追问判定
    fu_next = (fb or {}).get("followup")
    followup_max = int(config.get("session.followup_max", 1))
    if (not is_fu) and fu_next and st["followups_done"] < followup_max and len(transcript.split()) >= 12:
        st["pending_followup"] = fu_next
        st["followups_done"] += 1
    else:
        st["pending_followup"] = None
        st["idx"] += 1
    return {"transcript": transcript, "metrics": met, "script_diff": sd, "feedback": fb, "feedback_error": fb_error, "state": _state_payload(st)}


def skip_current(sid: str) -> dict:
    st = _load_or_raise(sid)
    if st["pending_followup"]:
        st["pending_followup"] = None
    else:
        st["idx"] += 1
    return _state_payload(st)


def end(sid: str) -> dict:
    st = _load_or_raise(sid)
    if not st["answers"]:
        raise ValueError("还没有任何回答，无法复盘")
    review = get_llm().chat_json(prompts.review_messages(_persona(st), st["answers"]), temperature=0.3, max_tokens=3000)
    store.append(sid, {"type": "review", "review": review})
    report_path = export_report(sid)
    st["ended"] = True
    return {"review": review, "report": str(report_path)}


def export_report(sid: str) -> Path:
    recs = store.load_records(sid)
    meta = next((r for r in recs if r.get("type") == "meta"), {})
    answers = [r for r in recs if r.get("type") == "answer"]
    review = next((r.get("review") for r in recs if r.get("type") == "review"), None)
    lines = [
        f"# 会话报告 · {sid}",
        "",
        f"- 考官人格: {meta.get('persona_title', meta.get('persona'))}",
        f"- 题集: {meta.get('set')} · 作答 {len(answers)} 条",
    ]
    wpm = [a["metrics"]["wpm"] for a in answers if a.get("metrics", {}).get("wpm")]
    fill = [a["metrics"]["fillers"] for a in answers if a.get("metrics")]
    if wpm:
        lines.append(f"- 平均语速: {sum(wpm) / len(wpm):.0f} wpm · 填充词合计: {sum(fill)}")
    lines.append("")
    for a in answers:
        m = a.get("metrics", {})
        lines += [
            f"## {a['n']}. {a['question']}",
            "",
            f"> {a['transcript']}",
            "",
            f"- 用时 {m.get('duration_s', 0)}s · {m.get('wpm', 0)} wpm · 填充词 {m.get('fillers', 0)} · 长停顿(≥2s) {m.get('long_pauses', 0)}",
            f"- 反馈: {(a.get('feedback') or {}).get('verdict', '') or ('（本轮反馈生成失败）' if a.get('feedback_error') else '')}",
            "",
        ]
    if review:
        lines += ["## 复盘", ""]
        sc = review.get("scores") or {}
        if sc:
            lines.append("评分: " + " · ".join(f"{k} {v}/5" for k, v in sc.items()))
            lines.append("")
        for s in review.get("strengths", []):
            lines.append(f"- 优点: {s}")
        for i in review.get("issues", []):
            lines.append(f"- 问题: [{i.get('type')}] {i.get('pattern')} | 例: {i.get('example', '')} | 改法: {i.get('fix')}")
        for d in review.get("drills", []):
            lines.append(f"- 练习: {d}")
        if review.get("next_focus"):
            lines.append("")
            lines.append(f"**下次重点**: {review['next_focus']}")
    out_dir = config.data_dir() / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"{sid}.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------- 单词速查

_GLOSS_CACHE = None


def gloss(word: str, context: str = "") -> dict:
    """单词速查（LLM 生成 + 本地缓存 data/gloss_cache.json）。"""
    import json

    w = (word or "").strip().strip(".,!?;:\"'()[]").lower()[:40]
    if not w:
        raise ValueError("empty word")
    global _GLOSS_CACHE
    if _GLOSS_CACHE is None:
        try:
            _GLOSS_CACHE = json.loads((config.data_dir() / "gloss_cache.json").read_text(encoding="utf-8"))
        except Exception:
            _GLOSS_CACHE = {}
    if w in _GLOSS_CACHE:
        return _GLOSS_CACHE[w]
    obj = get_llm().chat_json(prompts.gloss_messages(w, context), temperature=0.2, max_tokens=600)
    _GLOSS_CACHE[w] = obj
    try:
        (config.data_dir() / "gloss_cache.json").write_text(
            json.dumps(_GLOSS_CACHE, ensure_ascii=False, indent=1), encoding="utf-8"
        )
    except Exception:
        pass
    return obj

"""语音识别：云端（可配置端点）/ 本地 mlx-whisper 兜底。

云端支持两种协议（自动识别，端点含 /audio/transcriptions 走 OpenAI 兼容）：
  A) wand 系（如腾讯云 TokenHub）：
     POST {asr.endpoint}  入参 {model, data(音频base64), source, voice_encode_format}
     出参 output.{text, duration_ms, sentences:[{begin_ms,end_ms,text}], source}
  B) OpenAI 兼容（OpenAI / 硅基流动 / 百炼等）：
     POST {asr.endpoint}  multipart（file=音频, model=...）→ 出参 {text, ...}
端点留空时自动使用本地模型（auto / local）。
Key：使用「语音服务 Key」（SPEECH_API_KEY），未配置时复用对话 Key。
"""
import base64
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import requests

from . import config


class ASRError(RuntimeError):
    pass


def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise ASRError(f"cmd failed: {' '.join(cmd)}\n{(p.stderr or '')[:400]}")


def to_wav(src: Path) -> Path:
    """浏览器录音（webm/mp4/…）→ 16k 单声道 wav。"""
    dst = config.make_temp_dir("asr_") / "audio.wav"  # 临时文件放软件目录内（transcribe 结束后自动清理）
    ff = config.ffmpeg_path()
    if not (shutil.which(ff) or Path(ff).exists()):
        raise ASRError(f"ffmpeg 不可用: {ff}")
    _run([ff, "-y", "-i", str(src), "-ar", "16000", "-ac", "1", "-f", "wav", str(dst)])
    return dst


def _wav_duration_ms(p: Path) -> int:
    try:
        with wave.open(str(p), "rb") as w:
            return int(w.getnframes() / w.getframerate() * 1000)
    except Exception:
        return 0


def _protocol() -> str:
    """协议判定：显式配置优先；否则按端点特征自动识别。"""
    p = str(config.get("asr.protocol", "auto") or "auto").lower()
    if p in ("wand", "openai"):
        return p
    ep = str(config.get("asr.endpoint", "") or "").lower()
    return "openai" if "/audio/transcription" in ep else "wand"


def transcribe_cloud(wav: Path, model: str = None) -> dict:
    endpoint = config.get("asr.endpoint", "")
    if not endpoint:
        raise ASRError("未配置云端 ASR 接口地址（asr.endpoint）")
    model = model or config.get("asr.model") or ""
    if not model:
        raise ASRError("未配置云端识别模型名（asr.model）")
    key = config.speech_key()
    b64 = base64.b64encode(wav.read_bytes()).decode()
    r = requests.post(
        endpoint,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        json={
            "model": model,
            "data": b64,
            "source": config.get("asr.source", "en"),
            "voice_encode_format": "wav",
        },
        timeout=config.get("asr.timeout_s", 180),
    )
    if r.status_code != 200:
        raise ASRError(f"ASR HTTP {r.status_code}: {r.text[:300]}")
    j = r.json()
    out = j.get("output") or {}
    return {
        "driver": "cloud",
        "text": (out.get("text") or "").strip(),
        "duration_ms": out.get("duration_ms") or _wav_duration_ms(wav),
        "sentences": out.get("sentences") or [],
        "source": out.get("source"),
        "usage": j.get("usage"),
        "model": model,
    }


def transcribe_openai(wav: Path, model: str = None) -> dict:
    """OpenAI 兼容的 /audio/transcriptions（multipart 上传）。"""
    endpoint = config.get("asr.endpoint", "")
    if not endpoint:
        raise ASRError("未配置云端 ASR 接口地址（asr.endpoint）")
    model = model or config.get("asr.model") or ""
    if not model:
        raise ASRError("未配置云端识别模型名（asr.model）")
    key = config.speech_key()
    data = {"model": model, "response_format": "json"}
    lang = str(config.get("asr.source", "") or "").strip()
    if lang:
        data["language"] = lang
    with open(wav, "rb") as f:
        r = requests.post(
            endpoint,
            headers={"Authorization": "Bearer " + key},
            files={"file": ("audio.wav", f, "audio/wav")},
            data=data,
            timeout=config.get("asr.timeout_s", 180),
        )
    if r.status_code != 200:
        raise ASRError(f"ASR HTTP {r.status_code}: {r.text[:300]}")
    j = r.json()
    sentences = []
    for s in j.get("segments") or []:
        try:
            sentences.append({
                "begin_ms": int(float(s.get("start", 0)) * 1000),
                "end_ms": int(float(s.get("end", 0)) * 1000),
                "text": (s.get("text") or "").strip(),
            })
        except Exception:  # noqa: BLE001
            continue
    return {
        "driver": "cloud",
        "text": (j.get("text") or "").strip(),
        "duration_ms": _wav_duration_ms(wav),
        "sentences": sentences,
        "source": j.get("language") or config.get("asr.source", "en"),
        "usage": j.get("usage"),
        "model": model,
    }


def transcribe_local(wav: Path) -> dict:
    try:
        import mlx_whisper  # type: ignore
    except Exception as e:
        raise ASRError(f"本地 ASR 不可用（未安装 mlx-whisper）: {e}")
    model = config.get("asr.local_model", "mlx-community/whisper-large-v3-turbo")
    try:
        res = mlx_whisper.transcribe(str(wav), path_or_hf_repo=model, language="en")
    except Exception:
        model = config.get("asr.local_fallback_model", "mlx-community/whisper-small")
        res = mlx_whisper.transcribe(str(wav), path_or_hf_repo=model, language="en")
    segs = res.get("segments") or []
    sentences = [
        {
            "begin_ms": int(s.get("start", 0) * 1000),
            "end_ms": int(s.get("end", 0) * 1000),
            "text": (s.get("text") or "").strip(),
        }
        for s in segs
    ]
    return {
        "driver": "local",
        "text": (res.get("text") or "").strip(),
        "duration_ms": _wav_duration_ms(wav),
        "sentences": sentences,
        "source": "en",
        "usage": None,
        "model": model,
    }


def transcribe(audio_path) -> dict:
    """driver=auto：云端逐个模型尝试 → 本地兜底（仅 macOS 提供）。"""
    import sys

    driver = config.get("asr.driver", "auto")
    wav = to_wav(Path(audio_path))
    try:
        errors = []
        if driver in ("auto", "cloud"):
            models = [m for m in [config.get("asr.model")] + list(config.get("asr.fallback_models") or []) if m]
            if not models:
                errors.append("云识别未配置模型（asr.model）")
            proto = _protocol()
            for m in models:
                try:
                    if proto == "openai":
                        return transcribe_openai(wav, model=m)
                    return transcribe_cloud(wav, model=m)
                except Exception as e:  # noqa: BLE001
                    errors.append(f"云识别失败/{m}: {e}")
        if driver in ("auto", "local"):
            if sys.platform != "darwin":
                errors.append("本地识别不可用：mlx-whisper 仅支持 macOS")
            else:
                try:
                    return transcribe_local(wav)
                except Exception as e:  # noqa: BLE001
                    errors.append(f"local: {e}")
        msg = " | ".join(errors)
        if driver in ("auto", "cloud") and not config.get("asr.endpoint", ""):
            msg += "。请在「⚙️ 设置 → 语音服务」填入识别接口地址与模型"
        raise ASRError(msg)
    finally:
        shutil.rmtree(wav.parent, ignore_errors=True)

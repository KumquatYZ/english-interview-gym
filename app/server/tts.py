"""文本转语音：云端 TTS（可配置端点）/ macOS say 兜底（零成本）。

云端支持两种协议（自动识别，端点含 /audio/speech 走 OpenAI 兼容）：
  A) minimax 系（MiniMax 官方 / 腾讯云 TokenHub 等）POST {tts.endpoint}：
     入参 {model, text, voice_setting:{voice_id,...}, audio_setting:{format:'mp3'}, output_format:'hex'}
     出参 data.audio（hex 音频；若 output_format=url 则为临时链接）
  B) OpenAI 兼容（OpenAI / 硅基流动等）POST {tts.endpoint}：
     入参 {model, input, voice, response_format:'mp3'} → 返回音频二进制
Key：使用「语音服务 Key」（SPEECH_API_KEY），未配置时复用对话 Key。
"""
import base64
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

from . import config


class TTSError(RuntimeError):
    pass


_EMOJI_RE = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D\u20E3\u2122\u2139]+")


def _clean_for_speech(text: str) -> str:
    """去掉不朗读的装饰：markdown 记号、列表符号、emoji（避免 TTS 读出星号/符号音）。"""
    t = text.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
    t = re.sub(r"(?m)^\s*#{1,6}\s*", "", t)
    t = re.sub(r"(?m)^\s*[-*•·]\s+", "", t)
    t = _EMOJI_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _cache_path(text: str, tag: str) -> Path:
    h = hashlib.md5((tag + "|" + text).encode("utf-8")).hexdigest()[:16]
    d = config.data_dir() / "audio" / "tts_cache"
    d.mkdir(parents=True, exist_ok=True)
    return d / f"{h}.mp3"


def synth_say(text: str) -> bytes:
    voice = config.get("tts.say_voice", "Samantha")
    rate = int(config.get("tts.say_rate", 170))
    tmp = config.make_temp_dir("tts_")  # 临时文件放软件目录内，用完即清
    try:
        aiff, mp3 = tmp / "a.aiff", tmp / "a.mp3"
        p = subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), text], capture_output=True, text=True)
        if p.returncode != 0 or not aiff.exists():
            # 音色不存在时退回系统默认音色
            subprocess.run(["say", "-r", str(rate), "-o", str(aiff), text], check=True, capture_output=True)
        subprocess.run(
            [config.ffmpeg_path(), "-y", "-i", str(aiff), "-codec:a", "libmp3lame", "-qscale:a", "4", str(mp3)],
            check=True,
            capture_output=True,
        )
        return mp3.read_bytes()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _protocol() -> str:
    """协议判定：显式配置优先；否则按端点特征自动识别。"""
    p = str(config.get("tts.protocol", "auto") or "auto").lower()
    if p in ("minimax", "openai"):
        return p
    ep = str(config.get("tts.endpoint", "") or "").lower()
    return "openai" if "/audio/speech" in ep else "minimax"


def synth_cloud(text: str, voice_id: str = None) -> bytes:
    endpoint = config.get("tts.endpoint", "")
    if not endpoint:
        raise TTSError("未配置云端 TTS 接口地址（tts.endpoint）")
    key = config.speech_key()
    r = requests.post(
        endpoint,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        json={
            "model": config.get("tts.cloud_model", ""),
            "text": text,
            "voice_setting": {
                "voice_id": voice_id or config.get("tts.cloud_voice_id", ""),
                "speed": 1.0,
            },
            "audio_setting": {"format": "mp3", "sample_rate": 32000, "bitrate": 128000, "channel": 1},
            "output_format": "hex",
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise TTSError(f"TTS HTTP {r.status_code}: {r.text[:300]}")
    j = r.json()
    d = j.get("data") or j
    audio = d.get("audio") or ""
    if isinstance(audio, str) and audio.startswith("http"):
        return requests.get(audio, timeout=120).content
    if not audio:
        raise TTSError(f"TTS 返回无音频字段: {str(j)[:300]}")
    return bytes.fromhex(audio)


def synth_openai(text: str, voice_id: str = None) -> bytes:
    """OpenAI 兼容的 /audio/speech（返回音频二进制）。"""
    endpoint = config.get("tts.endpoint", "")
    if not endpoint:
        raise TTSError("未配置云端 TTS 接口地址（tts.endpoint）")
    key = config.speech_key()
    r = requests.post(
        endpoint,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        json={
            "model": config.get("tts.cloud_model", ""),
            "input": text,
            "voice": voice_id or config.get("tts.cloud_voice_id", ""),
            "response_format": "mp3",
        },
        timeout=120,
    )
    if r.status_code != 200:
        raise TTSError(f"TTS HTTP {r.status_code}: {r.text[:300]}")
    if r.headers.get("Content-Type", "").startswith("audio") or len(r.content) > 4096:
        return r.content
    # 少数兼容服务用 JSON 返回（hex / base64 音频）
    try:
        j = r.json()
    except Exception as e:  # noqa: BLE001
        raise TTSError(f"TTS 返回无法识别的音频: {r.text[:200]}") from e
    d = j.get("data") if isinstance(j.get("data"), dict) else j
    a = (d.get("audio") if isinstance(d, dict) else None) or j.get("audio") or ""
    if isinstance(a, str) and a.startswith("http"):
        return requests.get(a, timeout=120).content
    if a:
        try:
            return bytes.fromhex(a)
        except ValueError:
            return base64.b64decode(a)
    raise TTSError(f"TTS 返回无音频字段: {str(j)[:300]}")


def synth(text: str, persona: str = None) -> bytes:
    text = _clean_for_speech((text or "").strip())
    if not text:
        raise TTSError("empty text")
    driver = config.get("tts.driver", "macos_say")
    voice_id = None
    if persona:
        voice_id = (config.get("tts.voices") or {}).get(persona)
    tag = f"{driver}|{voice_id or config.get('tts.cloud_voice_id', '') or config.get('tts.say_voice', '')}"
    cache = _cache_path(text, tag)
    if config.get("tts.cache", True) and cache.exists():
        return cache.read_bytes()
    if driver == "cloud":
        try:
            if _protocol() == "openai":
                data = synth_openai(text, voice_id=voice_id)
            else:
                data = synth_cloud(text, voice_id=voice_id)
        except Exception as e:  # noqa: BLE001
            if sys.platform == "darwin":
                data = synth_say(text)  # macOS：云端异常时用 say 兜底
            else:
                raise TTSError(f"云端语音合成失败：{e}") from e
    else:
        data = synth_say(text)
    if config.get("tts.cache", True):
        cache.write_bytes(data)
    return data

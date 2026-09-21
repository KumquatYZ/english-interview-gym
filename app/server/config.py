"""配置加载：config.yaml + .env（+ config.local.yaml 用户覆盖）。

两种运行形态：
- 源码运行（macOS / 仓库模式）：app/config.yaml、app/.env、app/config.local.yaml（可选）
- 打包运行（Windows 免安装版）：以上文件都放在 exe 旁边（可写）；
  首次启动时从打包资源里释放默认 materials/ 与 config.yaml。
用户设置通过「⚙️ 设置」界面写入 config.local.yaml 与 .env —— 不会覆盖带注释的主配置。
"""
import os
import shutil
import sys
from pathlib import Path

import yaml


def _is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


if _is_frozen():
    ROOT = Path(sys.executable).resolve().parent          # exe 所在目录（可写：配置/数据/素材都在这）
    BUNDLE = Path(getattr(sys, "_MEIPASS", str(ROOT)))    # 打包内资源（只读）
else:
    ROOT = Path(__file__).resolve().parents[2]            # 仓库根（EngTraining/）
    BUNDLE = ROOT

_ENV = {}
_CFG = None


def is_frozen() -> bool:
    return _is_frozen()


def root_dir() -> Path:
    return ROOT


def _cfg_path() -> Path:
    return (ROOT / "config.yaml") if _is_frozen() else (ROOT / "app" / "config.yaml")


def config_local_path() -> Path:
    return (ROOT / "config.local.yaml") if _is_frozen() else (ROOT / "app" / "config.local.yaml")


def env_path() -> Path:
    return (ROOT / ".env") if _is_frozen() else (ROOT / "app" / ".env")


def web_dir() -> Path:
    if _is_frozen():
        return BUNDLE / "app" / "web"
    return ROOT / "app" / "web"


def _release_missing(src: Path, tgt: Path) -> int:
    """把 src 中缺失的文件逐个补到 tgt（不覆盖已存在文件）；返回补入的文件数。"""
    n = 0
    for p in sorted(src.rglob("*")):
        if p.is_dir():
            continue
        dst = tgt / p.relative_to(src)
        if dst.exists():
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
            n += 1
        except Exception:
            continue
    return n


def bootstrap():
    """打包模式启动：把默认 materials/ 与 config.yaml 释放到 exe 旁。

    - materials 目录整体缺失 → 全量释放；
    - 目录已存在（升级时在新包上覆盖解压）→ 逐个补齐缺失文件（新增题库 / 角色会自动出现），
      不覆盖用户已有文件（profile.md、自定义素材、旧题库均保留）；
    - 根 config.yaml 缺失时释放默认（用户设置在 .env / config.local.yaml，不受影响）。
    """
    if not _is_frozen():
        return
    try:
        src = BUNDLE / "materials_default"
        tgt = ROOT / "materials"
        if src.exists():
            if not tgt.exists():
                shutil.copytree(src, tgt)
            else:
                added = _release_missing(src, tgt)
                if added:
                    print(f"[bootstrap] 已补齐 {added} 个新增素材文件到 materials/（升级自动同步）")
        cfg = _cfg_path()
        if not cfg.exists() and (BUNDLE / "app" / "config.yaml").exists():
            shutil.copy(BUNDLE / "app" / "config.yaml", cfg)
        (ROOT / "data").mkdir(exist_ok=True)
    except Exception:
        pass


bootstrap()


def _load_env_file():
    p = env_path()
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        _ENV[k.strip()] = v.strip().strip('"').strip("'")


_load_env_file()


def _deep_merge(base: dict, extra: dict) -> dict:
    out = dict(base or {})
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load():
    global _CFG
    if _CFG is None:
        base = {}
        p = _cfg_path()
        if p.exists():
            try:
                base = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            except Exception:
                base = {}
        if not base and _is_frozen() and (BUNDLE / "app" / "config.yaml").exists():
            try:
                base = yaml.safe_load((BUNDLE / "app" / "config.yaml").read_text(encoding="utf-8")) or {}
            except Exception:
                base = {}
        lp = config_local_path()
        if lp.exists():
            try:
                local = yaml.safe_load(lp.read_text(encoding="utf-8")) or {}
                base = _deep_merge(base, local)
            except Exception:
                pass
        _CFG = base
    return _CFG


def get(path, default=None):
    d = load()
    for part in str(path).split("."):
        if not isinstance(d, dict) or part not in d:
            return default
        d = d[part]
    return d


def save_config(updates: dict):
    """把用户设置写入 config.local.yaml（与主配置深合并；不覆盖主文件注释）。"""
    global _CFG
    lp = config_local_path()
    cur = {}
    if lp.exists():
        try:
            cur = yaml.safe_load(lp.read_text(encoding="utf-8")) or {}
        except Exception:
            cur = {}
    cur = _deep_merge(cur, updates or {})
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(yaml.safe_dump(cur, allow_unicode=True, sort_keys=False), encoding="utf-8")
    _CFG = None


def save_env(updates: dict):
    """更新 .env 中的键（保留其他行与注释）；值为空字符串则删除该键。"""
    global _CFG
    p = env_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    remaining = dict(updates or {})
    out = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in remaining:
                v = (remaining.pop(k) or "").strip()
                if v:
                    out.append(f"{k}={v}")
                continue  # 空值 = 删除该键
        out.append(line)
    for k, v in remaining.items():
        v = (v or "").strip()
        if v:
            out.append(f"{k}={v}")
    p.write_text("\n".join(out).strip() + "\n", encoding="utf-8")
    for k, v in (updates or {}).items():
        v = (v or "").strip()
        if v:
            _ENV[k] = v
        else:
            _ENV.pop(k, None)
    _CFG = None


def env(name, default=None):
    """进程环境变量优先，其次 .env 文件。"""
    return os.environ.get(name) or _ENV.get(name) or default


def api_key():
    return env("API_KEY", "")


def speech_key():
    """语音（识别 / 合成）Key：SPEECH_API_KEY 优先；未设置时复用对话 Key（向后兼容）。"""
    return env("SPEECH_API_KEY", "") or api_key()


def data_dir() -> Path:
    d = ROOT / get("paths.data_dir", "data")
    d.mkdir(parents=True, exist_ok=True)
    return d


def make_temp_dir(prefix: str = "tmp_") -> Path:
    """在软件数据目录内创建临时工作目录（用完请自行 rmtree）。

    保证所有中间文件都落在软件目录内，不向系统 C 盘临时目录写入。
    """
    import tempfile

    base = data_dir() / "tmp"
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=prefix, dir=str(base)))


def materials_dir() -> Path:
    return ROOT / get("paths.materials_dir", "materials")


def ffmpeg_path() -> str:
    p = get("tools.ffmpeg") or "ffmpeg"
    if isinstance(p, str) and p != "ffmpeg" and Path(p).exists():
        return p
    if _is_frozen():
        try:
            import imageio_ffmpeg  # 打包内置的静态 ffmpeg（Windows 免安装版）

            return imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass
    return p

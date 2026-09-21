# -*- coding: utf-8 -*-
"""免安装版入口：本地服务 + 原生应用窗口（无控制台黑框）。

- 数据/配置/素材都放在程序旁边的文件夹（首启自动释放默认素材）。
- Windows 优先用系统自带 WebView2 内核打开独立应用窗口（pywebview）；
  不可用时退回 Edge/Chrome 独立窗口，再退回默认浏览器。
- 关闭应用窗口 = 停止服务；也可在页面「⚙️ 设置 → 完全退出程序」退出。
- 若检测到服务已在运行，则直接打开界面，不重复启动。
"""
import os
import socket
import sys
import threading
import time
import traceback
from pathlib import Path

APP_TITLE = "英语面试健身房"
PORT_PREFERRED = 8765

_SERVER = None          # uvicorn.Server（由 _main 注入）
_QUIT = threading.Event()


def _app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent  # 源码运行：仓库根目录


def _setup_streams() -> None:
    """windowed 模式下 stdout/stderr 为 None：接到日志文件，避免 print 崩溃。"""
    try:
        logdir = _app_root() / "logs"
        logdir.mkdir(parents=True, exist_ok=True)
        f = open(logdir / "app.log", "a", buffering=1, encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        f = open(os.devnull, "w")
    if sys.stdout is None:
        sys.stdout = f
    if sys.stderr is None:
        sys.stderr = f
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass


def _pick_port(preferred: int = PORT_PREFERRED) -> int:
    for p in range(preferred, preferred + 20):
        try:
            with socket.socket() as s:
                s.bind(("127.0.0.1", p))
                return p
        except OSError:
            continue
    return preferred


def _probe(port: int = PORT_PREFERRED) -> bool:
    try:
        import urllib.request

        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1.5) as r:
            return 200 <= r.status < 300
    except Exception:  # noqa: BLE001
        return False


def _wait_ready(port: int, timeout: float = 40.0) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout:
        if _probe(port):
            return True
        time.sleep(0.4)
    return False


def _request_quit() -> None:
    global _SERVER
    try:
        if _SERVER is not None:
            _SERVER.should_exit = True
    except Exception:  # noqa: BLE001
        pass
    # 关闭原生窗口（若以窗口方式启动）→ 让 webview.start() 返回、主线程继续收尾
    try:
        import webview as _wv

        for w in list(getattr(_wv, "windows", None) or []):
            try:
                w.destroy()
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass
    _QUIT.set()
    # 兜底：3.5 秒后仍未退出（例如窗口销毁失败）则强制结束进程
    def _force() -> None:
        time.sleep(3.5)
        os._exit(0)

    threading.Thread(target=_force, daemon=True).start()


def _message_box(text: str) -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.user32.MessageBoxW(None, text, APP_TITLE, 0x40)
    except Exception:  # noqa: BLE001
        pass


def _open_native_window(url: str) -> bool:
    """pywebview 原生窗口（Windows 走 WebView2）。阻塞直到窗口关闭；不可用返回 False。"""
    try:
        import webview
    except Exception as e:  # noqa: BLE001
        print(f"[launcher] 原生窗口不可用（无 pywebview）：{e!r}")
        return False
    try:
        w = webview.create_window(
            APP_TITLE,
            url,
            width=1200,
            height=840,
            min_size=(980, 640),
            text_select=True,
        )
        w.events.closed += _request_quit
        # WebView2 用户数据（缓存 / Cookies）固定放在软件目录内：
        # 保证「删除程序文件夹 = 完全清除环境」，不向 C 盘用户目录写入任何数据。
        try:
            storage = _app_root() / "webview_data"
            storage.mkdir(parents=True, exist_ok=True)
            webview.start(debug=False, storage_path=str(storage))
        except TypeError:
            webview.start(debug=False)  # 旧版 pywebview 不支持 storage_path 时兜底
        return True
    except Exception as e:  # noqa: BLE001
        print(f"[launcher] 原生窗口启动失败：{e!r}")
        return False


def _open_external(url: str) -> str:
    """兜底：Edge/Chrome 独立应用窗 > 默认浏览器。返回描述字符串。"""
    if sys.platform == "win32":
        import shutil
        import subprocess

        cands = []
        for exe in ("msedge", "chrome"):
            p = shutil.which(exe)
            if p:
                cands.append(p)
        cands += [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        for p in cands:
            if p and os.path.exists(p):
                try:
                    subprocess.Popen([p, f"--app={url}"], close_fds=True)
                    return f"已用独立窗口打开：{p}"
                except Exception:  # noqa: BLE001
                    continue
    import webbrowser

    webbrowser.open(url)
    return "已在默认浏览器打开"


def main() -> None:
    _setup_streams()
    try:
        _main()
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        _message_box("程序启动失败。详情见 logs/app.log。")
        sys.exit(1)


def _main() -> None:
    global _SERVER

    if _probe():
        # 已在运行：直接打开界面
        if not _open_native_window(f"http://127.0.0.1:{PORT_PREFERRED}"):
            _open_external(f"http://127.0.0.1:{PORT_PREFERRED}")
        return

    from server.main import app  # noqa: E402  （导入即完成配置/素材引导）
    import uvicorn  # noqa: E402

    port = _pick_port()
    url = f"http://127.0.0.1:{port}"
    cfg = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", access_log=False)
    _SERVER = uvicorn.Server(cfg)
    app.state.quit_callback = _request_quit

    print("=" * 58)
    print(f"  {APP_TITLE} · 本地服务已启动：{url}")
    print("=" * 58)

    threading.Thread(target=_SERVER.run, name="gym-server", daemon=True).start()
    if not _wait_ready(port):
        _message_box("服务启动超时，请查看 logs/app.log。")
        sys.exit(1)

    if _open_native_window(url):
        _request_quit()  # 窗口关闭 → 收尾退出
    else:
        how = _open_external(url)
        print(f"[launcher] {how}")
        _message_box(
            f"界面已在浏览器打开（{url}）。\n"
            "程序在后台持续运行；如需退出，请在页面「⚙️ 设置」中点击「完全退出程序」。"
        )
        _QUIT.wait()
    time.sleep(0.6)  # 给服务端一点收尾时间
    print("[launcher] 已退出")
    sys.exit(0)


if __name__ == "__main__":
    main()

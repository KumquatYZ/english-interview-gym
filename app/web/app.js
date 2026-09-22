/* 英语面试健身房 · 前端逻辑（Speakey 式对话体验）
   API：/api/health|personas|question-sets|stats|sessions|favorites|favorite|gloss
        /api/session/start|{sid}|{sid}/suggestion|{sid}/answer|{sid}/skip|{sid}/end|/api/tts */
"use strict";

const TUTORS = {
  "hr-friendly": { emoji: "👩‍💼", en: "Grace", sample: "Hi, I'm Grace. Let's have a friendly chat about your background. Take your time." },
  "tech-lead":   { emoji: "👨‍🔬", en: "Alan",  sample: "Hi, I'm Alan, the hiring manager. I'll dig into the technical details of your work." },
  "stress":      { emoji: "🧔",   en: "Victor", sample: "Let's keep this tight. I'll push back on your answers, that's my job." },
  "meeting-host":{ emoji: "🧑‍💼", en: "Olivia", sample: "Hi, I'm Olivia. Let's get started — I'll hand the floor to you for the first update." },
};
const SETMETA = {
  "baseline-8":    { ico: "📊", desc: "摸底测试 · 覆盖面试全流程" },
  "interview-core":{ ico: "🎯", desc: "面试核心高频 14 题" },
  "mnc-60":        { ico: "🏢", desc: "外企 60 题 · 商务英语深度" },
  "meetings-core":     { ico: "💼", desc: "外企会议通用 16 题 · 周会 / 讨论 / 决策" },
  "cosmetics-meetings":{ ico: "💄", desc: "美妆行业会议 22 题 · 新品 / 渠道 / 合规" },
};

const S = {
  personas: [], sets: [], selPersona: null, selSet: null,
  sid: null, personaKey: "", state: null,
  mode: "free", script: "", sugg: {}, suggOpen: false, suggCard: null,
  rec: null, recState: "idle", recStart: 0, timerId: null, chunks: [],
  phase: "home", maxSec: 120, busy: false,
  autoplayTimer: null, nowPlaying: "",
};

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const player = $("player");

/* ---------------- 基础 ---------------- */
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) {
    let msg = r.status + "";
    try { msg = (await r.json()).detail || msg; } catch (e) {}
    throw new Error(msg);
  }
  return r.json();
}
let toastTimer = null;
function toast(msg) {
  const t = $("toast");
  t.textContent = msg; t.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 2600);
}
function setStatus(msg) { $("status").textContent = msg || ""; }
function showView(name) {
  for (const v of ["home", "chat", "report", "set"]) $(`view-${v}`).classList.toggle("hidden", v !== name);
  S.phase = name;
  stopAudio();  // 离开/切换视图时停掉一切声音
  window.scrollTo(0, 0);
}

/* ---------------- 全局音频（单通道：同一时刻只允许一个声音） ---------------- */
function stopAudio() {
  clearTimeout(S.autoplayTimer); S.autoplayTimer = null;
  S.nowPlaying = "";
  try { player.pause(); } catch (e) {}
  try { player.removeAttribute("src"); player.load(); } catch (e) {}  // 终止挂起的加载与 play()
}
function speak(text, personaKey, btn) {
  if (!text) return;
  const src = `/api/tts?text=${encodeURIComponent(text)}&persona=${encodeURIComponent(personaKey || S.personaKey || "")}`;
  clearTimeout(S.autoplayTimer); S.autoplayTimer = null;  // 取消排队中的自动播放
  if (S.nowPlaying === src && !player.paused) {           // 同一段正在播：再点一次 = 暂停
    try { player.pause(); } catch (e) {}
    S.nowPlaying = "";
    if (btn) btn.classList.remove("playing");
    return;
  }
  try { player.pause(); } catch (e) {}                   // 先掐断上一条（单通道保证）
  player.muted = false;                                   // 解除解锁期可能残留的静音
  player.src = src;
  S.nowPlaying = src;
  if (btn) {
    btn.classList.add("playing");
    setTimeout(() => btn.classList.remove("playing"), 1200);
  }
  player.play().catch(() => {});
}
function scheduleSpeak(text, personaKey, delay) {
  clearTimeout(S.autoplayTimer);
  S.autoplayTimer = setTimeout(() => { S.autoplayTimer = null; speak(text, personaKey); }, delay);
}

/* ---------------- 移动端适配：iOS 音频 / 屏幕常亮 / 触屏文案 ---------------- */
try { if (navigator.audioSession) navigator.audioSession.type = "playback"; } catch (e) {}  // 静音拨片下也能出声
const MIC_HINT = (window.matchMedia && matchMedia("(pointer:coarse)").matches) ? "点击开始录音" : "点击或按空格开始";
try { $("micHint").textContent = MIC_HINT; } catch (e) {}
let _wakeLock = null;
async function keepScreenAwake(on) {
  try {
    if (on) { if ("wakeLock" in navigator && !_wakeLock) _wakeLock = await navigator.wakeLock.request("screen"); }
    else if (_wakeLock) { _wakeLock.release(); _wakeLock = null; }
  } catch (e) { _wakeLock = null; }
}
/* iOS：首次点按解锁 HTMLAudioElement，此后题目语音可自动播放 */
let _audioUnlocked = false;
const SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=";
document.addEventListener("pointerdown", () => {
  if (_audioUnlocked) return;
  _audioUnlocked = true;
  try {
    player.muted = true;
    player.src = SILENT_WAV;
    const pr = player.play();
    const fin = () => {
      player.muted = false;
      if (S.nowPlaying === "") {   // 若解锁动作本身仍占着音频通道，清掉它的 src
        try { player.pause(); player.removeAttribute("src"); player.load(); } catch (e) {}
      }
    };
    if (pr && pr.then) pr.then(fin).catch(fin); else fin();
  } catch (e) { player.muted = false; }
}, { once: true });
/* ---------------- 打卡庆祝（数字滚动 / 彩带 / 连胜里程碑） ---------------- */
function countUp(el, target, dur, decimals) {
  if (!el) return;
  decimals = decimals || 0;
  const t0 = performance.now();
  (function tick(t) {
    const k = Math.min(1, (t - t0) / (dur || 700));
    const e = 1 - Math.pow(1 - k, 3);
    el.textContent = (target * e).toFixed(decimals);
    if (k < 1) requestAnimationFrame(tick);
    else el.textContent = target.toFixed(decimals);
  })(t0);
}
function burstConfetti(n, x, y) {
  const cv = $("confetti");
  if (!cv) return;
  const ctx = cv.getContext("2d");
  cv.width = innerWidth; cv.height = innerHeight;
  const colors = ["#0FA79A", "#FFB25E", "#FF7A3D", "#E5484D", "#FFD84D", "#7C5CD6", "#4CC3E0"];
  const parts = [];
  const wide = n >= 80;  // 大批量 → 全屏散布（里程碑庆祝）
  for (let i = 0; i < n; i++) {
    const ox = wide ? (0.1 + Math.random() * 0.8) * innerWidth : (x == null ? innerWidth / 2 : x);
    const oy = wide ? (0.24 + Math.random() * 0.14) * innerHeight : (y == null ? innerHeight * 0.32 : y);
    const a = -Math.PI / 2 + (Math.random() - 0.5) * 2.7;
    const sp = 3.5 + Math.random() * 9;
    const kind = Math.random();
    parts.push({
      x: ox, y: oy,
      vx: Math.cos(a) * sp * (wide ? 1.2 : 1),
      vy: Math.sin(a) * sp - (wide ? 1.4 : 3.2),
      s: (kind < 0.6 ? 5 + Math.random() * 6 : 3 + Math.random() * 3) + (wide ? 2 : 0),
      long: kind >= 0.78,
      round: kind >= 0.6 && kind < 0.78,
      c: colors[(Math.random() * colors.length) | 0],
      r: Math.random() * Math.PI,
      vr: (Math.random() - 0.5) * 0.36,
      life: 90 + Math.random() * 70,
      sway: Math.random() * Math.PI * 2,
    });
  }
  (function frame() {
    ctx.clearRect(0, 0, cv.width, cv.height);
    let alive = false;
    for (const p of parts) {
      if (p.life <= 0) continue;
      alive = true;
      p.life--; p.vy += 0.2; p.vx *= 0.988;
      p.sway += 0.08;
      p.x += p.vx + Math.sin(p.sway) * (p.long ? 1.4 : 0.5);
      p.y += p.vy; p.r += p.vr;
      ctx.save();
      ctx.translate(p.x, p.y); ctx.rotate(p.r);
      ctx.globalAlpha = Math.min(1, p.life / 45);
      ctx.fillStyle = p.c;
      if (p.round) { ctx.beginPath(); ctx.arc(0, 0, p.s / 2, 0, Math.PI * 2); ctx.fill(); }
      else if (p.long) ctx.fillRect(-p.s / 2, -1.6, p.s, 3.2);
      else ctx.fillRect(-p.s / 2, -p.s / 2, p.s, p.s * 0.62);
      ctx.restore();
    }
    if (alive) requestAnimationFrame(frame);
    else ctx.clearRect(0, 0, cv.width, cv.height);
  })();
}
const STREAK_MILESTONES = [3, 7, 14, 30, 50, 100];
function maybeCelebrate(st) {
  try {
    const seen = parseInt(localStorage.getItem("et_streak_seen") || "0", 10) || 0;
    if (st.streak_days > seen && STREAK_MILESTONES.includes(st.streak_days)) {
      $("celebrateTitle").textContent = `连续 ${st.streak_days} 天！`;
      $("celebrateSub").textContent = st.streak_days >= 30 ? "这已经是习惯级别的坚持，太强了" : "你正在建立可怕的势头，继续保持";
      $("celebrateOverlay").classList.remove("hidden");
      burstConfetti(220);
    }
    if (st.streak_days > seen) localStorage.setItem("et_streak_seen", String(st.streak_days));
    const tk = st.today.date;
    if (st.today.sessions > 0 && localStorage.getItem("et_today_seen") !== tk) {
      localStorage.setItem("et_today_seen", tk);
      toast(`✅ 今日已打卡 · 连续 ${st.streak_days} 天`);
      setTimeout(() => burstConfetti(60), 260);
    }
  } catch (e) {}
}
$("celebrateBtn").addEventListener("click", () => $("celebrateOverlay").classList.add("hidden"));
$("celebrateOverlay").addEventListener("click", (e) => { if (e.target === $("celebrateOverlay")) $("celebrateOverlay").classList.add("hidden"); });
const tutorOf = (key) => TUTORS[key] || { emoji: "🎓", en: "Tutor", sample: "Hello! Ready to practice?" };

/* ---------------- 首页 ---------------- */
async function boot() {
  try {
    const h = await api("/api/health");
    S.maxSec = h.max_answer_seconds || 120;
    $("setupBanner").classList.toggle("hidden", !!h.api_configured);
  } catch (e) {}
  await reloadHome();
}
async function reloadHome() {
  const [personas, sets, stats, sessions, favs] = await Promise.all([
    api("/api/personas"), api("/api/question-sets"), api("/api/stats"), api("/api/sessions"), api("/api/favorites"),
  ]);
  S.personas = personas; S.sets = sets;
  const favN = (favs || []).length;
  $("favOpenBtn").textContent = favN ? `⭐ 收藏夹（${favN}）` : "⭐ 收藏夹";
  $("favOpenBtn2").textContent = favN ? `⭐ 收藏夹（${favN}）` : "⭐ 收藏夹";
  renderCheckin(stats);
  maybeCelebrate(stats);
  revBadgeFrom(stats.review);
  renderTutors();
  renderSets();
  renderRecent(sessions);
  if (!S.selPersona && personas[0]) S.selPersona = personas[0].key;
  if (!S.selSet && sets[0]) S.selSet = sets[0].key;
  syncStart();
}
function renderCheckin(st) {
  const goal = st.daily_goal_minutes || 20;
  const today = st.today || { date: "", sessions: 0, minutes: 0 };
  const done = today.sessions > 0;
  const pct = Math.max(0, Math.min(1, (today.minutes || 0) / goal));
  const R = 30.5, C = 2 * Math.PI * R;
  const days7 = (st.recent_14 || []).slice(-7);
  const maxMin = Math.max(goal, ...days7.map((d) => d.minutes || 0), 1);
  const WD = ["日", "一", "二", "三", "四", "五", "六"];
  const cells = days7.map((d) => {
    const isToday = d.date === today.date;
    const isDone = (d.count || 0) > 0;
    const label = isToday ? "今" : WD[new Date(d.date + "T12:00:00").getDay()];
    const barH = Math.max((d.minutes || 0) > 0 ? 4 : 0, Math.round(((d.minutes || 0) / maxMin) * 26));
    return `<div class="ck-day ${isDone ? "done" : ""} ${isToday ? "today" : ""} ${isToday && !isDone ? "pending" : ""}" title="${d.date} · ${d.minutes || 0} 分钟">
      <span class="dl">${label}</span>
      <span class="cc">${isDone ? "✓" : ""}</span>
      <span class="bar"><i data-h="${barH}"></i></span>
    </div>`;
  }).join("");
  const msg = done
    ? (today.minutes >= goal ? "今天已打卡 · 目标达成 🎉" : `今天已打卡 · 还差 ${Math.max(0, goal - today.minutes).toFixed(0)} 分钟达标`)
    : "今天还没开口，练一局保持连胜";
  const minutesLabel = today.minutes >= 100 ? String(Math.round(today.minutes)) : (today.minutes || 0).toFixed(1).replace(/\.0$/, "");
  const rv = st.review || null;
  const rvLine = rv && rv.goal > 0 ? `<div class="ck-review" id="ckReview" title="点我去复习（按比例随机温故）">
      <span>🔁 今日复习</span><b>${rv.answered}</b><span>/</span><b>${rv.goal}</b><span>词</span>
      ${rv.done ? `<span class="ck-rv-ok">✓ 完成</span>` : `<span class="ck-rv-go">去复习 →</span>`}
    </div>` : "";
  $("statsStrip").innerHTML = `
    <div class="ck-panel">
      <div class="ck-top">
        <div class="ck-flame-wrap ${done ? "lit" : ""}" id="ckFlameWrap" title="点我一下">
          <span class="ck-glow"></span>
          <span class="ck-flame ${done ? "lit" : ""}">🔥</span>
        </div>
        <div class="ck-streak">
          <div><b id="ckStreakNum">0</b><span class="unit">天连续</span></div>
          <span class="msg ${done ? "ok" : ""}">${msg}</span>
        </div>
        <div class="ck-ring" title="今日开口目标 ${goal} 分钟">
          <svg width="74" height="74" viewBox="0 0 74 74">
            <circle class="bg" cx="37" cy="37" r="${R}"/>
            <circle class="fg" cx="37" cy="37" r="${R}" id="ckRing"
              stroke-dasharray="${C.toFixed(1)}" stroke-dashoffset="${C.toFixed(1)}"/>
          </svg>
          <span class="txt">${minutesLabel}<small>/ ${goal} 分钟</small></span>
        </div>
      </div>
      <div class="ck-days">${cells}</div>${rvLine}
      <div class="ck-cards">
        <div class="ck-card"><b data-count="${st.total_sessions}">0</b><span>场训练</span></div>
        <div class="ck-card"><b data-count="${st.total_answers}">0</b><span>题作答</span></div>
        <div class="ck-card"><b data-count="${st.total_minutes}">0</b><span>分钟开口</span></div>
        <div class="ck-card"><b data-count="${st.best_streak || st.streak_days}">0</b><span>最长连胜</span></div>
      </div>
    </div>`;
  countUp($("ckStreakNum"), st.streak_days, 750);
  document.querySelectorAll(".ck-card b[data-count]").forEach((el, i) => {
    setTimeout(() => countUp(el, parseFloat(el.dataset.count) || 0, 700, String(el.dataset.count).includes(".") ? 1 : 0), 80 + i * 90);
  });
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const ring = $("ckRing");
    if (ring) ring.style.strokeDashoffset = (C * (1 - pct)).toFixed(1);
    document.querySelectorAll(".ck-day .bar i").forEach((b) => { b.style.height = (parseInt(b.dataset.h, 10) || 0) + "px"; });
  }));
  const wrap = $("ckFlameWrap");
  if (wrap) wrap.addEventListener("click", () => {
    wrap.style.transform = "scale(1.18)";
    setTimeout(() => { wrap.style.transform = ""; }, 180);
    const r = wrap.getBoundingClientRect();
    burstConfetti(16, r.left + r.width / 2, r.top + r.height / 2);
  });
  const rvEl = $("ckReview");
  if (rvEl) rvEl.addEventListener("click", () => openFavorites("review"));
}
function renderTutors() {
  $("tutorGrid").innerHTML = S.personas.map((p) => {
    const t = tutorOf(p.key);
    return `<div class="tutor-card" data-key="${esc(p.key)}">
      <span class="check">✓</span>
      <div class="avatar">${t.emoji}</div>
      <b>${esc(t.en)}</b>
      <small>${esc(p.title)}</small>
      <button class="mini-btn listen" data-listen="${esc(p.key)}">▶ 试听</button>
    </div>`;
  }).join("");
  $("tutorGrid").querySelectorAll(".tutor-card").forEach((card) => {
    card.addEventListener("click", (e) => {
      if (e.target.closest("[data-listen]")) return;
      S.selPersona = card.dataset.key; renderTutors(); syncStart();
    });
  });
  $("tutorGrid").querySelectorAll("[data-listen]").forEach((b) => {
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      speak(tutorOf(b.dataset.listen).sample, b.dataset.listen, b);
    });
  });
}
function renderSets() {
  $("setList").innerHTML = S.sets.map((s) => {
    const m = SETMETA[s.key] || { ico: "📚", desc: "" };
    return `<button class="set-card" data-key="${esc(s.key)}">
      <span class="ico">${m.ico}</span>
      <span><b>${esc(s.title)}</b><small>${esc(m.desc)}</small></span>
      <span class="count">${s.count} 题</span>
    </button>`;
  }).join("");
  $("setList").querySelectorAll(".set-card").forEach((card) => {
    card.addEventListener("click", () => openSet(card.dataset.key));
  });
}
function renderRecent(sessions) {
  const top = (sessions || []).slice(0, 5);
  if (!top.length) { $("recentList").innerHTML = `<div class="empty">还没有训练记录 — 今天就是第 1 天 💪</div>`; return; }
  $("recentList").innerHTML = top.map((r) => {
    const d = r.started_at ? new Date(r.started_at * 1000) : null;
    const t = d ? `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}` : "";
    return `<div class="row"><span>${r.ended ? "✅" : "⏸"}</span><span>${esc(r.persona || "")} · ${esc(r.set || "")}</span><span>${r.answers} 答</span><span class="t">${t}</span></div>`;
  }).join("");
}
function syncStart() {
  document.querySelectorAll(".tutor-card").forEach((c) => c.classList.toggle("sel", c.dataset.key === S.selPersona));
  document.querySelectorAll(".set-card").forEach((c) => c.classList.toggle("sel", c.dataset.key === S.selSet));
  $("startBtn").disabled = !(S.selPersona && S.selSet);
}
$("startBtn").addEventListener("click", () => startSession());
$("refreshStatsBtn").addEventListener("click", reloadHome);
$("favOpenBtn").addEventListener("click", () => openFavorites());
$("favOpenBtn2").addEventListener("click", () => openFavorites());

/* ---------------- 我的简历（本地保存，导入后示范答案出现「定制版」） ---------------- */
async function refreshProfileStat() {
  try {
    const p = await api("/api/profile");
    $("profileStat").innerHTML = p.has_profile
      ? `✅ 已导入（${p.chars} 字）—— 示范答案将提供「🎯 定制版」`
      : "⚠️ 未导入 —— 示范答案目前仅有「🧩 通用版」";
  } catch (e) { $("profileStat").textContent = "读取失败：" + e.message; }
}
$("profileBtn").addEventListener("click", () => { $("profileOverlay").classList.remove("hidden"); refreshProfileStat(); });
$("profileClose").addEventListener("click", () => $("profileOverlay").classList.add("hidden"));
$("profileOverlay").addEventListener("click", (e) => { if (e.target === $("profileOverlay")) $("profileOverlay").classList.add("hidden"); });
$("profilePick").addEventListener("click", () => $("profileFile").click());
$("profileFile").addEventListener("change", async () => {
  const f = $("profileFile").files[0];
  if (!f) return;
  const fd = new FormData();
  fd.append("file", f);
  try {
    const r = await api("/api/profile/upload", { method: "POST", body: fd });
    toast(`✅ 简历已导入（${r.chars} 字），定制版回答已解锁`);
    refreshProfileStat();
  } catch (e) { toast("导入失败：" + e.message); }
  $("profileFile").value = "";
});
$("profileSave").addEventListener("click", async () => {
  const text = $("profileText").value.trim();
  if (text.length < 30) { toast("内容太短（至少 30 字）"); return; }
  try {
    const r = await api("/api/profile/text", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
    toast(`✅ 已保存（${r.chars} 字），定制版回答已解锁`);
    $("profileText").value = "";
    refreshProfileStat();
  } catch (e) { toast("保存失败：" + e.message); }
});
$("profileWipe").addEventListener("click", async () => {
  if (!confirm("删除已导入的简历？示范答案将退回仅有通用版。")) return;
  try { await api("/api/profile", { method: "DELETE" }); toast("已删除"); refreshProfileStat(); } catch (e) { toast("删除失败：" + e.message); }
});

/* ---------------- 题集页（题目卡片墙） ---------------- */
let SET_VIEW = null;
async function openSet(key) {
  try {
    SET_VIEW = await api(`/api/set/${encodeURIComponent(key)}`);
  } catch (e) { toast("打开题集失败：" + e.message); return; }
  S.selSet = key;
  renderSets(); syncStart();
  renderSetView();
  showView("set");
}
function fmtDate(ts) {
  if (!ts) return "";
  const d = new Date(ts * 1000);
  return `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
function renderSetView() {
  const d = SET_VIEW;
  if (!d) return;
  $("setTitle").textContent = d.title;
  $("setProgress").textContent = `${d.done}/${d.count} 已练`;
  const pbar = $("setProgressBar");
  if (pbar) pbar.style.width = Math.round((d.done / Math.max(1, d.count)) * 100) + "%";
  const firstTodo = d.questions.find((q) => q.attempts === 0);
  $("setContinueBtn").textContent = firstTodo ? `▶ ${d.done ? "继续练习" : "从第 1 题开始"}` : "▶ 再练一遍";
  const cut = (s, n) => (s.length <= n ? s : s.slice(0, n).replace(/\s+\S*$/, "") + "…");
  $("qGrid").innerHTML = d.questions.map((q) => {
    const chip = q.attempts > 0 ? `<span class="qchip done">✓ 已练 ${q.attempts} 次</span>` : `<span class="qchip">未练</span>`;
    const best = q.best_score ? `<span class="qbest">最高 ${q.best_score}/10</span>` : "";
    const img = q.img ? `<img class="qimg" src="${esc(q.img)}" alt="" loading="lazy">` : `<span class="qimg ph">${esc((q.title || q.tag || "Q").slice(0, 1))}</span>`;
    return `<button class="qcard" data-i="${q.i}">
      ${img}
      <span class="qmain">
        <b>${esc(q.title || `第 ${q.i + 1} 题`)}</b>
        <small>${esc(cut(q.text, 66))}</small>
      </span>
      <span class="qside">${chip}${best}</span>
      <span class="qchev">›</span>
    </button>`;
  }).join("");
  $("qGrid").querySelectorAll(".qcard").forEach((el) => {
    el.addEventListener("click", () => openQuestionDetail(SET_VIEW.questions[+el.dataset.i]));
  });
}
function sparkSVG(history) {
  const pts = (history || []).filter((h) => h.score).map((h) => h.score).reverse();  // 时间正序
  if (pts.length < 2) return "";
  const W = 240, H = 48, P = 8;
  const xs = pts.map((_, i) => P + (i * (W - 2 * P)) / (pts.length - 1));
  const ys = pts.map((v) => H - P - ((v - 1) / 9) * (H - 2 * P));
  const line = xs.map((x, i) => `${x.toFixed(1)},${ys[i].toFixed(1)}`).join(" ");
  const dots = xs.map((x, i) => `<circle cx="${x.toFixed(1)}" cy="${ys[i].toFixed(1)}" r="2.6" fill="#0FA79A"/>`).join("");
  return `<svg class="spark" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}">
    <line x1="${P}" y1="${H - P}" x2="${W - P}" y2="${H - P}" stroke="#E3EDEC"/>
    <line x1="${P}" y1="${P}" x2="${P}" y2="${H - P}" stroke="#E3EDEC"/>
    <polyline points="${line}" fill="none" stroke="#0FA79A" stroke-width="2" stroke-linecap="round"/>${dots}</svg>`;
}
function openQuestionDetail(q) {
  const img = q.img ? `<img class="qd-img" src="${esc(q.img)}" alt="">` : `<span class="qd-img ph">${esc((q.title || "Q").slice(0, 1))}</span>`;
  const chips = [q.round, q.category].filter(Boolean).map((t) => `<span class="tag">${esc(t)}</span>`).join("");
  const histRows = (q.history || []).map((h) => {
    const sc = h.score ? `<b class="hsc">${h.score}/10</b>` : (h.accuracy ? `<b class="hsc">${h.accuracy}%</b>` : `<b class="hsc dim">—</b>`);
    return `<div class="hrow"><span>${fmtDate(h.ts)}</span><span>${h.mode === "read" ? "照读" : "自由说"}</span><span>${h.duration_s || 0}s</span><span>${h.wpm || 0} wpm</span>${sc}</div>`;
  }).join("") || `<div class="hempty">还没有练习记录 — 从这题开始第一次吧 💪</div>`;
  $("qdBody").innerHTML = `
    <div class="qd-head">${img}<div><h3>${esc(q.title || `第 ${q.i + 1} 题`)}</h3><div class="qmeta">${chips}</div></div></div>
    <div class="qd-q" data-ctx="${esc(q.text)}">${wordsHTML(q.text)}</div>
    ${q.intent ? `<div class="qd-note"><b>考察</b>${esc(q.intent)}</div>` : ""}
    ${q.hint ? `<div class="qd-note"><b>思路</b>${esc(q.hint)}</div>` : ""}
    ${sparkSVG(q.history)}
    <div class="qd-hist-title">历史练习（${(q.history || []).length} 次${q.best_score ? ` · 最高 ${q.best_score}/10` : ""}）</div>
    <div class="qd-hist">${histRows}</div>`;
  $("qStartBtn").dataset.i = q.i;
  $("qPlayBtn").dataset.text = q.text;
  $("qDetailOverlay").classList.remove("hidden");
}
$("qPlayBtn").addEventListener("click", (e) => speak(e.currentTarget.dataset.text, S.personaKey || undefined, e.currentTarget));
$("qStartBtn").addEventListener("click", () => {
  const i = +$("qStartBtn").dataset.i || 0;
  $("qDetailOverlay").classList.add("hidden");
  startSession(SET_VIEW.key, i);
});
$("qDetailClose").addEventListener("click", () => $("qDetailOverlay").classList.add("hidden"));
$("qDetailOverlay").addEventListener("click", (e) => { if (e.target === $("qDetailOverlay")) $("qDetailOverlay").classList.add("hidden"); });
$("setBackBtn").addEventListener("click", async () => { showView("home"); await reloadHome(); });
$("setContinueBtn").addEventListener("click", () => {
  const firstTodo = SET_VIEW.questions.find((q) => q.attempts === 0);
  startSession(SET_VIEW.key, firstTodo ? firstTodo.i : 0);
});

/* ---------------- 开始会话 ---------------- */
async function startSession(setKey, startIdx) {
  const set = setKey || S.selSet;
  if (!(S.selPersona && set)) return;
  try {
    $("startBtn").disabled = true;
    const st = await api("/api/session/start", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona: S.selPersona, set, start: startIdx || 0 }),
    });
    Object.assign(S, { sid: st.sid, personaKey: st.persona, state: st, mode: "free", script: "", sugg: {}, busy: false });
    $("messages").innerHTML = "";
    $("doneBanner").classList.add("hidden");
    $("micBtn").disabled = false;
    $("skipBtn").disabled = false;
    syncMode();
    updateChatTop();
    showView("chat");
    renderQuestion(st, true);
    setStatus("💡 点对话中的任意英文单词 = 查释义 · 收藏生词");
  } catch (e) {
    toast("启动失败：" + e.message);
  } finally {
    $("startBtn").disabled = false;
  }
}
function updateChatTop() {
  const t = tutorOf(S.personaKey);
  $("chatAvatar").textContent = t.emoji;
  $("chatTutor").textContent = `${t.en} · ${S.state ? S.state.persona_title || "" : ""}`;
  const st = S.state;
  if (st) $("chatProgress").textContent = st.done ? "已完成" : `Q ${st.idx + 1}/${st.total}${st.is_followup ? " · 追问" : ""}`;
  const bar = $("progressBar");
  if (bar && st) {
    const frac = st.done ? 1 : Math.min((st.idx + 0.5) / st.total, 1);
    bar.style.width = Math.round(frac * 100) + "%";
  }
}

/* ---------------- 渲染题目气泡 ---------------- */
function renderQuestion(st, autoplay, speakDelay) {
  updateChatTop();
  const t = tutorOf(S.personaKey);
  const tags = [];
  if (st.is_followup) tags.push(`<span class="tag fu">追问</span>`);
  if (st.round) tags.push(`<span class="tag">${esc(st.round)}</span>`);
  if (st.category) tags.push(`<span class="tag">${esc(st.category)}</span>`);
  const qinfo = (st.intent || st.hint) ? `
    <details class="qinfo"><summary>答题思路</summary>
      ${st.intent ? `<div class="row"><b>考察</b>${esc(st.intent)}</div>` : ""}
      ${st.hint ? `<div class="row"><b>思路</b>${esc(st.hint)}</div>` : ""}
    </details>` : "";
  const node = document.createElement("div");
  node.className = "msg ai";
  node.innerHTML = `
    <div class="avatar">${t.emoji}</div>
    <div class="col">
      <div class="bubble">
        ${tags.length ? `<div class="qmeta">${tags.join("")}</div>` : ""}
        <div class="qtext" data-ctx="${esc(st.question)}">${wordsHTML(st.question)}</div>
        ${qinfo}
      </div>
      <div class="ai-actions">
        <button class="mini-btn" data-act="play">▶ 播放</button>
        <button class="mini-btn" data-act="sugg">📖 示范答案</button>
      </div>
      <div class="sugg-slot"></div>
    </div>`;
  $("messages").appendChild(node);
  node.querySelector('[data-act="play"]').addEventListener("click", (e) => speak(st.question, S.personaKey, e.currentTarget));
  node.querySelector('[data-act="sugg"]').addEventListener("click", () => toggleSuggestion(node, st));
  S.suggCard = null; S.suggOpen = false;
  scrollBottom();
  stopAudio();  // 新题出现：先停掉旧音频（面试官/示范/任何声音），再排队自动播放新题
  if (autoplay) scheduleSpeak(st.question, S.personaKey, speakDelay || 500);
}
function scrollBottom() { const m = $("messages"); m.scrollTop = m.scrollHeight; }

/* ---------------- 示范答案 ---------------- */
function qKey(st) { return `${st.idx}:${st.is_followup ? "f" : "q"}`; }
async function fetchSuggestion(st, refresh) {
  const key = qKey(st);
  if (!refresh && S.sugg[key]) return S.sugg[key];
  const r = await api(`/api/session/${S.sid}/suggestion?refresh=${refresh ? 1 : 0}`);
  S.sugg[key] = r;  // {personal, generic, q_key}
  return S.sugg[key];
}
async function toggleSuggestion(qNode, st) {
  const slot = qNode.querySelector(".sugg-slot");
  if (slot.dataset.open === "1") { slot.innerHTML = ""; slot.dataset.open = "0"; return; }
  slot.dataset.open = "1";
  slot.innerHTML = `<div class="sugg-card"><div class="head"><b>📖 示范答案</b><span class="hint-inline">短答 · 通俗易懂 · 可直接说出口</span></div><div class="loading"><span class="loader-sm"></span>生成中…（首次约 4-10 秒）</div></div>`;
  try {
    const sug = await fetchSuggestion(st, false);
    renderSugg(slot, sug, st);
  } catch (e) {
    slot.innerHTML = `<div class="sugg-card"><div class="head"><b>📖 示范答案</b></div><p style="color:var(--red)">生成失败：${esc(e.message)}</p><div class="sugg-actions"><button class="mini-btn" data-a="retry">↻ 重试</button></div></div>`;
    slot.querySelector('[data-a="retry"]').addEventListener("click", () => { slot.dataset.open = "0"; toggleSuggestion(qNode, st); });
  }
}
function renderSugg(slot, sug, st) {
  const hasP = !!(sug && sug.personal);
  slot.innerHTML = `<div class="sugg-card">
    <div class="head"><b>📖 示范答案</b><span class="hint-inline">点单词可查释义 · 照读或参考后自己说</span></div>
    <div class="sugg-tabs">
      ${hasP
        ? `<button class="mini-btn tab on" data-t="personal">🎯 我的定制版</button><button class="mini-btn tab" data-t="generic">🧩 通用版</button>`
        : `<button class="mini-btn tab on" data-t="generic">🧩 通用版</button><span class="hint-inline">导入简历解锁定制版（首页 📄）</span>`}
      <span class="wcount"></span>
    </div>
    <p class="sugg-text" data-ctx=""></p>
    <div class="sugg-actions">
      <button class="mini-btn" data-a="read">🎧 照读这段</button>
      <button class="mini-btn" data-a="free">💬 参考着说</button>
      <button class="mini-btn" data-a="again">↻ 换一版</button>
      <button class="mini-btn" data-a="play">▶ 播放示范</button>
    </div></div>`;
  let cur = hasP ? "personal" : "generic";
  const textEl = slot.querySelector(".sugg-text");
  const cntEl = slot.querySelector(".wcount");
  const apply = () => {
    const t = (sug && sug[cur]) || "";
    textEl.innerHTML = wordsHTML(t);
    textEl.dataset.ctx = t;
    const n = (t.match(/[A-Za-z']+/g) || []).length;
    cntEl.textContent = `${n} 词 · 约 ${Math.round(n / 2.3)} 秒`;
    if (S.mode === "read") S.script = t;
  };
  slot.querySelectorAll(".sugg-tabs .tab").forEach((b) => b.addEventListener("click", () => {
    cur = b.dataset.t;
    slot.querySelectorAll(".sugg-tabs .tab").forEach((x) => x.classList.toggle("on", x === b));
    apply();
  }));
  slot.querySelectorAll("[data-a]").forEach((b) => b.addEventListener("click", async () => {
    const a = b.dataset.a;
    if (a === "read") { S.mode = "read"; S.script = (sug && sug[cur]) || ""; syncMode(); toast("已切换「照读模式」：录音时对照朗读"); }
    if (a === "free") { S.mode = "free"; syncMode(); toast("已切换「自己说」模式"); }
    if (a === "play") speak((sug && sug[cur]) || "", S.personaKey, b);
    if (a === "again") {
      textEl.innerHTML = `<span class="loader-sm"></span>换一版生成中…`;
      try {
        const t2 = await fetchSuggestion(st, true);
        sug.personal = t2.personal; sug.generic = t2.generic;
        apply();
      } catch (e) { toast("换一版失败：" + e.message); apply(); }
    }
  }));
  apply();
}
function syncMode() {
  $("modeFreeBtn").classList.toggle("on", S.mode === "free");
  $("modeReadBtn").classList.toggle("on", S.mode === "read");
}
$("modeFreeBtn").addEventListener("click", () => { S.mode = "free"; syncMode(); });
$("modeReadBtn").addEventListener("click", async () => {
  if (S.mode === "read") { S.mode = "free"; syncMode(); return; }
  S.mode = "read"; syncMode();
  if (!S.script && S.state) {
    try {
      setStatus("获取示范答案…");
      const sg0 = await fetchSuggestion(S.state, false);
      S.script = sg0.personal || sg0.generic;
      toast("示范答案已就绪：录音时对照朗读即可");
    } catch (e) { toast("获取示范失败：" + e.message); S.mode = "free"; syncMode(); }
    setStatus("");
  }
});
$("suggBtn").addEventListener("click", () => {
  const last = [...$("messages").querySelectorAll(".msg.ai")].pop();
  if (last && S.state) toggleSuggestion(last, S.state);
});
$("skipBtn").addEventListener("click", async () => {
  if (S.busy || S.phase !== "chat" || !S.sid) return;
  if (S.state && S.state.done) { toast("本场已完成，点右上角「复盘」"); return; }
  try {
    S.state = await api(`/api/session/${S.sid}/skip`, { method: "POST" });
    S.script = ""; S.suggCard = null;
    if (S.state.done) { showDone(); } else { renderQuestion(S.state, true); }
  } catch (e) { toast("跳过失败：" + e.message); }
});

/* ---------------- 录音 ---------------- */
$("micBtn").addEventListener("click", toggleMic);
document.addEventListener("keydown", (e) => {
  if (e.code !== "Space" || e.repeat) return;
  const tag = (e.target.tagName || "").toLowerCase();
  if (["input", "textarea", "select"].includes(tag) || e.target.isContentEditable) return;
  if (S.phase !== "chat") return;
  e.preventDefault();
  toggleMic();
});
async function toggleMic() {
  if (S.busy) return;
  if (S.recState === "recording") { stopRec(); return; }
  if (S.recState !== "idle" || S.phase !== "chat") return;
  if (S.state && S.state.done) return;
  stopAudio();  // 开始录音前停掉一切播放（不会和自己的麦克风打架）
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mime = ["audio/webm", "audio/mp4", ""].find((m) => !m || MediaRecorder.isTypeSupported(m));
    const mr = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
    S.chunks = [];
    mr.ondataavailable = (e) => { if (e.data && e.data.size) S.chunks.push(e.data); };
    mr.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(S.chunks, { type: mr.mimeType || "audio/webm" });
      await submitAnswer(blob);
    };
    mr.start();
    S.rec = mr; S.recState = "recording"; S.recStart = Date.now();
    keepScreenAwake(true);   // 录音期间屏幕常亮（移动端）
    $("micBtn").classList.add("rec"); $("micBtn").textContent = "■";
    $("micHint").textContent = "录音中…点击停止";
    setStatus("");
    S.timerId = setInterval(() => {
      const s = Math.floor((Date.now() - S.recStart) / 1000);
      $("timer").textContent = `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
      if (s >= S.maxSec) stopRec();
    }, 200);
  } catch (e) {
    toast("麦克风不可用：" + e.message);
  }
}
function stopRec() {
  if (S.rec && S.rec.state !== "inactive") S.rec.stop();
  S.recState = "idle";
  keepScreenAwake(false);
  clearInterval(S.timerId); S.timerId = null;
  $("micBtn").classList.remove("rec"); $("micBtn").textContent = "🎤";
  $("micHint").textContent = MIC_HINT;
}
async function submitAnswer(blob) {
  S.busy = true;
  setStatus("识别 + 生成反馈中…（约 5-15 秒）");
  $("micBtn").disabled = true;
  $("skipBtn").disabled = true;
  const ext = blob.type.includes("mp4") ? "m4a" : "webm";
  const fd = new FormData();
  fd.append("audio", blob, `answer.${ext}`);
  fd.append("mode", S.mode);
  fd.append("script", S.mode === "read" ? S.script || "" : "");
  try {
    const r = await api(`/api/session/${S.sid}/answer`, { method: "POST", body: fd });
    renderUserCard(r);
    renderFeedback(r);
    if (r.feedback_error) toast("⚠️ 反馈生成失败，详见反馈卡（可检查 ⚙️ 设置）");
    S.state = r.state;
    S.script = "";
    updateChatTop();
    $("timer").textContent = "00:00";
    if (S.state.done) { showDone(); }
    else { renderQuestion(S.state, true, 2600); }   // 留出时间先看反馈，再播下一题
    setStatus("");
  } catch (e) {
    setStatus("⚠️ 提交失败：" + e.message + "（可直接重录重试）");
    toast("提交失败：" + e.message);
  } finally {
    S.busy = false;
    $("micBtn").disabled = false;
    $("skipBtn").disabled = false;
  }
}
function showDone() {
  $("doneBanner").classList.remove("hidden");
  $("micBtn").disabled = true;
  $("skipBtn").disabled = true;
  S.busy = false;
  stopAudio();
}

/* ---------------- 用户卡 & 反馈卡 ---------------- */
function wordsHTML(transcript, highlight) {
  const hl = new Set((highlight || []).map((w) => w.toLowerCase()));
  return esc(transcript || "").replace(/[A-Za-z']+/g, (w) => {
    const cls = hl.has(w.toLowerCase()) ? "w hl" : "w";
    return `<span class="${cls}">${w}</span>`;
  });
}
function renderUserCard(r) {
  const node = document.createElement("div");
  node.className = "msg user";
  let diffRow = "";
  const sd = r.script_diff;
  if (sd && sd.script_words) {
    const miss = (sd.missed || []).map((w) => `<span class="chipword miss">漏 ${esc(w)}</span>`).join("");
    const extra = (sd.extra || []).map((w) => `<span class="chipword extra">添 ${esc(w)}</span>`).join("");
    diffRow = `<div class="diff-row"><span class="acc">照读准确率 ${sd.accuracy}%</span>${miss}${extra}</div>`;
  }
  node.innerHTML = `<div class="col"><div class="bubble user">
    <div class="lbl">你说（${r.mode === "read" ? "照读" : "自由说"}）</div>
    <div class="utext" data-ctx="${esc(r.transcript || "")}">${wordsHTML(r.transcript, r.script_diff ? r.script_diff.extra : [])}</div>
    ${diffRow}
  </div></div>`;
  $("messages").appendChild(node);
  scrollBottom();
}
function renderFeedback(r) {
  const fb = r.feedback || {};
  const m = r.metrics || {};
  let body = "";
  const sc = parseInt(fb.score, 10);
  const scoreHTML = sc >= 1 && sc <= 10
    ? `<span class="fb-score ${sc >= 8 ? "good" : sc >= 6 ? "ok" : "low"}">${sc}<i>/10</i></span>`
    : (r.feedback_error ? `<span class="fb-score low">!</span>` : "");
  let hasContent = false;
  if (r.feedback_error) {
    body += `<div class="fb-err">⚠️ <b>本轮反馈生成失败</b>：${esc(r.feedback_error)}<br>
      请到「⚙️ 设置 → 💬 对话服务」检查接口地址 / API Key / 模型，并点「🧪 测试对话服务」自查；修正后下一轮自动恢复（本场其余流程不受影响）。</div>`;
    hasContent = true;
  }
  if (fb.verdict) { body += `<div class="verdict">${esc(fb.verdict)}</div>`; hasContent = true; }
  if (r.mode === "read" && r.script_diff && r.script_diff.script_words) {
    body += `<span class="pill read">朗读表现</span><div class="seg">照读准确率 <b>${r.script_diff.accuracy}%</b>（漏读 ${(r.script_diff.missed || []).length} 词 · 添词 ${(r.script_diff.extra || []).length} 词）</div>`;
    hasContent = true;
  }
  if (fb.content_gap) { body += `<span class="pill content">内容建议</span><div class="seg">${esc(fb.content_gap)}</div>`; hasContent = true; }
  if (fb.language_point && fb.language_point.original) {
    body += `<span class="pill correction">Correction</span>
      <div class="delta"><span class="orig">${esc(fb.language_point.original)}</span><span class="arrowx">→</span><span class="better" data-ctx="${esc(fb.language_point.better)}">${wordsHTML(fb.language_point.better)}</span></div>
      <div class="explain">${esc(fb.language_point.explain || "")}</div>`;
    hasContent = true;
  }
  if (fb.upgrade && fb.upgrade.original) {
    body += `<span class="pill upgrade">Upgrade</span>
      <div class="delta"><span class="orig">${esc(fb.upgrade.original)}</span><span class="arrowx">→</span><span class="better" data-ctx="${esc(fb.upgrade.better)}">${wordsHTML(fb.upgrade.better)}</span></div>
      <div class="explain">${esc(fb.upgrade.explain || "")}</div>`;
    hasContent = true;
  }
  if (fb.polished) {
    body += `<span class="pill revision">Revision</span><div class="seg" data-ctx="${esc(fb.polished)}">${wordsHTML(fb.polished)}</div>
      <div class="fb-actions">
        <button class="mini-btn" data-f="say">🔊 Say it!</button>
        <button class="mini-btn" data-f="fav">⭐ 收藏</button>
        <button class="mini-btn" data-f="copy">📋 复制</button>
      </div>`;
    hasContent = true;
  } else if (fb.language_point && fb.language_point.better) {
    body += `<div class="fb-actions"><button class="mini-btn" data-f="say">🔊 朗读修订句</button></div>`;
    hasContent = true;
  }
  if (!hasContent) {
    body += `<div class="fb-err">⚠️ <b>本轮没有可显示的反馈内容</b>：模型返回了空的反馈对象（服务端已记录原始输出）。<br>
      请到「⚙️ 设置 → 💬 对话服务」点「🧪 测试对话服务」查看原始返回；不影响继续练习。</div>`;
  }
  body += `<div class="metrics-line">用时 ${m.duration_s || 0}s · ${m.wpm || 0} wpm · 填充词 ${m.fillers || 0} · 长停顿 ${m.long_pauses || 0} · 转写引擎 ${esc({ cloud: "云端", local: "本地" }[r.asr_driver] || r.asr_driver || "")}</div>`;

  const node = document.createElement("details");
  node.className = "fb-card";
  node.open = true; // 默认展开；折叠/展开用原生 <details>，与「答题思路」同机制，任何环境点击都可切换
  node.innerHTML = `<summary class="fb-head"><b>AI Feedback</b>${scoreHTML}<span class="arrow">▾</span></summary><div class="fb-body">${body}</div>`;
  const sayText = fb.polished || (fb.language_point && fb.language_point.better) || "";
  node.querySelectorAll("[data-f]").forEach((b) => b.addEventListener("click", async () => {
    const a = b.dataset.f;
    if (a === "say") speak(sayText, S.personaKey, b);
    if (a === "copy") { try { await navigator.clipboard.writeText(sayText); toast("已复制"); } catch (e) { toast("复制失败"); } }
    if (a === "fav") {
      try {
        await api("/api/favorite", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "revision", text: sayText, note: fb.verdict || "", session: S.sid }) });
        toast("已加入收藏夹 ⭐");
      } catch (e) { toast("收藏失败：" + e.message); }
    }
  }));
  $("messages").appendChild(node);
  scrollBottom();
}

/* ---------------- 设置（接口地址 / API Key / 模型） ---------------- */
async function openSettings() {
  $("settingsOverlay").classList.remove("hidden");
  try {
    const s = await api("/api/settings");
    $("setBase").value = s.api_base_url || "";
    $("setModel").value = s.llm_model || "";
    $("setAsrEp").value = s.asr_endpoint || "";
    $("setAsrModel").value = s.asr_model || "";
    $("setTtsEp").value = s.tts_endpoint || "";
    $("setTtsModel").value = s.tts_model || "";
    $("setTtsVoice").value = s.tts_voice || "";
    $("setKey").value = "";
    $("setKey").placeholder = s.api_key_set ? `已设置（${s.api_key_masked}）· 留空 = 不修改` : "粘贴你的 Key";
    $("setSpeechKey").value = "";
    $("setSpeechKey").placeholder = s.speech_key_set
      ? `已设置（${s.speech_key_masked}）· 留空 = 不修改`
      : "留空 = 复用对话 Key";
    $("settingsFile").textContent = "配置文件：" + (s.env_file || "");
    const verEl = $("setVer");
    if (verEl) verEl.textContent = "版本 " + (s.version || "?");
    const adv = document.querySelector("#settingsOverlay details.smore");
    if (adv) adv.open = !s.asr_endpoint;   // 识别端点未配置 → 自动展开引导
    const qr = $("quitRow");
    if (qr) qr.style.display = s.can_quit ? "" : "none";
    refreshMobile();
  } catch (e) { toast("读取设置失败：" + e.message); }
}
async function saveSettings() {
  const body = {
    api_base_url: $("setBase").value.trim(),
    llm_model: $("setModel").value.trim(),
    asr_endpoint: $("setAsrEp").value.trim(),
    asr_model: $("setAsrModel").value.trim(),
    tts_endpoint: $("setTtsEp").value.trim(),
    tts_model: $("setTtsModel").value.trim(),
    tts_voice: $("setTtsVoice").value.trim(),
  };
  const k = $("setKey").value.trim();
  if (k) body.api_key = k;
  const sk = $("setSpeechKey").value.trim();
  if (sk) body.speech_api_key = sk;
  $("settingsSave").disabled = true;
  try {
    await api("/api/settings", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    toast("✅ 已保存，立即生效");
    $("setKey").value = "";
    refreshSetupBanner();
    reloadHome();
  } catch (e) { toast("保存失败：" + e.message); }
  finally { $("settingsSave").disabled = false; }
}
async function refreshSetupBanner() {
  try {
    const h = await api("/api/health");
    $("setupBanner").classList.toggle("hidden", !!h.api_configured);
  } catch (e) {}
}
$("settingsBtn").addEventListener("click", openSettings);

/* ---------------- 🧪 对话服务自检（排障用） ---------------- */
async function runSelftest() {
  const box = $("selftestOut");
  if (!box) return;
  box.classList.remove("hidden");
  box.textContent = "🧪 测试中…（约 5–20 秒，会消耗一次少量 API 调用）";
  try {
    const r = await api("/api/selftest/llm");
    const lines = [];
    lines.push(r.ok ? "✅ 对话服务正常（反馈 JSON 生成成功）" : "❌ 对话服务异常");
    if (r.version) lines.push("版本：" + r.version);
    if (r.model) lines.push("模型：" + r.model);
    if (r.base) lines.push("接口地址：" + r.base);
    if (r.plain) lines.push("基础回复：" + r.plain);
    if (r.feedback_keys) lines.push("反馈字段：" + r.feedback_keys);
    if (r.feedback_preview) lines.push("反馈原始返回（截断）：\n" + r.feedback_preview);
    if (r.error) lines.push("⚠️ 错误：" + r.error);
    lines.push("（把此结果截图发给开发者即可定位问题）");
    box.textContent = lines.join("\n");
  } catch (e) {
    box.textContent = "❌ 测试请求失败：" + e.message;
  }
}
const _stb = $("selftestBtn");
if (_stb) _stb.addEventListener("click", runSelftest);
$("setupBanner").addEventListener("click", openSettings);
$("settingsSave").addEventListener("click", saveSettings);
$("quitBtn").addEventListener("click", async () => {
  if (!confirm("确定完全退出程序？（后台服务将停止，数据已自动保存）")) return;
  try { await api("/api/quit", { method: "POST" }); } catch (e) {}
  document.body.innerHTML = '<div style="font:15px/1.9 system-ui;padding:70px 24px;text-align:center;color:#444">✅ 程序已退出<br><span style="color:#999;font-size:13px">现在可以关闭本窗口了</span></div>';
});
$("settingsClose").addEventListener("click", () => $("settingsOverlay").classList.add("hidden"));
$("settingsOverlay").addEventListener("click", (e) => { if (e.target === $("settingsOverlay")) $("settingsOverlay").classList.add("hidden"); });

/* —— 手机访问（HTTPS 通道，一键启用） —— */
async function refreshMobile() {
  try {
    renderMobile(await api("/api/mobile"));
  } catch (e) {
    $("mobBody").innerHTML = `<p class="pdesc" style="margin:0">读取失败：${esc(e.message)}</p>`;
  }
}
function renderMobile(m) {
  const st = $("mobState");
  st.textContent = m.enabled ? "已启用" : (m.tailscale ? "未启用（可经 Tailscale）" : "未启用");
  st.classList.toggle("ok", !!m.enabled);
  if (m.enabled) {
    $("mobBody").innerHTML = `
      <p class="pdesc" style="margin:2px 0 6px">手机浏览器打开（需先安装证书，一次即可）：</p>
      ${(m.urls || []).map((u) => `<div class="mob-url"><code>${esc(u)}</code><button class="mini-btn" data-copy="${esc(u)}">复制</button></div>`).join("") || `<p class="pdesc">未检测到可用地址（检查网络/Tailscale）。</p>`}
      <p class="pdesc" style="margin:8px 0 0">iPhone 首次安装证书：用 Safari 打开上面地址（提示"证书无效"→继续访问）→ 再打开 <code>该地址/ca.crt</code> 下载描述文件 → 「设置 → 通用 → VPN与设备管理」安装 → 「通用 → 关于本机 → 证书信任设置」开启完全信任 → 分享 → 添加到主屏幕。</p>
      <div class="prow" style="margin-top:8px">
        <a class="mini-btn" href="/ca.crt">下载证书（CA）</a>
        <button class="mini-btn" id="mobDisable" style="margin-left:8px">停用</button>
      </div>`;
  } else {
    $("mobBody").innerHTML = `
      <p class="pdesc" style="margin:2px 0 8px">手机（Tailscale 或同一 Wi-Fi）使用需要 HTTPS 通道——点一下自动生成证书并开启${m.cert_ready ? "（证书已就绪）" : ""}。</p>
      <button class="btn ghost small" id="mobEnable">启用手机访问</button>`;
  }
}
$("mobBody").addEventListener("click", async (e) => {
  const b = e.target.closest("button, a");
  if (!b) return;
  if (b.id === "mobEnable") {
    b.disabled = true;
    try {
      const r = await api("/api/mobile/enable", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
      renderMobile(r);
      toast(r.already ? "手机访问已在运行" : "✅ 手机访问已启用");
    } catch (err) { toast("启用失败：" + err.message); b.disabled = false; }
  } else if (b.id === "mobDisable") {
    try { renderMobile(await api("/api/mobile/disable", { method: "POST" })); toast("已停用"); } catch (err) { toast("停用失败：" + err.message); }
  } else if (b.dataset.copy) {
    try { await navigator.clipboard.writeText(b.dataset.copy); toast("已复制"); } catch (err) {}
  }
});

/* ---------------- 单词速查 ---------------- */
let glossWord = "";
/* 全局点词委派：带 data-ctx 容器内的任意 .w 单词都可点击查释义/收藏 */
document.addEventListener("click", (e) => {
  const w = e.target.closest(".w");
  if (!w) return;
  const holder = w.closest("[data-ctx]");
  openGloss(w.textContent, holder ? holder.dataset.ctx : "");
});
async function openGloss(word, context) {
  glossWord = word;
  $("glossOverlay").classList.remove("hidden");
  $("gw").textContent = word;
  $("glossBody").innerHTML = `<div class="loading"><span class="loader-sm"></span>查询中…</div>`;
  try {
    const g = await api(`/api/gloss?word=${encodeURIComponent(word)}&context=${encodeURIComponent((context || "").slice(-600))}`);
    $("glossBody").innerHTML = `
      ${g.ipa ? `<div class="ipa">/${esc(g.ipa)}/ <button class="mini-btn" data-g="play" style="padding:2px 9px">🔊</button></div>` : ""}
      <div><span class="pos">${esc(g.pos || "")}</span><span class="zh">${esc(g.zh || "")}</span></div>
      ${g.example_en ? `<div class="ex" data-ctx="${esc(g.example_en)}">${wordsHTML(g.example_en)}<div class="zhx">${esc(g.example_zh || "")}</div></div>` : ""}
      ${g.note ? `<div class="note">💡 ${esc(g.note)}</div>` : ""}
      <div class="actions">
        <button class="mini-btn" data-g="fav">⭐ 收藏生词</button>
      </div>`;
    $("glossBody").querySelectorAll("[data-g]").forEach((b) => b.addEventListener("click", async () => {
      if (b.dataset.g === "play") speak(word, S.personaKey || undefined, b);
      if (b.dataset.g === "fav") {
        try {
          await api("/api/favorite", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ type: "word", text: word, note: g.zh || "", ipa: g.ipa || "", session: S.sid || "" }) });
          toast("已收藏 ⭐");
          reloadHome();
        } catch (e) { toast("收藏失败：" + e.message); }
      }
    }));
  } catch (e) {
    $("glossBody").innerHTML = `<p style="color:var(--red)">查询失败：${esc(e.message)}</p>`;
  }
}
$("glossClose").addEventListener("click", () => $("glossOverlay").classList.add("hidden"));
$("glossOverlay").addEventListener("click", (e) => { if (e.target === $("glossOverlay")) $("glossOverlay").classList.add("hidden"); });

/* ---------------- 收藏夹：词库（字典式分页 + 删除） + 今日复习 ---------------- */
const FAV = { all: [], page: 1, per: 8, sort: localStorage.getItem("et_fav_sort") || "new", slice: [] };
const REV = { data: null, stats: null, running: false, queue: [], lose: [], pass: 1, revealed: false };

let favTab = "lib";
async function openFavorites(tab) {
  $("favOverlay").classList.remove("hidden");
  switchFavTab(typeof tab === "string" ? tab : favTab);
}
function switchFavTab(tab) {
  favTab = tab;
  $("favTabLib").classList.toggle("active", tab === "lib");
  $("favTabRev").classList.toggle("active", tab === "review");
  $("favPaneLib").classList.toggle("hidden", tab !== "lib");
  $("favPaneRev").classList.toggle("hidden", tab !== "review");
  if (tab === "lib") loadFavLib(); else loadReview();
}

/* —— 词库（字典式：分页 / 排序 / 删除 / 点击查词） —— */
async function loadFavLib() {
  $("favList").innerHTML = `<div class="empty"><span class="loader-sm"></span>加载中…</div>`;
  try {
    FAV.all = await api("/api/favorites");
    FAV.page = 1;
    renderFavLib();
  } catch (e) { $("favList").innerHTML = `<div class="empty">加载失败：${esc(e.message)}</div>`; }
}
function favSorted() {
  const arr = FAV.all.slice();
  if (FAV.sort === "new") arr.sort((a, b) => (b.ts || 0) - (a.ts || 0));
  else arr.sort((a, b) => String(a.text || "").toLowerCase().localeCompare(String(b.text || "").toLowerCase(), "en"));
  return arr;
}
function renderFavLib() {
  const arr = favSorted();
  const pages = Math.max(1, Math.ceil(arr.length / FAV.per));
  FAV.page = Math.min(Math.max(1, FAV.page), pages);
  FAV.slice = arr.slice((FAV.page - 1) * FAV.per, FAV.page * FAV.per);
  $("favCount").textContent = arr.length ? `共 ${arr.length} 条 · 第 ${FAV.page} / ${pages} 页` : "";
  $("favSortBtn").textContent = FAV.sort === "new" ? "排序：最新" : "排序：A–Z";
  if (!arr.length) {
    $("favList").innerHTML = `<div class="empty">还没有收藏。练习中点单词或收藏 Revision 句子吧 ⭐</div>`;
    $("favPager").innerHTML = "";
    return;
  }
  $("favList").innerHTML = FAV.slice.map((f, i) => {
    const d = f.ts ? new Date(f.ts * 1000) : null;
    const t = d ? `${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}` : "";
    const isWord = (f.type || "word") === "word";
    return `<div class="fv-row">
      <div class="fv-top">
        <span class="fv-word ${isWord ? "" : "rev"}" data-ctx="${esc(f.text || "")}">${wordsHTML(f.text || "")}</span>
        ${f.ipa ? `<span class="fv-ipa">/${esc(f.ipa)}/</span>` : ""}
        ${isWord ? "" : `<span class="tag fu">修订句</span>`}
        <span class="fv-right">
          ${/[A-Za-z]/.test(f.text || "") ? `<button class="mini-btn" data-say="${esc(f.text || "")}" title="朗读">🔊</button>` : ""}
          <span class="fv-date">${t}</span>
          <button class="fv-del" data-del="${i}" title="删除">✕</button>
        </span>
      </div>
      ${f.note ? `<div class="fv-note" data-note="${i}" title="点击展开/收起">${esc(f.note)}</div>` : ""}
    </div>`;
  }).join("");
  $("favPager").innerHTML = pages > 1 ? `
    <button class="mini-btn" id="favPrev" ${FAV.page <= 1 ? "disabled" : ""}>‹ 上一页</button>
    <span>${FAV.page} / ${pages}</span>
    <button class="mini-btn" id="favNext" ${FAV.page >= pages ? "disabled" : ""}>下一页 ›</button>` : "";
  const prev = $("favPrev"); if (prev) prev.addEventListener("click", () => { FAV.page--; renderFavLib(); });
  const next = $("favNext"); if (next) next.addEventListener("click", () => { FAV.page++; renderFavLib(); });
  $("favList").querySelectorAll("[data-say]").forEach((b) => b.addEventListener("click", () => speak(b.dataset.say, S.personaKey || undefined, b)));
  $("favList").querySelectorAll("[data-note]").forEach((n) => n.addEventListener("click", () => n.classList.toggle("exp")));
  $("favList").querySelectorAll("[data-del]").forEach((b) => b.addEventListener("click", () => onFavDelete(b)));
}
async function onFavDelete(btn) {
  const f = FAV.slice[parseInt(btn.dataset.del, 10)];
  if (!f) return;
  if (!btn.classList.contains("confirm")) {          // 两步确认：✕ → 确认删除？
    btn.classList.add("confirm");
    btn.textContent = "确认删除？";
    btn.dataset.timer = setTimeout(() => { btn.classList.remove("confirm"); btn.textContent = "✕"; }, 2600);
    return;
  }
  clearTimeout(btn.dataset.timer);
  try {
    await api("/api/favorite/delete", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: f.text || "", kind: f.type || "word" }) });
    FAV.all = FAV.all.filter((x) => !((x.text || "") === (f.text || "") && (x.type || "word") === (f.type || "word")));
    REV.data = null;
    toast(`已删除「${String(f.text || "").slice(0, 24)}」`);
    renderFavLib();
    reloadHome();
  } catch (e) { toast("删除失败：" + e.message); }
}
$("favSortBtn").addEventListener("click", () => {
  FAV.sort = FAV.sort === "new" ? "alpha" : "new";
  localStorage.setItem("et_fav_sort", FAV.sort);
  renderFavLib();
});
$("favTabLib").addEventListener("click", () => switchFavTab("lib"));
$("favTabRev").addEventListener("click", () => switchFavTab("review"));
$("favClose").addEventListener("click", () => $("favOverlay").classList.add("hidden"));
$("favOverlay").addEventListener("click", (e) => { if (e.target === $("favOverlay")) $("favOverlay").classList.add("hidden"); });

/* —— 今日复习（按比例随机温故） —— */
function revBadgeFrom(st) {
  REV.stats = st || null;
  refreshRevBadge();
}
function refreshRevBadge() {
  const b = $("revBadge");
  const src = REV.data ? { remaining: REV.data.remaining, done: REV.data.done, goal: REV.data.goal } : REV.stats;
  if (!src || !src.goal) { b.classList.add("hidden"); return; }
  b.textContent = src.done ? "✓" : String(src.remaining);
  b.classList.toggle("ok", !!src.done);
  b.classList.remove("hidden");
}
async function loadReview() {
  $("favPaneRev").innerHTML = `<div class="empty"><span class="loader-sm"></span>加载复习计划…</div>`;
  try {
    REV.data = await api("/api/review");
    resetRevRun();
    refreshRevBadge();
    renderRevPane();
  } catch (e) { $("favPaneRev").innerHTML = `<div class="empty">加载失败：${esc(e.message)}</div>`; }
}
function resetRevRun() { REV.running = false; REV.queue = []; REV.lose = []; REV.pass = 1; REV.revealed = false; }
function revWeek(d) {
  const rec = d.recent || [];
  if (!rec.length) return "";
  return `<div class="rev-week"><span>最近 7 天</span>${rec.map((x) => `<span class="rd ${x.count ? "on" : ""}" title="${x.date} · 复习 ${x.count} 词">${x.count || ""}</span>`).join("")}</div>`;
}
function renderRevPane() {
  const d = REV.data || {};
  const deck = d.deck || [];
  if (!deck.length) {
    $("favPaneRev").innerHTML = `<div class="rev-wrap"><div class="rev-ico">🌱</div><h3>还没有待复习的单词</h3><p class="rev-goal">在练习中点单词 →「⭐ 收藏生词」，第二天起就会按比例随机进入复习计划。</p></div>`;
    return;
  }
  if (REV.running) { renderRevCard(); return; }
  if (d.done) {
    const weak = deck.filter((x) => x.last_ok === false);
    $("favPaneRev").innerHTML = `<div class="rev-wrap">
      <div class="rev-done-ico">🎉</div>
      <h3>今日复习完成！</h3>
      <p class="rev-goal">复习 <b>${d.answered}</b> 词 · 记住 <b>${d.correct}</b>${weak.length ? ` · 待加强 <b class="rev-weak-n">${weak.length}</b>` : " · 全对好棒"}</p>
      ${weak.length ? `<div class="rev-weak">没记住的将优先出现在明天：${weak.map((x) => `<span class="chip">${esc(x.text)}</span>`).join("")}</div>` : ""}
      ${revWeek(d)}
      <p class="rev-hint" style="margin-top:14px">明天见 👋</p>
    </div>`;
    return;
  }
  $("favPaneRev").innerHTML = `<div class="rev-wrap">
    <div class="rev-ico">🔁</div>
    <h3>今日复习</h3>
    <p class="rev-goal">目标 <b>${d.goal}</b> 词（共收藏 ${d.pool} 词 × ${Math.round((d.ratio || 0.3) * 100)}% 随机抽取）<br>优先安排从未复习、上次没记住、久未复习的单词。</p>
    ${d.answered ? `<p class="rev-partial">已复习 ${d.answered} / ${d.goal}，还剩 <b>${d.remaining}</b> 词</p>` : ""}
    <button class="btn primary" id="revStartBtn">${d.answered ? "继续复习" : "开始复习"}（${d.remaining} 词）</button>
    ${revWeek(d)}
  </div>`;
  $("revStartBtn").addEventListener("click", startRev);
}
function startRev() {
  REV.queue = (REV.data.deck || []).filter((x) => !x.done).slice();
  REV.running = true; REV.lose = []; REV.pass = 1; REV.revealed = false;
  renderRevCard();
}
function renderRevCard() {
  const item = REV.queue[0];
  if (!item) return finRev();
  const d = REV.data;
  const pct = d.goal ? Math.round((d.answered / d.goal) * 100) : 0;
  $("favPaneRev").innerHTML = `<div class="rev-wrap">
    <div class="rev-prog"><div class="rev-bar"><i style="width:${pct}%"></i></div><span>${d.answered} / ${d.goal}</span></div>
    ${REV.pass === 2 ? `<div class="rev-pass">第 2 轮 · 再试一次（${REV.queue.length} 词）</div>` : ""}
    <div class="rev-card">
      <div class="rev-word">${esc(item.text)}<button class="mini-btn" id="revSay" title="朗读">🔊</button></div>
      ${item.ipa ? `<div class="rev-ipa">/${esc(item.ipa)}/</div>` : ""}
      <div class="rev-badge-mini ${item.reviewed_before ? "" : "new"}">${item.reviewed_before ? `已复习 ${item.times} 次${item.prev_ok === false ? " · 上次没记住" : ""}` : "新词 · 第一次复习"}</div>
      ${REV.revealed && item.note ? `<div class="rev-note">${esc(item.note)}</div>` : ""}
      ${REV.revealed && !item.note ? `<div class="rev-note rev-nonote">（收藏时未记录释义）</div>` : ""}
      ${REV.revealed ? "" : `<button class="btn primary small" id="revShow">显示释义</button>`}
    </div>
    ${REV.revealed
      ? `<div class="rev-btns"><button class="btn ghost" id="revNo">😵 没记住</button><button class="btn primary" id="revYes">😎 记住了</button></div>`
      : `<div class="rev-hint">先在心里回忆一遍，再点「显示释义」</div>`}
  </div>`;
  $("revSay").addEventListener("click", () => speak(item.text, S.personaKey || undefined, $("revSay")));
  const show = $("revShow"); if (show) show.addEventListener("click", () => { REV.revealed = true; renderRevCard(); });
  const yes = $("revYes"); if (yes) yes.addEventListener("click", () => revAnswer(item, true));
  const no = $("revNo"); if (no) no.addEventListener("click", () => revAnswer(item, false));
}
async function revAnswer(item, ok) {
  try {
    const resp = await api("/api/review/answer", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ word: item.text, ok }) });
    REV.data = resp;
    REV.queue.shift();
    if (!ok) REV.lose.push(item);
    REV.revealed = false;
    if (!REV.queue.length) {
      if (REV.pass === 1 && REV.lose.length) {
        REV.pass = 2; REV.queue = REV.lose.slice(); REV.lose = [];
        toast(`还有 ${REV.queue.length} 个词，再巩固一轮`);
        renderRevCard();
        return;
      }
      return finRev();
    }
    renderRevCard();
  } catch (e) { toast("记录失败：" + e.message); }
}
function finRev() {
  REV.running = false;
  refreshRevBadge();
  renderRevPane();
  reloadHome();
  if (REV.data && REV.data.done) { toast("✅ 今日复习完成！"); setTimeout(() => burstConfetti(90), 120); }
}

/* ---------------- 复盘 ---------------- */
$("endBtn").addEventListener("click", endSession);
async function endSession() {
  if (!S.sid) return;
  try {
    setStatus("生成复盘中…（约 10-20 秒）");
    $("endBtn").disabled = true;
    stopAudio();
    const r = await api(`/api/session/${S.sid}/end`, { method: "POST" });
    renderReport(r);
    showView("report");
  } catch (e) {
    toast("复盘失败：" + e.message);
  } finally { $("endBtn").disabled = false; setStatus(""); }
}
function renderReport(r) {
  const rv = r.review || {};
  const sc = rv.scores || {};
  const names = { content: "内容", structure: "结构", grammar: "语法", lexical: "词汇", fluency: "流利度" };
  const bars = Object.keys(names).map((k) => `
    <div class="score-row"><span class="name">${names[k]}</span>
      <span class="bar"><i style="width:${(Math.max(0, Math.min(5, sc[k] || 0)) / 5) * 100}%"></i></span>
      <span class="val">${sc[k] || 0}/5</span></div>`).join("");
  const strengths = (rv.strengths || []).map((s) => `<li>${esc(s)}</li>`).join("");
  const issues = (rv.issues || []).map((i) => `<li><span class="tag">${esc(i.type || "")}</span> ${esc(i.pattern || "")}<span class="ex">例：<span class="ita">${esc(i.example || "")}</span> → <span class="fix">${esc(i.fix || "")}</span></span></li>`).join("");
  const drills = (rv.drills || []).map((d) => `<li>${esc(d)}</li>`).join("");
  $("reportBody").innerHTML = `
    ${bars ? `<div class="report-card"><h3>评分</h3>${bars}</div>` : ""}
    ${strengths ? `<div class="report-card"><h3>✅ 做得好的</h3><ul>${strengths}</ul></div>` : ""}
    ${issues ? `<div class="report-card"><h3>🔧 反复出现的问题</h3><ul>${issues}</ul></div>` : ""}
    ${drills ? `<div class="report-card"><h3>📝 下次训练前练这 3 件事</h3><ul>${drills}</ul></div>` : ""}
    ${rv.next_focus ? `<div class="focus">🎯 下次重点：${esc(rv.next_focus)}</div>` : ""}
    <div class="rpath">报告已保存：${esc(r.report || "")}</div>`;
}
$("backHomeBtn").addEventListener("click", async () => { showView("home"); await reloadHome(); });
$("backBtn").addEventListener("click", async () => {
  if (S.busy) return;
  if (!confirm("返回首页？本场未复盘的作答仍会保存到记录。")) return;
  showView("home");
  await reloadHome();
});

/* ---------------- 启动 ---------------- */
boot();

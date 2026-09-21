"""提示词、人格、题库、示范答案生成。"""
import json
from pathlib import Path

import yaml

from . import config


def load_persona(key: str) -> dict:
    """从 materials/personas/<key>.md 读取：标题、说明、'### system' 后的系统提示。"""
    p = config.materials_dir() / "personas" / f"{key}.md"
    if not p.exists():
        raise FileNotFoundError(f"persona not found: {p}")
    text = p.read_text(encoding="utf-8")
    title = ""
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    sys_prompt = ""
    marker = "### system"
    if marker in text:
        sys_prompt = text.split(marker, 1)[1].strip()
    return {"key": key, "title": title or key, "system": sys_prompt}


def list_personas() -> list:
    d = config.materials_dir() / "personas"
    out = []
    if not d.exists():
        return out
    for p in sorted(d.glob("*.md")):
        try:
            out.append(load_persona(p.stem))
        except Exception:
            continue
    return [{"key": x["key"], "title": x["title"]} for x in out]


def load_question_set(key: str) -> dict:
    p = config.materials_dir() / "question-bank" / f"{key}.yml"
    if not p.exists():
        raise FileNotFoundError(f"question set not found: {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def list_question_sets() -> list:
    d = config.materials_dir() / "question-bank"
    out = []
    if not d.exists():
        return out
    for p in sorted(d.glob("*.yml")):
        try:
            j = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            out.append({"key": p.stem, "title": j.get("title", p.stem), "count": len(j.get("questions", []))})
        except Exception:
            continue
    return out


def load_profile() -> str:
    """读取个人资料（materials/profile.md，由首页『我的简历』导入生成）。
    文件不存在/过短 → 视为未提供个人资料（示范答案将只生成通用版，保证零个人信息可用）。"""
    p = config.materials_dir() / "profile.md"
    try:
        t = p.read_text(encoding="utf-8").strip()
        return t if len(t) >= 40 else ""
    except Exception:
        return ""


def load_question_meta() -> dict:
    """题目元信息（中文短标题 + 生图提示词），由 scripts/gen_question_meta.py 生成。"""
    p = config.materials_dir() / "question-bank" / "meta.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


# ---------------------------------------------------------------- 示范答案

def suggestion_messages(question: str, profile: str = "", persona_title: str = "") -> list:
    stage = ""
    if persona_title:
        if "会议" in persona_title:
            stage = (
                f"【本轮场景】{persona_title}——候选人的回答是会议发言：结论先行、用数字 / 事实支撑、"
                "给出选项与建议、敢于要决策，并带上 owner 与时间点；口吻是同事间的专业沟通，不要面试腔。\n"
            )
        else:
            stage = (
                f"【本轮面试官】{persona_title}——答案的深度与口吻要对齐该轮次：HR 初面=动机与经历故事；"
                "技术面=方法、数字与判断；压力面=直接给立场、顶得住质疑。\n"
            )
    common = """你是一位坐过面试官席位（外企 / 一线大厂）的英语面试教练。产出的是「对标真实企业面试官期待、可当场说出口」的示范答案——检验标准：这段话若出现在真实面试录音里，要可信、专业、有分量；不能像求职攻略、课堂例句或背诵模板。
面试官在听什么（答案必须答到点上）：
- 结论先行：第一句给出立场 / 主句；不铺垫、不感谢、不复述问题；
- 证据链：具体方法 / 工具 / 决策 / 数字（经得起追问两层）；讲取舍时给出理由；
- 成熟度：敢承认边界、失败与替代方案；归因客观（我做的 vs 团队做的）；
- 岗位对齐：至少一处让面试官看到「这对岗位 / 公司意味着什么」。
反例（严禁出现这类 naive 特征）：
- 空洞热情与讨好："passionate about your company"、"I would love to"、"great company"；
- 学生腔："I want to learn a lot"、"I will work hard"、没有证据的 "quick learner / team player"；
- 客套铺垫："Thank you for the question"、"That's a great question"；
- 没有具体名词与数字的形容词堆砌（excellent / very / successfully）。
按问题类型选结构：
- 动机 / 公司类：具体事实（产品 / 团队 / 技术方向）→ 与我的交叉点 → 我能带来的增量；
- 行为 / 故事类：情境一句带过 → 我的动作与判断 → 结果数字 → 一句反思；
- 弱点 / 失败类：真实且可改进的点 → 正在做的具体动作 → 已有证据；
- 技术 / 观点类：立场 → 一个最硬的证据 → 边界与 trade-off。
示例（风格与深度对标；不要照抄内容）：
问题：Why did you choose this field?
❌ 天真版：I am very passionate about chemistry because it is interesting and I want to learn more in a great company.
✅ 对标版：Two things. First, I like that it's testable — when a model I built makes a prediction, the lab tells me if it's right. Second, in industry that feedback comes much faster: real data, real users. I want my work to be used, not just published.
语言与格式：
- 自然的美式职场口语，短句为主；不用 furthermore / moreover 这类书面连接词；
- 用词要常用、顺口、好发音：优先日常对话里的高频词（use / build / cut / speed up / at first / in the end 这类）；避开冷门词、生硬搭配和"炫技"同义词（orchestrate、spearhead、utilize 式表达），除非行业里就这么说；
- 答案会被人大声照着朗读（照读模式）：凡是读起来打结、拗口的句子都不要写——写完默读一遍，不顺就换成简单说法；
- 贴紧当前语境：紧扣这个问题与该轮次场景来组织和用词，问题里的关键信息（公司 / 团队 / 岗位 / 技术方向）要用得上；不跑题、不泛泛而谈；
- 纯口语文本：不要 markdown、不要标题、不要动作说明；除方括号占位符外只允许英文，严禁出现中文字符；严禁复述或提及任务说明本身（如"我需要写""候选人资料"等），直接从答案第一句开始。"""
    generic_block = """【generic（通用版）】
- 不依赖具体经历、任何候选人都能直接套用的框架答案，第一人称；
- 50–85 个英文单词，绝不超过 95 词；
- 需替换的个人信息用英文方括号占位——占位符要具体到能直接替换：如 [the company's drug-discovery platform]、[78% accuracy]、[a five-person team]、[your target role]；不要用 [your skill]、[specific strength] 这类无法替换的空洞占位；
- 语气自然、像真人在说，不是模板腔。"""
    if profile:
        sys = f"""你是一位坐过面试官席位的资深面试教练（外企 / 一线大厂）。针对同一个面试问题写两版「可直接说出口」的短示范答案，必须符合严肃的企业面试场景。

{stage}{common}

【personal（我的经历定制版）】
- 严格基于「候选人资料」中的真实经历与数字，第一人称，像本人临场作答；
- 数字与事实只能取自资料，不得虚构新的经历或数字；资料里没有合适素材时，用最相关的真实素材组织；
- 60–100 个英文单词（口语约 30–45 秒），绝不超过 110 词；
- 结构：直接回应问题 → 一个最相关的具体证据（方法 / 数字 / 结果）→ 一句收尾或留出可追问的钩子。

{generic_block}

只输出一个 JSON 对象：{{"personal": "...", "generic": "..."}}"""
        user = f"候选人资料：\n{profile}\n\n面试问题：{question}"
    else:
        sys = f"""你是一位坐过面试官席位的资深面试教练（外企 / 一线大厂）。针对一个面试问题写一版「可直接说出口」的短示范答案（通用框架版——用户尚未提供个人资料，不要编造任何具体经历），必须符合严肃的企业面试场景。

{stage}{common}

{generic_block}

只输出一个 JSON 对象：{{"generic": "..."}}"""
        user = f"面试问题：{question}"
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": user},
    ]


# ---------------------------------------------------------------- 即时反馈

FEEDBACK_SCHEMA = """{
  "verdict": "<总结（中文）：先肯定一个具体优点，再点出最关键的一条改进>",
  "score": <1-10 整数：本回答的综合表现分（内容完整性 × 表达质量 × 流利度整体印象；7=合格、8=良好、9=优秀、10=接近母语面试水准）>,
  "content_gap": "<内容层面缺什么：结构/例子/数字/立场（中文一句；照读模式填 null）>",
  "language_point": {"original": "<候选人原句片段（英文）>", "better": "<更自然或更正确的说法（英文）>", "explain": "<中文讲解 10-40 字>", "type": "grammar|vocab|structure"},
  "upgrade": {"original": "<候选人原句片段（英文）>", "better": "<不装但更高级的说法（英文）>", "explain": "<中文讲解>", "type": "vocab|structure"},
  "polished": "<把整段回答润色为自然的英文口语版：保留信息与观点，修正语法/用词/结构，可直接照着说；自由说模式必填，照读模式填 null>",
  "followup": "<作为面试官（角色A）的下一句追问（英文，≤25 词；口语、可直接对候选人说出口，会被语音朗读）；没有就填 null>"
}"""


def feedback_messages(persona: dict, question: str, transcript: str, history: list, mode: str = "free", script: str = "") -> list:
    mode_block = ""
    if mode == "read":
        mode_block = (
            "\n\n【本次为「照读模式」】：候选人是照着下面的示范答案朗读的（可能有漏读/改读）。\n"
            "- content_gap 填 null；不要给内容建议。\n"
            "- 聚焦朗读表现：与脚本的差异（漏读、改读、添词）、发音清晰度、节奏与停顿、语调。\n"
            "- polished 填 null。\n"
            "- verdict 仍要有：先说朗读优点，再给 1 条最关键改进。\n"
            "【示范答案（供对比）】：\n" + (script or "")[:2500]
        )
    meeting = "会议" in (persona.get("title") or "")
    scene = "会议发言" if meeting else "面试回答"
    role_a = "会议主持人" if meeting else "面试官"
    role_b = (
        "【角色B · 隐形教练】为一名中文母语的学习者提供英文职场会议口语反馈：候选人的发言发生在跨国企业的工作会议上；"
        "反馈要围绕「会议场景下的表达」（结论先行、数字支撑、给出选项与建议、行动项闭环），而不是面试话术。"
        if meeting
        else "【角色B · 隐形教练】为一名中文母语的化学博士提供英文面试口语训练反馈（目标：技术面试流利自如）。"
    )
    probe_style = (
        "追问上一答里最值得追的一点（缺数字、缺 owner、缺时间点、风险没说透、决策含糊等），方向符合角色A 的主持人身份（主持人追数字、owner、deadline 与决策）。"
        if meeting
        else "追问上一答里最值得追的一点（缺数字、缺个人贡献、逻辑跳跃、夸大表述等），方向符合角色A 的轮次身份（HR 追动机与行为细节；技术官追方法与数字；压力官质疑漂亮话）。"
    )
    sys = f"""你同时扮演两个角色，为同一段{scene}产出一次反馈。

【角色A · {role_a}】{persona.get('system', '')}

{role_b}
硬性要求：
- 严格基于候选人原话，不得虚构错误；句子没问题时不要鸡蛋里挑骨头，改为"升级"建议。
- 转写可能含语音识别噪声：若某词只出现一次、形态怪异（例如把标准术语转成了不存在的拼写），不要当作候选人的语言错误（可跳过该点）。
- 字段语言：verdict/explain 用中文；original/better/followup/polished 用英文。
- followup 是角色A（{role_a}）真实的下一个回合：像现场一样先给一个简短反应再追问（反应可省略），不超过 25 词，必须能直接说出口；{probe_style}回答完整且具体时可为 null。
- followup 引用的内容只能来自候选人原话：严禁虚构对方没有说过的事实、数字或细节（要数字就直接要，不要去猜一个数字）。
- 只输出一个 JSON 对象，不要解释、不要 markdown 代码块。结构：
{FEEDBACK_SCHEMA}{mode_block}"""
    msgs = [{"role": "system", "content": sys}]
    for h in (history or [])[-6:]:
        msgs.append({"role": "user", "content": f"[面试官] {h.get('question', '')}"})
        msgs.append({"role": "user", "content": f"[候选人·转写] {h.get('transcript', '')}"})
    msgs.append({"role": "user", "content": f"[面试官] {question}\n\n[候选人·转写（ASR 自动识别，可能有转写误差）]\n{transcript}\n\n请按 JSON 输出反馈。"})
    return msgs


# ---------------------------------------------------------------- 收场复盘

def review_messages(persona: dict, qa_list: list) -> list:
    sys = """你是英语面试教练。基于整场会话记录产出复盘报告（中文为主，例句保留英文）。
只输出一个 JSON 对象，结构：
{
 "scores": {"content": 1-5, "structure": 1-5, "grammar": 1-5, "lexical": 1-5, "fluency": 1-5},
 "strengths": ["最多3条"],
 "issues": [{"type": "grammar|vocab|structure|content|delivery", "pattern": "反复出现的问题", "example": "原句（英文）", "fix": "怎么改"}],
 "drills": ["下次训练前要练的 3 件事"],
 "next_focus": "下一次会话重点（一句话）"
}
要求：issues 按出现频率排序、最多 5 条；所有判断必须引用具体句子；不要客套话。"""
    body = []
    for i, qa in enumerate(qa_list, 1):
        dur = (qa.get("duration_ms") or 0) / 1000
        mode = "照读" if qa.get("mode") == "read" else "自由说"
        body.append(f"Q{i}: {qa.get('question', '')}\nA{i}（{mode}）: {qa.get('transcript', '')}\n(用时 {dur:.0f}s)")
    return [{"role": "system", "content": sys}, {"role": "user", "content": "\n\n".join(body)}]


# ---------------------------------------------------------------- 单词速查（Speakey 式点词）

def gloss_messages(word: str, context: str) -> list:
    sys = """你是面向中文母语者的英语学习词典。用户会给你一个单词/短语和它出现的上下文（面试场景）。
输出一个 JSON 对象：
{
 "word": "<原词或短语>",
 "ipa": "<美式音标，不含斜杠>",
 "pos": "<词性简写：n./v./adj./adv./phrase/其他>",
 "zh": "<结合此上下文最贴切的中文释义（10-30 字）>",
 "example_en": "<一个面试场景中的简短英文例句>",
 "example_zh": "<例句中文翻译>",
 "note": "<可选：用法/搭配/易混提醒（中文，20 字内；没有则空字符串）>"
}
只输出 JSON，不要任何解释。"""
    return [
        {"role": "system", "content": sys},
        {"role": "user", "content": f"单词：{word}\n上下文（面试回答片段）：{(context or '')[:600]}"},
    ]

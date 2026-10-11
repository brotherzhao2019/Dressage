"""Render the example's architecture figures; requires PyGObject and librsvg."""

from html import escape
from pathlib import Path

import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg

ROOT = Path(__file__).resolve().parent
BLUE, TEAL, INK, MUTED = "#3569C8", "#188579", "#1C2D47", "#62738A"


class Diagram:
    def __init__(self, height, title, subtitle, font="DejaVu Sans, sans-serif"):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="{height}" viewBox="0 0 1320 {height}">',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>',
            '<rect width="100%" height="100%" fill="#FAFCFF"/>',
            f'<g font-family="{escape(font, quote=True)}">',
        ]
        self.text(44, 54, title, 29, INK)
        self.text(44, 90, subtitle, 17)

    def text(self, x, y, text, size=18, color=MUTED, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{escape(text)}</text>')

    def box(self, x, y, w, h, title, lines, color=BLUE, fill="white"):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="#DCE5F0"/>')
        self.parts.append(f'<rect x="{x+18}" y="{y+20}" width="5" height="23" rx="2" fill="{color}"/>')
        self.text(x+34, y+39, title, 21, INK)
        for i, line in enumerate(lines):
            self.text(x+24, y+73+29*i, line, 16)

    def arrow(self, x1, y1, x2, y2, color=BLUE):
        self.parts.append(f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{color}" stroke-width="2.5" fill="none" marker-end="url(#arrow)"/>')

    def save(self, name, scale=1):
        svg = "\n".join(self.parts + ["</g></svg>"])
        (ROOT/f"{name}.svg").write_text(svg)
        raster = svg.replace(
            f'width="1320" height="{self.height}"',
            f'width="{int(1320 * scale)}" height="{int(self.height * scale)}"',
            1,
        )
        Rsvg.Handle.new_from_data(raster.encode()).get_pixbuf().savev(str(ROOT/f"{name}.png"), "png", [], [])


d = Diagram(765, "Dressage DistRoll", "A self-managed CPU execution pool, separate from GPU inference and training")
d.box(40, 125, 500, 510, "GPU cluster", ["Containerized training; no task Docker daemon"], fill="#EFF4FF")
d.box(780, 125, 500, 510, "CPU rollout cluster", ["Harbor tasks on user-managed worker hosts"], TEAL, "#EDF8F4")
d.box(64, 232, 452, 180, "GPU Head", ["RL queue, group selection, early stop", "Policy routes and request deduplication", "Dressage Proxy: TITO and native TQ"])
d.box(804, 232, 452, 180, "CPU Head", ["Control: admission and execution state", "Worker-facing Policy gateway", "PostgreSQL and image Registry"], TEAL)
d.arrow(516, 267, 804, 267)
d.text(660, 251, "Execution control", 17, BLUE, "middle")
d.text(660, 293, "reserve / query / cancel / ACK", 12, MUTED, "middle")
d.arrow(804, 334, 516, 334, TEAL)
d.text(660, 317, "Route lifecycle", 17, TEAL, "middle")
d.text(660, 360, "bind / open / seal / revoke", 12, MUTED, "middle")
d.arrow(804, 400, 516, 400, TEAL)
d.text(660, 383, "Model requests", 17, TEAL, "middle")
d.text(660, 427, "Complete responses return to CPU", 12, MUTED, "middle")
for x, title, lines, color in [
    (64, "Actor nodes", ["Loss and optimizer", "Checkpoints"], BLUE),
    (304, "Inference", ["Model generation", "Weight updates"], BLUE),
    (804, "Worker 1", ["Harbor / Agent", "Verifier / sandbox"], TEAL),
    (1044, "Worker N", ["Image cache", "Sandbox protection"], TEAL),
]:
    d.arrow(x+105, 426, x+105, 468, color)
    d.box(x, 477, 212, 127, title, lines, color)
d.text(44, 686, "Only the Heads cross the cluster boundary. Workers and ranks use internal networks.")
d.text(44, 724, "The link is reachable but may stall or disconnect; application protocols handle bounded recovery.")
d.save("architecture")

d = Diagram(
    1320,
    "From one rollout slot to a training update",
    "Reserve CPU capacity first. Bind model access only after a Worker creates a real trial.",
)
lanes = [190, 503, 816, 1129]

# Light phase bands provide structure without competing with the call arrows.
for y, height, label, fill, color in [
    (231, 272, "ADMIT", "#F0F5FE", BLUE),
    (511, 202, "EXECUTE", "#EDF7F4", TEAL),
    (721, 272, "DELIVER", "#F0F5FE", BLUE),
]:
    d.parts.append(f'<rect x="44" y="{y}" width="1232" height="{height}" rx="16" fill="{fill}"/>')
    d.text(59, y+23, label, 11, color)

for i, (x, name, detail) in enumerate(zip(
    lanes,
    ["RL queue", "CPU Control", "CPU Worker", "GPU Policy / Proxy"],
    ["Candidates & groups", "Capacity & results", "Harbor execution", "Routes & trajectories"],
)):
    color = TEAL if i in (1, 2) else BLUE
    d.parts.append(f'<path d="M{x},211 L{x},979" stroke="#C7D5E5" stroke-width="1.6" stroke-dasharray="4 7"/>')
    d.parts.append(f'<rect x="{x-130}" y="132" width="260" height="78" rx="13" fill="#E5ECF5" opacity="0.55"/>')
    d.parts.append(f'<rect x="{x-130}" y="128" width="260" height="78" rx="13" fill="white" stroke="#D9E3EE"/>')
    d.parts.append(f'<rect x="{x-130}" y="144" width="4" height="46" rx="2" fill="{color}"/>')
    d.text(x, 159, name, 20, INK, "middle")
    d.text(x, 186, detail, 13, MUTED, "middle")

events = [
    (0, 1, "Reserve capacity", "Atomic admission", False),
    (0, 3, "Prepare model context", "Only after reservation succeeds", False),
    (0, 1, "Activate execution", "Hand off the admitted task", False),
    (2, 1, "Claim execution", "Check ownership and configuration", False),
    (2, 3, "Bind / open route", "After creating the Harbor trial", False),
    (2, 3, "Model requests", "Tools run in the CPU sandbox", False),
    (2, 1, "Report verified result", "Persist in outbox before delivery", False),
    (1, 0, "Return queried result", "Response to RL polling", True),
    (0, 3, "Finalize and read trajectory references", "Validate identity, tokens, loss masks and weight version", False),
    (0, 1, "ACK result", "Acknowledge receipt, not training", False),
    (0, 3, "Detach model route", "Generation ends; selected source TQ remains available", False),
]
for i, (source, target, label, detail, reply) in enumerate(events):
    y = 274 + i*68
    x1, x2 = lanes[source], lanes[target]
    center = (x1+x2)/2
    color = BLUE if source == 0 else TEAL
    dash = ' stroke-dasharray="6 4"' if reply else ""
    d.parts.append(f'<path d="M{x1},{y} L{x2},{y}" stroke="{color}" stroke-width="2.6" fill="none"{dash} marker-end="url(#arrow)"/>')
    d.parts.append(f'<circle cx="{x1}" cy="{y}" r="3.7" fill="{color}"/>')
    d.text(center, y-13, f"{i+1:02d}  {label}", 16, color, "middle")
    d.text(center, y+22, detail, 12, MUTED, "middle")

d.parts.append('<rect x="60" y="1014" width="1200" height="80" rx="14" fill="#FFF6E5" stroke="#F0DCB5"/>')
d.text(84, 1045, "Cleanup barrier & group selection", 21, "#92631D")
d.text(84, 1073, "Verify CPU cleanup and idle GPU generations. Early stop must settle surplus executions too.", 16, "#846E49")

stages = [
    ("Read native TQ", "All selected training ranks"),
    ("Update model", "Loss / backward / optimizer"),
    ("Release source keys", "After every rank finishes"),
    ("Publish weights", "Checkpoint when due"),
]
for i, (title, detail) in enumerate(stages):
    x = 60+i*313
    d.box(x, 1130, 260, 106, title, [detail], BLUE, "#EFF4FF")
    if i < len(stages)-1:
        d.arrow(x+267, 1183, x+305, 1183)
d.text(60, 1270, "No capacity: wait in the RL queue. Result ACK, batch delivery and optimizer completion are distinct.", 15)
d.text(60, 1298, "Logical service calls shown; CPU Head forwards Worker traffic across clusters. Most response arrows are omitted.", 13)
d.save("lifecycle", scale=1.5)


def render_reliability(language):
    if language == "zh-CN":
        title = "两种请求，两套去重机制"
        subtitle = "传输重试保持业务身份；不重复启动任务，不把响应重放变成另一次生成"
        headings = ["GPU → CPU：任务控制", "CPU → GPU：模型调用"]
        cards = [
            ("1  RL固定执行与预留请求身份", [
                "execution ID + 预留请求身份 + 请求内容",
                "回复丢失：用原身份重试或回查",
                "不为传输重试另建execution",
            ]),
            ("2  Control数据库原子处理", [
                "同身份同内容：复用预留 / 当前状态",
                "同身份内容冲突：拒绝",
                "容量不足：429，继续在RL侧等待",
            ]),
            ("3  持久结果outbox与ACK", [
                "Worker先落结果，再交付Control",
                "同execution / digest重发可去重",
                "RL接收后ACK，不重跑Agent",
            ]),
            ("1  Worker本地Relay固定调用身份", [
                "request ID + 原请求字节 + digest",
                "经CPU Head转发；传输重试不换身份",
                "另一独立调用使用新的request ID",
            ]),
            ("2  GPU Policy请求账本", [
                "键：route ID + request ID",
                "同身份同内容：共享在途生成 / 完整响应",
                "同身份内容冲突：拒绝",
            ]),
            ("3  完整响应返回Agent", [
                "回复丢失：同一请求取回原响应字节",
                "重放不重复生成，也不拼接不同响应",
                "独立响应独立message ID，重放不变",
            ]),
        ]
        boundary = "两条通道汇合到训练交付边界"
        checks = [
            "CPU清理证明 + GPU旧generation关闭 + 轨迹身份 / token / mask / 权重版本检查",
            "RL选组 → 原生TQ交付训练rank；全部rank消费后才释放入选源key",
        ]
        footnotes = [
            "传输恢复有预算；耗尽或清理无法证实则明确失败，不使用不确定轨迹训练。",
            "模型账本有界且在进程内；相同内容不等于同一次调用，ACK不等于optimizer完成。",
        ]
        font, body_size = "Noto Sans CJK SC, sans-serif", 18
    else:
        title = "Two request paths, two deduplication mechanisms"
        subtitle = "Retries preserve identity: no duplicate task launch or extra generation from response replay"
        headings = ["GPU → CPU: execution control", "CPU → GPU: model calls"]
        cards = [
            ("1  RL freezes execution identity", [
                "execution ID + reservation request ID + content",
                "Lost reply: retry or query with the same identity",
                "A transport retry does not create a new execution",
            ]),
            ("2  Control handles requests atomically", [
                "Same identity and content: reuse reservation / state",
                "Same identity, different content: reject",
                "No capacity: return 429; wait in the RL queue",
            ]),
            ("3  Durable result outbox and ACK", [
                "Worker persists the result, then delivers to Control",
                "Deduplicate by execution identity and result digest",
                "RL acknowledges receipt; the Agent is not rerun",
            ]),
            ("1  Worker Relay freezes each call", [
                "request ID + original request bytes + digest",
                "CPU Head forwards; transport retries retain identity",
                "An independent call gets a new request ID",
            ]),
            ("2  GPU Policy request ledger", [
                "Key: route ID + request ID",
                "Matching retry: share generation / complete response",
                "Same identity, different content: reject",
            ]),
            ("3  Return one complete response", [
                "Lost reply: replay the original response bytes",
                "No extra generation or mixed response fragments",
                "Distinct response: new message ID; replay: same ID",
            ]),
        ]
        boundary = "Both paths meet at the training-delivery boundary"
        checks = [
            "Verify CPU cleanup, idle GPU generations, trajectory identity, tokens, loss masks and weight version.",
            "Select groups → native TQ references → release selected source keys only after all training ranks finish.",
        ]
        footnotes = [
            "Recovery is bounded. Exhaustion or unverified cleanup fails; uncertain trajectories cannot train.",
            "Bounded in-memory model ledger; equal content is not equal identity. ACK is not an optimizer update.",
        ]
        font, body_size = "DejaVu Sans, sans-serif", 16

    d = Diagram(1140, title, subtitle, font)
    for column, (heading, color, fill) in enumerate(zip(
        headings, [BLUE, TEAL], ["#EFF4FF", "#EDF8F4"],
    )):
        x = 40 + column * 645
        d.box(x, 135, 595, 750, heading, [], color, fill)
        for row in range(3):
            y = 215 + row * 225
            card_title, lines = cards[column * 3 + row]
            d.box(x + 25, y, 545, 165, card_title, [], color)
            for i, line in enumerate(lines):
                d.text(x + 49, y + 79 + i * 31, line, body_size)
            if row < 2:
                d.arrow(x + 297, y + 177, x + 297, y + 211, color)
    d.box(40, 915, 1240, 135, boundary, [], BLUE, "#EFF4FF")
    for i, line in enumerate(checks):
        d.text(64, 994 + i * 31, line, body_size)
    for i, line in enumerate(footnotes):
        d.text(48, 1085 + i * 32, line, body_size - 1)
    d.save("reliability" + (".zh-CN" if language == "zh-CN" else ""), scale=1.5)


render_reliability("zh-CN")
render_reliability("en")

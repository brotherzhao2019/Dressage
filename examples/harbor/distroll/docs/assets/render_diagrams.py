"""Render the example's architecture figures; requires PyGObject and librsvg."""

from html import escape
from pathlib import Path

import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg

ROOT = Path(__file__).resolve().parent
BLUE, TEAL, INK, MUTED = "#3569C8", "#188579", "#1C2D47", "#62738A"


class Diagram:
    def __init__(self, height, title, subtitle):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="{height}" viewBox="0 0 1320 {height}">',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>',
            '<rect width="100%" height="100%" fill="#FAFCFF"/>',
            '<g font-family="DejaVu Sans, sans-serif">',
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

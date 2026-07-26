"""inspector.py — full-screen deep mind inspector overlay (Arc A / A2, "The Glass Box").

Toggled with V; shows the TAB-selected subject's *complete* internal state — every
chemical, every drive (+ which is winning), the full memory (per-source EMAs,
per-region comfort), affinity, traits, needs, vitals — laid out in three columns.
Read-only; renders the current live state each frame (composes with the sim freeze
[P] and, later, rewind). For the player (no NPC controller) the mind columns are
simply omitted.
"""
from __future__ import annotations

# noinspection PyPackageRequirements
import pygame
import settings
from Mechanics.needs.need import NeedZone

_BG   = (12, 12, 18, 232)
_HDR  = (255, 225, 120)
_SEC  = (150, 200, 255)
_VAL  = (225, 225, 235)
_DIM  = (110, 110, 130)
_GOOD = (130, 200, 130)
_LINE = 17


def _fields(obj) -> dict:
    """Best-effort {name: value} for a small data object (attributes/traits)."""
    if obj is None:
        return {}
    if hasattr(obj, "as_dict"):
        try:
            return obj.as_dict()
        except Exception:
            pass
    d = getattr(obj, "__dict__", None)
    return {k: v for k, v in d.items() if not k.startswith("_")} if d else {}


def draw_inspector(surface, entity, controller, needs, font) -> None:
    W, H = surface.get_size()
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill(_BG)
    surface.blit(overlay, (0, 0))

    cols: dict[int, int] = {}

    def line(x, text, color=_VAL):
        surface.blit(font.render(text, True, color), (x, cols[x]))
        cols[x] += _LINE

    def sec(x, title):
        cols[x] += 6
        surface.blit(font.render(title, True, _SEC), (x, cols[x]))
        cols[x] += _LINE

    C1, C2, C3 = 40, 372, 704
    for x in (C1, C2, C3):
        cols[x] = 30

    # --- Title ---
    subtype = getattr(entity, "subtype", "?")
    state = controller.state if controller is not None else "PLAYER"
    tgt = getattr(getattr(controller, "target_source", None), "label", None) if controller else None
    title = (f"MIND INSPECTOR   {entity.name} [{subtype}]   state: {state}"
             + (f"   -> {tgt}" if tgt else ""))
    surface.blit(font.render(title, True, _HDR), (C1, 6))

    # --- Column 1: vitals + attributes ---
    sec(C1, "- VITALS -")
    line(C1, f"HP   {entity.hp:.0f}/{entity.max_hp}")
    line(C1, f"SP   {entity.cycles}/{entity.max_cycles}")
    line(C1, f"Bit  {entity.bit_pool}/{entity.max_bit_pool}")
    line(C1, f"Byte {entity.byte_pool}/{entity.max_byte_pool}")
    line(C1, f"pos  ({entity.x:.0f}, {entity.y:.0f})", _DIM)
    sec(C1, "- ATTRIBUTES -")
    for k, v in _fields(getattr(entity, "attributes", None)).items():
        vs = f"{v:.2f}" if isinstance(v, float) else str(v)
        line(C1, f"{k:<14}{vs}")

    # --- Column 2: needs + affinity + traits ---
    sec(C2, "- NEEDS -")
    for need in needs:
        z = getattr(need, "zone", None)
        zname = z.name if z is not None else ""
        zcolor = (settings.COLOR_CRITICAL if z == NeedZone.CRITICAL
                  else settings.COLOR_WARNING if z == NeedZone.WARNING else _VAL)
        label = getattr(need, "label", getattr(need, "need_id", "?"))
        line(C2, f"{label:<10}{need.current_value:6.1f}  {zname}", zcolor)

    sec(C2, "- AFFINITY -")
    aff = getattr(entity, "affinity", None)
    if aff is not None:
        innate = aff.innate.value if getattr(aff, "innate", None) is not None else "neutral"
        line(C2, f"innate   {innate}")
        try:
            cur = ", ".join(a.value for a in aff.current())
            line(C2, f"current  {cur or '-'}", _DIM)
        except Exception:
            pass
    if controller is not None:
        line(C2, f"comfort  {getattr(controller, 'affinity_comfort', 0.0):+.3f}")
        line(C2, f"strain   {controller.brain.chemicals.get('affinity_strain'):.3f}")

    sec(C2, "- TRAITS -")
    for k, v in _fields(getattr(entity, "traits", None)).items():
        vs = f"{v:.2f}" if isinstance(v, float) else str(v)
        line(C2, f"{k:<14}{vs}")

    # --- Column 3: the mind (NPC only) ---
    if controller is not None:
        brain = controller.brain
        chem = brain.chemicals

        sec(C3, "- BIOCHEM (all) -")
        for k, v in chem.as_dict().items():
            line(C3, f"{k:<16}{v:+.3f}", _VAL if abs(v) > 0.05 else _DIM)

        sec(C3, "- DRIVES -")
        urg = [(d.need_id, d.compute_urgency(chem, brain.traits)) for d in brain.drives]
        winner = max(urg, key=lambda t: t[1])[0] if urg else None
        for need_id, u in urg:
            mark = " <=" if need_id == winner else ""
            color = (settings.COLOR_CRITICAL if u > 0.7
                     else settings.COLOR_WARNING if u > 0.4 else _DIM)
            line(C3, f"{need_id:<10}{u:.3f}{mark}", color)

        mem = controller.memory
        sec(C3, "- MEMORY: sources -")
        srcs = getattr(mem, "_sources", {})
        if srcs:
            for label, e in srcs.items():
                line(C3, f"{label:<10}{e.avg_satisfaction:.2f} (x{e.visit_count})", _DIM)
        else:
            line(C3, "(none yet)", _DIM)

        sec(C3, "- MEMORY: regions -")
        regs = getattr(mem, "_regions", {})
        if regs:
            for rid, e in regs.items():
                line(C3, f"{rid:<12}{e.avg_comfort:+.2f} (x{e.visit_count})", _DIM)
        else:
            line(C3, "(none yet)", _DIM)
        best = mem.best_region()
        if best:
            line(C3, f"best: {best[0]} {best[1]:+.2f}", _GOOD)

    # --- footer ---
    surface.blit(
        font.render("[V] close   [TAB] change subject   [P] freeze   [.] step",
                    True, _DIM),
        (C1, H - 24))

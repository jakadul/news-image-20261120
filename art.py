"""Flat editorial illustrations drawn from primitives.

The pages that win this contest are not made of type alone: each lead carries a
flat vector drawing built out of rectangles, polygons, ellipses and lines. This
module does the same thing with the standard library only - every function here
takes the drawing surface plus a box and paints inside it, in the fixed palette
below, with no gradients, no textures and no images read from disk.

Each function is one news picture, so a page can mix them:

    bridge(c, x, y, w, h)      a struck road bridge over water
    radar(c, x, y, w, h)       a radar dome on a lattice tower
    flags(c, x, y, w, h)       four flagpoles at a summit
    tank(c, x, y, w, h)        armour pushing across a line
    cyclone(c, x, y, w, h)     a spiral storm over sea
    spaceprobe(c, x, y, w, h)  a probe against a star field
    caps(c, x, y, w, h)        a classical building with columns
    chart(c, x, y, w, h)       rising bars for a markets story
    portrait(c, x, y, w, h)    a head-and-shoulders silhouette
    press(c, x, y, w, h)       a printing press / newspapers
"""

# A small flat palette: sky, sea, land, stone, ink, warning colours.
SKY = (176, 205, 224)
SEA = (58, 116, 158)
DEEP = (36, 78, 112)
LAND = (206, 188, 158)
STONE = (176, 174, 168)
STONE_D = (128, 126, 122)
INK = (34, 34, 38)
WHITE = (250, 249, 246)
RED = (176, 32, 42)
ORANGE = (222, 118, 42)
YELLOW = (240, 190, 70)
GREEN = (74, 122, 84)
NAVY = (32, 52, 88)
PURPLE = (94, 68, 122)
SMOKE = (86, 84, 88)
SMOKE_L = (146, 144, 148)


def _line(c, x0, y0, x1, y1, fill=INK, width=1.0):
    """PageCanvas wraps segments as rule(); this keeps the call sites short."""
    c.rule(x0, y0, x1, y1, width=width, fill=fill)


def _mix(a, b, t):
    return (int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t))


def panel(c, x, y, w, h, sky=SKY, sea=None, sea_h=0.42):
    """Background: flat sky, and optionally a band of water under it."""
    c.rect(x, y, x + w, y + h, fill=sky)
    if sea is not None:
        c.rect(x, y + h * (1.0 - sea_h), x + w, y + h, fill=sea)


def bridge(c, x, y, w, h, struck=True):
    """A two-tower road bridge over water, one deck span missing.

    The break is shown by absence - a gap in the deck with the severed end
    dropping - rather than by covering the middle with smoke, which is what made
    the earlier version unreadable.
    """
    panel(c, x, y, w, h, sky=SKY, sea=SEA, sea_h=0.38)
    deck_y = y + h * 0.50
    deck_h = h * 0.06
    tower_top = y + h * 0.10
    # towers, tall and unmistakable
    for tx in (0.30, 0.70):
        px = x + w * tx
        c.rect(px - w * 0.016, tower_top, px + w * 0.016, y + h * 0.86, fill=STONE_D)
        # cross beam
        c.rect(px - w * 0.055, tower_top + h * 0.07, px + w * 0.055,
               tower_top + h * 0.11, fill=STONE_D)
    # deck: three pieces, with the middle-left one missing when struck
    seg = ((0.00, 0.34), (0.40, 0.66), (0.72, 1.00)) if struck else (
           (0.00, 0.34), (0.34, 0.66), (0.66, 1.00))
    for a, b in seg:
        c.rect(x + w * a, deck_y, x + w * b, deck_y + deck_h, fill=STONE)
    # suspender cables from the towers to the deck
    for tx in (0.30, 0.70):
        px = x + w * tx
        for i in range(1, 7):
            off = w * 0.055 * i
            if px - off > x:
                _line(c, px, tower_top + h * 0.12, px - off, deck_y,
                      fill=STONE_D, width=1.0)
            if px + off < x + w:
                _line(c, px, tower_top + h * 0.12, px + off, deck_y,
                      fill=STONE_D, width=1.0)
    if struck:
        # the severed span, tilted into the water like a ramp, not a pendulum
        c.polygon([(x + w * 0.34, deck_y),
                   (x + w * 0.40, deck_y),
                   (x + w * 0.475, y + h * 0.74),
                   (x + w * 0.425, y + h * 0.755)], fill=STONE)
        # two small puffs at water level, well clear of the span
        for dx, r in ((0.36, 0.035), (0.39, 0.028)):
            c.dot(x + w * dx, y + h * 0.845, w * r, fill=SMOKE_L)
        c.dot(x + w * 0.375, y + h * 0.83, w * 0.022, fill=ORANGE)
    # waterline detail
    for i in range(5):
        _line(c, x + w * (0.04 + i * 0.20), y + h * 0.93,
              x + w * (0.10 + i * 0.20), y + h * 0.93,
              fill=_mix(SEA, WHITE, 0.45), width=1.2)


def radar(c, x, y, w, h):
    """A wide, flat radome on a tall triangular lattice tower, a ship, drones.

    The dome is deliberately wide and shallow and the tower legs are drawn as two
    straight members meeting at the apex, so the silhouette reads as a radar mast
    rather than as a parachute or a mushroom.
    """
    panel(c, x, y, w, h, sky=_mix(SKY, WHITE, 0.25), sea=SEA, sea_h=0.26)
    c.polygon([(x, y + h * 0.74), (x + w * 0.46, y + h * 0.70),
               (x + w * 0.50, y + h), (x, y + h)], fill=LAND)
    apex_x = x + w * 0.26
    apex_y = y + h * 0.40
    lx = x + w * 0.13
    rx = x + w * 0.39
    base_y = y + h * 0.76
    # two main legs plus a centre post: a mast, not a tent
    _line(c, lx, base_y, apex_x, apex_y, fill=STONE_D, width=3.2)
    _line(c, rx, base_y, apex_x, apex_y, fill=STONE_D, width=3.2)
    _line(c, apex_x, base_y, apex_x, apex_y, fill=STONE_D, width=1.8)
    # horizontal braces and one cross brace
    for t in (0.30, 0.62, 0.88):
        _line(c, lx + (apex_x - lx) * t, base_y + (apex_y - base_y) * t,
              rx + (apex_x - rx) * t, base_y + (apex_y - base_y) * t,
              fill=STONE_D, width=1.4)
    _line(c, lx, base_y, apex_x, apex_y + h * 0.10, fill=STONE_D, width=1.0)
    c.rect(lx - w * 0.02, base_y, rx + w * 0.02, base_y + h * 0.035, fill=INK)
    # wide shallow radome
    dr = w * 0.155
    c.ellipse(apex_x - dr, apex_y - dr * 0.52, apex_x + dr, apex_y + dr * 0.52,
              fill=WHITE, outline=STONE_D, width=1.6)
    # the antenna on top of the radome, short so it reads as a fitting
    c.rect(apex_x - dr * 0.06, apex_y - dr * 0.95, apex_x + dr * 0.06,
           apex_y - dr * 0.50, fill=STONE_D)
    # ship
    sx = x + w * 0.66
    sy = y + h * 0.74
    c.polygon([(sx, sy), (sx + w * 0.27, sy - h * 0.012),
               (sx + w * 0.24, sy + h * 0.095), (sx + w * 0.04, sy + h * 0.105)],
              fill=INK)
    c.rect(sx + w * 0.10, sy - h * 0.065, sx + w * 0.17, sy, fill=WHITE,
           outline=STONE_D, width=1.0)
    # drones: body + swept wings + tail, red so they read at small size
    for dx, dy in ((0.55, 0.14), (0.66, 0.23), (0.77, 0.11)):
        cx = x + w * dx
        cy = y + h * dy
        c.polygon([(cx - w * 0.045, cy), (cx, cy - h * 0.012),
                   (cx + w * 0.045, cy), (cx, cy + h * 0.012)], fill=RED)
        _line(c, cx, cy - h * 0.012, cx, cy + h * 0.012, fill=RED, width=1.6)
        _line(c, cx, cy + h * 0.012, cx + w * 0.018, cy + h * 0.030,
              fill=RED, width=1.2)


def flags(c, x, y, w, h):
    """A summit: two figures at a table, four national flags behind them.

    The earlier version was four bare rectangles on poles, which read as
    unidentifiable colour blocks. Adding the two seated figures and a long table
    gives the picture a scene, so the flags become background rather than the
    whole subject.
    """
    panel(c, x, y, w, h, sky=_mix(PURPLE, WHITE, 0.78))
    # backdrop wall
    c.rect(x, y + h * 0.34, x + w, y + h * 0.34 + h * 0.30, fill=_mix(PURPLE, WHITE, 0.62))
    # four flags, tall and evenly spaced, behind the table
    for i in range(4):
        px = x + w * (0.14 + i * 0.24)
        _line(c, px, y + h * 0.10, px, y + h * 0.62, fill=STONE_D, width=2.2)
        col = (NAVY, RED, WHITE, GREEN)[i]
        c.rect(px + 1.5, y + h * 0.12, px + w * 0.15, y + h * 0.30, fill=col,
               outline=_mix(col, INK, 0.35), width=0.8)
        # a second band so each flag reads as a flag rather than a card
        c.rect(px + 1.5, y + h * 0.12, px + w * 0.15, y + h * 0.18,
               fill=_mix(col, WHITE, 0.55))
    # the table
    c.rect(x + w * 0.10, y + h * 0.64, x + w * 0.90, y + h * 0.74, fill=STONE_D)
    c.rect(x + w * 0.10, y + h * 0.74, x + w * 0.90, y + h * 0.78, fill=_mix(STONE_D, INK, 0.4))
    # two seated figures, left and right, facing each other
    for fx, flip in ((0.30, 1), (0.70, -1)):
        cx = x + w * fx
        c.ellipse(cx - w * 0.045, y + h * 0.40, cx + w * 0.045, y + h * 0.54, fill=INK)
        c.polygon([(cx - w * 0.075, y + h * 0.66), (cx - w * 0.055, y + h * 0.55),
                   (cx + w * 0.055, y + h * 0.55), (cx + w * 0.075, y + h * 0.66)],
                  fill=INK)
    # microphones on the table
    for mx in (0.46, 0.54):
        _line(c, x + w * mx, y + h * 0.64, x + w * mx, y + h * 0.56, fill=INK, width=1.6)
        c.dot(x + w * mx, y + h * 0.55, w * 0.010, fill=RED)


def tank(c, x, y, w, h):
    """Armour on a dusty plain, with a marked line in the sand."""
    panel(c, x, y, w, h, sky=_mix(LAND, WHITE, 0.55))
    c.rect(x, y + h * 0.62, x + w, y + h, fill=_mix(LAND, ORANGE, 0.18))
    # the marked line
    for i in range(9):
        _line(c, x + w * (0.04 + i * 0.11), y + h * 0.72,
               x + w * (0.09 + i * 0.11), y + h * 0.76, fill=RED, width=2.0)
    # hull
    hx = x + w * 0.22
    hy = y + h * 0.56
    c.rect(hx, hy, hx + w * 0.44, hy + h * 0.10, fill=STONE_D)
    # tracks
    c.rect(hx, hy + h * 0.10, hx + w * 0.44, hy + h * 0.17, fill=INK)
    for i in range(7):
        cx = hx + w * 0.03 + i * w * 0.06
        c.dot(cx, hy + h * 0.135, h * 0.022, fill=STONE)
    # turret and barrel
    c.rect(hx + w * 0.14, hy - h * 0.08, hx + w * 0.30, hy, fill=STONE)
    _line(c, hx + w * 0.29, hy - h * 0.04, hx + w * 0.50, hy - h * 0.06,
           fill=STONE_D, width=2.4)
    # dust
    for i in range(4):
        c.ellipse(hx - w * (0.02 + i * 0.03), hy + h * 0.02 + i * h * 0.02,
                  hx + w * 0.06, hy + h * 0.16 + i * h * 0.02,
                  fill=_mix(LAND, WHITE, 0.4))


def cyclone(c, x, y, w, h):
    """A storm spiral over a dark sea: arms drawn as arcs of a shrinking radius."""
    import math
    panel(c, x, y, w, h, sky=_mix(DEEP, SMOKE, 0.5), sea=DEEP, sea_h=0.24)
    cx = x + w * 0.50
    cy = y + h * 0.44
    # three arms, each a spiral of short segments so the curl reads at a glance
    for arm in range(3):
        a0 = arm * (2.0 * math.pi / 3.0)
        pts = []
        for i in range(40):
            t = i / 39.0
            ang = a0 + t * 3.6
            r = w * (0.045 + 0.34 * t)
            pts.append((cx + math.cos(ang) * r,
                        cy + math.sin(ang) * r * 0.66))
        for i in range(len(pts) - 1):
            shade = _mix(WHITE, DEEP, i / float(len(pts)))
            _line(c, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                  fill=shade, width=2.6 - 1.6 * (i / float(len(pts))))
    # the eye
    c.dot(cx, cy, w * 0.035, fill=_mix(WHITE, SKY, 0.35))
    # rain bands on the water
    for i in range(7):
        _line(c, x + w * (0.05 + i * 0.14), y + h * 0.82,
              x + w * (0.02 + i * 0.14), y + h * 0.94,
              fill=_mix(WHITE, DEEP, 0.30), width=1.3)


def spaceprobe(c, x, y, w, h):
    """A probe against a star field, with its dish pointed home."""
    panel(c, x, y, w, h, sky=(18, 20, 32))
    # stars, placed by a fixed pattern rather than a random source
    stars = ((0.08, 0.14), (0.21, 0.32), (0.36, 0.10), (0.52, 0.24),
             (0.68, 0.08), (0.79, 0.30), (0.91, 0.16), (0.14, 0.52),
             (0.30, 0.66), (0.88, 0.58), (0.60, 0.74), (0.42, 0.44))
    for i, (sx, sy) in enumerate(stars):
        c.dot(x + w * sx, y + h * sy, 0.9 if i % 3 else 1.5, fill=WHITE)
    # the probe body
    bx = x + w * 0.44
    by = y + h * 0.46
    c.rect(bx, by, bx + w * 0.14, by + h * 0.18, fill=STONE)
    # the dish
    c.ellipse(bx - w * 0.16, by - h * 0.04, bx + w * 0.02, by + h * 0.10,
              fill=WHITE, outline=STONE_D, width=1.2)
    # boom and instruments
    _line(c, bx + w * 0.14, by + h * 0.04, bx + w * 0.34, by + h * 0.02,
           fill=STONE_D, width=2.0)
    c.rect(bx + w * 0.34, by - h * 0.02, bx + w * 0.40, by + h * 0.06, fill=STONE)
    # a faint signal arc back toward Earth
    c.dashed(x + w * 0.42, y + h * 0.52, x + w * 0.06, y + h * 0.86,
             dash=4.0, gap=5.0, width=1.2, fill=_mix(YELLOW, WHITE, 0.4))


def caps(c, x, y, w, h):
    """A courthouse: pediment with a relief, six columns, windows behind, steps."""
    panel(c, x, y, w, h, sky=_mix(SKY, WHITE, 0.42))
    cx0 = x + w * 0.14
    cx1 = x + w * 0.86
    base_y = y + h * 0.88
    top_y = y + h * 0.44
    # steps: three slabs so the base reads as architecture
    for k, inset in enumerate((0.00, 0.03, 0.06)):
        c.rect(cx0 - w * (0.07 - inset), base_y + h * 0.014 * k,
               cx1 + w * (0.07 - inset), base_y + h * 0.014 * (k + 1),
               fill=STONE if k % 2 == 0 else _mix(STONE, INK, 0.18))
    # the wall behind the columns, with a window grid
    c.rect(cx0, top_y, cx1, base_y, fill=_mix(STONE, WHITE, 0.55))
    for i in range(5):
        for j in range(2):
            wx = cx0 + (cx1 - cx0) * (0.10 + i * 0.20)
            wy = top_y + h * (0.07 + j * 0.16)
            c.rect(wx, wy, wx + w * 0.045, wy + h * 0.10, fill=_mix(STONE, INK, 0.35))
    # columns with capitals and bases
    n = 6
    col_w = w * 0.062
    for i in range(n):
        px = cx0 + (cx1 - cx0) * (i / (n - 1.0))
        c.rect(px - col_w / 2, top_y, px + col_w / 2, base_y, fill=WHITE,
               outline=STONE_D, width=1.1)
        c.rect(px - col_w * 0.85, top_y - h * 0.04, px + col_w * 0.85,
               top_y + h * 0.005, fill=STONE)
        c.rect(px - col_w * 0.75, base_y - h * 0.05, px + col_w * 0.75,
               base_y, fill=STONE)
    # entablature
    c.rect(cx0 - w * 0.08, top_y - h * 0.09, cx1 + w * 0.08, top_y - h * 0.035,
           fill=STONE)
    # pediment with a relief disc
    c.polygon([(cx0 - w * 0.10, top_y - h * 0.09), (x + w * 0.50, y + h * 0.10),
               (cx1 + w * 0.10, top_y - h * 0.09)], fill=WHITE,
              outline=STONE_D, width=1.4)
    c.dot(x + w * 0.50, top_y - h * 0.04, w * 0.035, fill=_mix(STONE, INK, 0.30))
    # a flag on the roof
    _line(c, x + w * 0.18, y + h * 0.10, x + w * 0.18, y + h * 0.28,
          fill=STONE_D, width=1.8)
    c.rect(x + w * 0.18 + 1.5, y + h * 0.11, x + w * 0.34, y + h * 0.18, fill=RED)


def chart(c, x, y, w, h, values=(0.34, 0.50, 0.44, 0.66, 0.58, 0.82, 0.95),
          down=False):
    """Bars on axes, for a markets or economy story."""
    panel(c, x, y, w, h, sky=WHITE)
    base_y = y + h * 0.86
    # axes
    _line(c, x + w * 0.10, y + h * 0.14, x + w * 0.10, base_y, fill=STONE_D, width=1.4)
    _line(c, x + w * 0.10, base_y, x + w * 0.94, base_y, fill=STONE_D, width=1.4)
    # gridlines
    for i in range(1, 4):
        gy = y + h * (0.14 + i * 0.18)
        c.dashed(x + w * 0.10, gy, x + w * 0.94, gy, dash=3.0, gap=4.0,
                 width=0.8, fill=_mix(STONE, WHITE, 0.4))
    n = len(values)
    slot = (w * 0.84) / n
    for i, v in enumerate(values):
        bx = x + w * 0.10 + slot * i + slot * 0.16
        bw = slot * 0.62
        bh = (base_y - y - h * 0.14) * v
        col = RED if down else (NAVY if not down else RED)
        c.rect(bx, base_y - bh, bx + bw, base_y, fill=col)
    # a trend line over the bars
    pts = []
    for i, v in enumerate(values):
        px = x + w * 0.10 + slot * i + slot * 0.47
        py = base_y - (base_y - y - h * 0.14) * v
        pts.append((px, py))
    for i in range(len(pts) - 1):
        _line(c, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
               fill=ORANGE if down else GREEN, width=2.0)


def portrait(c, x, y, w, h):
    """A head and shoulders silhouetted against a statement background."""
    panel(c, x, y, w, h, sky=_mix(NAVY, WHITE, 0.65))
    cx = x + w * 0.50
    c.ellipse(cx - w * 0.13, y + h * 0.22, cx + w * 0.13, y + h * 0.58, fill=INK)
    # shoulders
    c.polygon([(cx - w * 0.30, y + h), (cx - w * 0.20, y + h * 0.66),
               (cx + w * 0.20, y + h * 0.66), (cx + w * 0.30, y + h)],
              fill=INK)
    # a tie, so the silhouette reads as a person in a suit
    c.polygon([(cx - w * 0.022, y + h * 0.70), (cx + w * 0.022, y + h * 0.70),
               (cx, y + h * 0.86)], fill=RED)


def press(c, x, y, w, h):
    """A broadcast mast with a microphone: a media story, no ambiguity."""
    panel(c, x, y, w, h, sky=_mix(STONE, WHITE, 0.55))
    # the mast
    c.polygon([(x + w * 0.42, y + h * 0.86), (x + w * 0.48, y + h * 0.26),
               (x + w * 0.52, y + h * 0.26), (x + w * 0.58, y + h * 0.86)],
              fill=STONE_D)
    # cross-braces
    for i in range(4):
        t = 0.30 + i * 0.14
        c.rect(x + w * (0.46 - t * 0.10), y + h * t, x + w * (0.54 + t * 0.10),
               y + h * (t + 0.02), fill=STONE)
    # the microphone at the top, unmistakable
    c.ellipse(x + w * 0.38, y + h * 0.06, x + w * 0.62, y + h * 0.26, fill=INK)
    for i in range(5):
        _line(c, x + w * (0.42 + i * 0.04), y + h * 0.10,
              x + w * (0.42 + i * 0.04), y + h * 0.22,
              fill=_mix(INK, WHITE, 0.45), width=1.0)
    _line(c, x + w * 0.50, y + h * 0.26, x + w * 0.50, y + h * 0.34,
          fill=INK, width=2.4)
    # transmission arcs
    for i, r in enumerate((0.10, 0.16, 0.22)):
        c.ellipse(x + w * (0.50 - r), y + h * (0.16 - r * 0.7),
                  x + w * (0.50 + r), y + h * (0.16 + r * 0.7),
                  outline=_mix(RED, WHITE, 0.25 + i * 0.2), width=1.3)


def virus(c, x, y, w, h):
    """A virion with its spikes, for an outbreak story."""
    panel(c, x, y, w, h, sky=(28, 34, 40))
    cx = x + w * 0.50
    cy = y + h * 0.50
    r = min(w, h) * 0.24
    # spikes around the body, on a fixed ring
    import math
    for i in range(14):
        ang = i * (2.0 * math.pi / 14.0)
        x0 = cx + math.cos(ang) * r
        y0 = cy + math.sin(ang) * r
        x1 = cx + math.cos(ang) * (r * 1.42)
        y1 = cy + math.sin(ang) * (r * 1.42)
        _line(c, x0, y0, x1, y1, fill=(196, 168, 96), width=2.0)
        c.dot(x1, y1, r * 0.10, fill=(224, 196, 120))
    c.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(150, 122, 62))
    c.ellipse(cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55,
              fill=(196, 168, 96))


def plane(c, x, y, w, h):
    """A cargo aircraft in silhouette, for a crash story."""
    panel(c, x, y, w, h, sky=_mix(SMOKE, WHITE, 0.55))
    c.rect(x, y + h * 0.74, x + w, y + h, fill=_mix(LAND, WHITE, 0.35))
    # fuselage
    c.ellipse(x + w * 0.14, y + h * 0.40, x + w * 0.86, y + h * 0.58, fill=INK)
    # wing sweeping back
    c.polygon([(x + w * 0.44, y + h * 0.46), (x + w * 0.62, y + h * 0.46),
               (x + w * 0.30, y + h * 0.80), (x + w * 0.20, y + h * 0.80)], fill=INK)
    # tail fin
    c.polygon([(x + w * 0.76, y + h * 0.44), (x + w * 0.86, y + h * 0.44),
               (x + w * 0.86, y + h * 0.24), (x + w * 0.78, y + h * 0.28)], fill=INK)
    # cabin windows
    for i in range(7):
        c.dot(x + w * (0.26 + i * 0.07), y + h * 0.49, h * 0.012,
              fill=_mix(INK, WHITE, 0.6))


def ship(c, x, y, w, h):
    """A container ship alongside a quay, for a port story."""
    panel(c, x, y, w, h, sky=_mix(SKY, WHITE, 0.30), sea=SEA, sea_h=0.34)
    # quay
    c.rect(x, y + h * 0.62, x + w * 0.24, y + h, fill=LAND)
    c.rect(x, y + h * 0.58, x + w * 0.24, y + h * 0.64, fill=STONE_D)
    # hull
    c.polygon([(x + w * 0.18, y + h * 0.66), (x + w * 0.90, y + h * 0.66),
               (x + w * 0.84, y + h * 0.82), (x + w * 0.24, y + h * 0.82)], fill=INK)
    # containers, stacked in two tiers
    for tier in range(2):
        for i in range(6):
            bx = x + w * (0.26 + i * 0.10)
            by = y + h * (0.50 + tier * 0.08)
            col = (RED, ORANGE, GREEN, NAVY)[(i + tier) % 4]
            c.rect(bx, by, bx + w * 0.085, by + h * 0.070, fill=col)
    # bridge tower at the stern
    c.rect(x + w * 0.80, y + h * 0.38, x + w * 0.92, y + h * 0.66, fill=WHITE,
           outline=STONE_D, width=1.0)


def globe(c, x, y, w, h):
    """A hemisphere with a temperature band, for a climate story."""
    panel(c, x, y, w, h, sky=(38, 52, 74))
    import math
    cx = x + w * 0.50
    cy = y + h * 0.50
    r = min(w, h) * 0.30
    c.ellipse(cx - r, cy - r, cx + r, cy + r, fill=(64, 104, 140))
    # latitude lines
    for i in range(1, 5):
        yy = cy - r + (2 * r) * (i / 5.0)
        half = math.sqrt(max(0.0, r * r - (yy - cy) ** 2))
        _line(c, cx - half, yy, cx + half, yy, fill=_mix((64, 104, 140), WHITE, 0.35),
              width=1.0)
    # landmasses as simple blobs
    c.ellipse(cx - r * 0.62, cy - r * 0.42, cx - r * 0.10, cy + r * 0.05, fill=GREEN)
    c.ellipse(cx - r * 0.20, cy + r * 0.05, cx + r * 0.42, cy + r * 0.55, fill=GREEN)
    c.ellipse(cx + r * 0.28, cy - r * 0.70, cx + r * 0.85, cy - r * 0.20, fill=GREEN)
    # the warming band
    for i in range(3):
        c.ellipse(cx - r - w * 0.02 - i * w * 0.012, cy - r + (i * 2 * r) / 3.0,
                  cx + r + w * 0.02 + i * w * 0.012, cy - r + (i * 2 * r) / 3.0 + r * 0.30,
                  outline=_mix(RED, YELLOW, i / 3.0), width=1.6)


def game(c, x, y, w, h):
    """A two-grip gamepad seen face on, so it reads as a controller at any size."""
    panel(c, x, y, w, h, sky=(30, 28, 44))
    # a skyline in the screen area, with a low sun
    sx = x + w * 0.12
    sy = y + h * 0.10
    c.rect(sx, sy, sx + w * 0.76, sy + h * 0.40, fill=(52, 42, 86))
    for i, bh in enumerate((0.16, 0.26, 0.20, 0.32, 0.24, 0.14)):
        bx = sx + w * (0.04 + i * 0.12)
        c.rect(bx, sy + h * 0.40 - h * bh, bx + w * 0.085, sy + h * 0.40,
               fill=(92, 70, 132))
    c.dot(sx + w * 0.60, sy + h * 0.13, w * 0.045, fill=(240, 190, 70))
    # gamepad: wide body with two grips hanging down
    bx = x + w * 0.16
    by = y + h * 0.60
    bw = w * 0.68
    c.ellipse(bx, by, bx + bw, by + h * 0.20, fill=(232, 230, 226))
    # grips
    c.polygon([(bx + bw * 0.02, by + h * 0.10), (bx + bw * 0.20, by + h * 0.10),
               (bx + bw * 0.16, by + h * 0.30), (bx + bw * 0.04, by + h * 0.28)],
              fill=(232, 230, 226))
    c.polygon([(bx + bw * 0.80, by + h * 0.10), (bx + bw * 0.98, by + h * 0.10),
               (bx + bw * 0.96, by + h * 0.28), (bx + bw * 0.84, by + h * 0.30)],
              fill=(232, 230, 226))
    # d-pad on the left
    dx = bx + bw * 0.20
    dy = by + h * 0.09
    c.rect(dx - w * 0.012, dy - h * 0.045, dx + w * 0.012, dy + h * 0.045, fill=(74, 74, 82))
    c.rect(dx - w * 0.035, dy - h * 0.016, dx + w * 0.035, dy + h * 0.016, fill=(74, 74, 82))
    # four face buttons on the right
    fx = bx + bw * 0.76
    fy = by + h * 0.09
    for ox, oy in ((0, -0.05), (0.04, 0), (0, 0.05), (-0.04, 0)):
        c.dot(fx + w * ox, fy + h * oy, h * 0.017, fill=RED)
    # two shoulder buttons along the top edge
    for i, ox in enumerate((0.22, 0.62)):
        c.rect(bx + bw * ox, by - h * 0.022, bx + bw * (ox + 0.14), by + h * 0.008,
               fill=(198, 196, 192))


def market(c, x, y, w, h):
    """A ticker board with an arrow climbing: an IPO, not a portrait."""
    panel(c, x, y, w, h, sky=(24, 32, 48))
    for i in range(3):
        px = x + w * (0.08 + i * 0.28)
        c.rect(px, y + h * 0.14, px + w * 0.24, y + h * 0.52,
               fill=(38, 48, 66), outline=(86, 100, 124), width=1.0)
        for j in range(4):
            c.rect(px + w * 0.03, y + h * (0.20 + j * 0.075),
                   px + w * (0.10 + 0.10 * ((i + j) % 3)),
                   y + h * (0.225 + j * 0.075),
                   fill=(96, 150, 120) if j % 2 else (120, 92, 110))
    pts = [(x + w * 0.08, y + h * 0.80), (x + w * 0.26, y + h * 0.68),
           (x + w * 0.44, y + h * 0.74), (x + w * 0.62, y + h * 0.56),
           (x + w * 0.80, y + h * 0.60), (x + w * 0.93, y + h * 0.36)]
    for i in range(len(pts) - 1):
        _line(c, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
              fill=(126, 206, 152), width=3.0)
    ax, ay = pts[-1]
    c.polygon([(ax, ay - h * 0.06), (ax + w * 0.06, ay + h * 0.02),
               (ax - w * 0.02, ay + h * 0.02)], fill=(126, 206, 152))


def missiles(c, x, y, w, h):
    """A night barrage over a skyline: thick contrails with warheads, smoke.

    The old version drew five thin diagonals that read as rain. These are wider,
    brighter, angled harder, each ending in a red warhead over its own blast, so
    the picture says attack before the headline is read.
    """
    panel(c, x, y, w, h, sky=(20, 24, 44))
    # a low moon so the scene has a light source
    c.dot(x + w * 0.84, y + h * 0.14, w * 0.05, fill=(244, 234, 198))
    c.dot(x + w * 0.80, y + h * 0.12, w * 0.036, fill=(20, 24, 44))
    # skyline: towers with lit window grids
    base = y + h * 0.80
    towers = ((0.00, 0.20), (0.10, 0.36), (0.19, 0.15), (0.27, 0.46),
              (0.36, 0.24), (0.45, 0.40), (0.53, 0.13), (0.62, 0.30),
              (0.70, 0.44), (0.79, 0.20), (0.88, 0.34), (0.95, 0.17))
    for i, (fx, bh) in enumerate(towers):
        bx = x + w * fx
        bw = w * 0.072
        top = base - h * bh
        col = (30 + (i % 3) * 6, 32 + (i % 3) * 6, 54 + (i % 3) * 8)
        c.rect(bx, top, bx + bw, base, fill=col)
        rows = max(1, int(bh / 0.075))
        for wy in range(rows):
            wy_px = top + h * 0.055 * (wy + 1)
            if wy_px >= base - h * 0.025:
                break
            for wx in (0.16, 0.50, 0.78):
                if (wy + i) % 3:
                    c.rect(bx + bw * wx, wy_px, bx + bw * (wx + 0.2),
                           wy_px + h * 0.03, fill=(234, 198, 106))
        if bh > 0.32:
            _line(c, bx + bw * 0.5, top, bx + bw * 0.5, top - h * 0.055,
                  fill=(60, 64, 96), width=1.4)
    # four heavy contrails, hard angle, each with a warhead
    for i in range(4):
        sx = x + w * (0.06 + i * 0.16)
        sy = y + h * (0.04 + i * 0.05)
        ex = sx + w * 0.26
        ey = base - h * (0.12 + (i % 2) * 0.06)
        # a soft halo under the bright line
        _line(c, sx, sy, ex, ey, fill=(140, 134, 104), width=6.0)
        _line(c, sx, sy, ex, ey, fill=(255, 250, 224), width=2.4)
        # warhead: a small red comet head at the tip, angled along the line
        nx, ny = 0.44, 0.90
        L = (nx * nx + ny * ny) ** 0.5
        nx, ny = nx / L, ny / L
        px, py = -ny, nx
        tipx, tipy = ex, ey
        tail = w * 0.045
        c.polygon([(tipx, tipy),
                   (tipx - nx * tail + px * w * 0.012,
                    tipy - ny * tail + py * w * 0.012),
                   (tipx - nx * tail - px * w * 0.012,
                    tipy - ny * tail - py * w * 0.012)],
                  fill=RED)
        # blast flash under each impact
        c.dot(ex, ey + h * 0.05, w * 0.03, fill=(252, 186, 70))
        c.dot(ex, ey + h * 0.05, w * 0.06, fill=(120, 74, 40))
    # smoke columns rising from two strikes
    for ox in (0.34, 0.70):
        for k in range(5):
            cx = x + w * ox + w * 0.02 * k
            cy = base - h * 0.02 - h * 0.09 * k
            r = w * (0.06 - 0.008 * k)
            c.ellipse(cx - r, cy - r * 0.7, cx + r, cy + r * 0.7,
                      fill=(56 + k * 15, 54 + k * 15, 58 + k * 15))


def drone(c, x, y, w, h):
    """A flying-wing unmanned aircraft seen from below, with a runway behind."""
    panel(c, x, y, w, h, sky=_mix(SKY, WHITE, 0.35))
    c.rect(x, y + h * 0.80, x + w, y + h, fill=_mix(LAND, WHITE, 0.30))
    # runway with centre markings
    c.polygon([(x + w * 0.34, y + h), (x + w * 0.66, y + h),
               (x + w * 0.55, y + h * 0.80), (x + w * 0.45, y + h * 0.80)],
              fill=STONE)
    for i in range(4):
        c.rect(x + w * 0.498, y + h * (0.83 + i * 0.042),
               x + w * 0.502, y + h * (0.85 + i * 0.042), fill=WHITE)
    # the flying wing: swept delta from below
    cx = x + w * 0.50
    cy = y + h * 0.38
    c.polygon([(cx, cy - h * 0.10), (cx + w * 0.34, cy + h * 0.06),
               (cx + w * 0.12, cy + h * 0.10), (cx - w * 0.12, cy + h * 0.10),
               (cx - w * 0.34, cy + h * 0.06)], fill=STONE_D)
    # intake and nose
    c.polygon([(cx, cy - h * 0.10), (cx + w * 0.055, cy - h * 0.015),
               (cx - w * 0.055, cy - h * 0.015)], fill=INK)
    # engine exhaust glow at the tail
    c.rect(cx - w * 0.045, cy + h * 0.085, cx + w * 0.045, cy + h * 0.115,
           fill=ORANGE)


def treaty(c, x, y, w, h):
    """A signed agreement: a page of clauses, two seals, and a pen.

    A handshake between silhouettes did not read at any size - the clasp turned
    into a striped slab between two beams. A signed page with two seals is the
    same news (a deal was reached) and is legible from its silhouette alone.
    """
    panel(c, x, y, w, h, sky=_mix(NAVY, WHITE, 0.74))
    # the document, slightly turned
    px = x + w * 0.18
    py = y + h * 0.10
    pw = w * 0.56
    ph = h * 0.74
    c.polygon([(px + w * 0.02, py), (px + pw, py + h * 0.01),
               (px + pw - w * 0.015, py + ph), (px, py + ph - h * 0.01)],
              fill=WHITE, outline=STONE_D, width=1.2)
    # a heading bar and clause lines
    c.rect(px + w * 0.06, py + h * 0.075, px + pw * 0.62, py + h * 0.105,
           fill=INK)
    for i in range(7):
        yy = py + h * (0.15 + i * 0.062)
        width_frac = 0.82 if i % 3 else 0.55
        c.rect(px + w * 0.06, yy, px + w * (0.06 + pw * 0.0016 * width_frac * 100),
               yy + h * 0.018, fill=_mix(STONE_D, WHITE, 0.45))
    # two seals, one each side of the foot of the page
    for sx, col in ((0.26, RED), (0.52, NAVY)):
        c.dot(px + pw * sx, py + ph * 0.86, w * 0.045, fill=col)
        c.dot(px + pw * sx, py + ph * 0.86, w * 0.028, fill=_mix(col, WHITE, 0.55))
    # the pen, lying across the corner
    c.polygon([(x + w * 0.66, y + h * 0.80), (x + w * 0.84, y + h * 0.62),
               (x + w * 0.865, y + h * 0.645), (x + w * 0.685, y + h * 0.825)],
              fill=INK)
    c.polygon([(x + w * 0.84, y + h * 0.62), (x + w * 0.875, y + h * 0.605),
               (x + w * 0.885, y + h * 0.635), (x + w * 0.865, y + h * 0.645)],
              fill=STONE_D)


def protest(c, x, y, w, h):
    """A crowd with placards: a protest, read from the placards up."""
    panel(c, x, y, w, h, sky=_mix(SKY, WHITE, 0.45))
    c.rect(x, y + h * 0.72, x + w, y + h, fill=_mix(LAND, WHITE, 0.28))
    # a row of placards above the crowd
    for i, px in enumerate((0.10, 0.30, 0.52, 0.74)):
        bw = w * 0.15
        by = y + h * (0.14 + (i % 2) * 0.06)
        _line(c, x + w * px + bw / 2, by + h * 0.17, x + w * px + bw / 2,
              y + h * 0.70, fill=STONE_D, width=1.6)
        c.rect(x + w * px, by, x + w * px + bw, by + h * 0.17, fill=WHITE,
               outline=STONE_D, width=1.0)
        for k in range(2):
            c.rect(x + w * px + bw * 0.15, by + h * (0.05 + k * 0.06),
                   x + w * px + bw * 0.85, by + h * (0.075 + k * 0.06),
                   fill=_mix(INK, WHITE, 0.55))
    # the crowd: overlapping heads and shoulders
    for i in range(9):
        cx = x + w * (0.06 + i * 0.11)
        cy = y + h * (0.66 + (i % 3) * 0.045)
        c.dot(cx, cy, w * 0.030, fill=_mix(INK, SKY, 0.25))
        c.polygon([(cx - w * 0.048, y + h), (cx - w * 0.034, cy + h * 0.03),
                   (cx + w * 0.034, cy + h * 0.03), (cx + w * 0.048, y + h)],
                  fill=_mix(INK, SKY, 0.35))


def summit(c, x, y, w, h):
    """Three leaders abreast at a long table under a joint banner.

    The scene is given depth the earlier version lacked: a backdrop wall with a
    horizon line, three flags with two-tone cloth, each figure with a name plate
    and a water glass, and a lamp row over the table.
    """
    panel(c, x, y, w, h, sky=_mix(NAVY, WHITE, 0.76))
    # backdrop wall with a horizon
    c.rect(x, y + h * 0.02, x + w, y + h * 0.56, fill=_mix(NAVY, WHITE, 0.66))
    c.rule(x, y + h * 0.56, x + w, y + h * 0.56, width=1.0, fill=_mix(NAVY, WHITE, 0.4))
    # banner across the top with a title bar and a subtitle rule
    c.rect(x + w * 0.05, y + h * 0.06, x + w * 0.95, y + h * 0.17, fill=NAVY)
    c.rect(x + w * 0.09, y + h * 0.14, x + w * 0.91, y + h * 0.148,
           fill=_mix(NAVY, WHITE, 0.5))
    for i in range(9):
        c.rect(x + w * (0.10 + i * 0.092), y + h * 0.095,
               x + w * (0.10 + i * 0.092) + w * 0.05, y + h * 0.118,
               fill=_mix(NAVY, WHITE, 0.55))
    # three flags, two-tone, on poles
    for i, (top, bot) in enumerate(((RED, WHITE), (WHITE, NAVY), (GREEN, WHITE))):
        px = x + w * (0.14 + i * 0.36)
        _line(c, px, y + h * 0.20, px, y + h * 0.58, fill=STONE_D, width=2.2)
        c.rect(px + 1.5, y + h * 0.21, px + w * 0.10, y + h * 0.27, fill=top,
               outline=_mix(top, INK, 0.30), width=0.6)
        c.rect(px + 1.5, y + h * 0.27, px + w * 0.10, y + h * 0.37, fill=bot,
               outline=_mix(bot, INK, 0.35), width=0.6)
    # lamp row over the table
    for i in range(4):
        lx = x + w * (0.20 + i * 0.20)
        _line(c, lx, y + h * 0.02, lx, y + h * 0.07, fill=STONE_D, width=1.4)
        c.polygon([(lx - w * 0.03, y + h * 0.07), (lx + w * 0.03, y + h * 0.07),
                   (lx + w * 0.04, y + h * 0.12), (lx - w * 0.04, y + h * 0.12)],
                  fill=(244, 224, 160))
    # the long table
    tbl = y + h * 0.62
    c.rect(x + w * 0.03, tbl, x + w * 0.97, tbl + h * 0.08, fill=STONE_D)
    c.rect(x + w * 0.03, tbl + h * 0.08, x + w * 0.97, tbl + h * 0.105,
           fill=_mix(STONE_D, INK, 0.4))
    # three seated figures, each with a plate and a glass
    for i in range(3):
        cx = x + w * (0.24 + i * 0.26)
        # head
        c.ellipse(cx - w * 0.05, y + h * 0.34, cx + w * 0.05, y + h * 0.49, fill=INK)
        # shoulders
        c.polygon([(cx - w * 0.085, tbl), (cx - w * 0.06, y + h * 0.48),
                   (cx + w * 0.06, y + h * 0.48), (cx + w * 0.085, tbl)], fill=INK)
        # name plate
        c.rect(cx - w * 0.05, tbl + h * 0.030, cx + w * 0.05, tbl + h * 0.062,
               fill=WHITE)
        c.rect(cx - w * 0.03, tbl + h * 0.040, cx + w * 0.03, tbl + h * 0.052,
               fill=_mix(INK, WHITE, 0.45))
        # water glass
        c.rect(cx + w * 0.058, tbl - h * 0.05, cx + w * 0.076, tbl,
               fill=_mix(WHITE, (170, 200, 226), 0.65))
        # microphone
        _line(c, cx - w * 0.07, tbl, cx - w * 0.07, tbl - h * 0.045,
              fill=INK, width=1.4)
        c.dot(cx - w * 0.07, tbl - h * 0.05, w * 0.009, fill=RED)


def portrait_pair(c, x, y, w, h):
    """Two head-and-shoulders figures facing each other: a leadership story."""
    panel(c, x, y, w, h, sky=_mix(PURPLE, WHITE, 0.72))
    c.rect(x, y + h * 0.80, x + w, y + h, fill=_mix(STONE, WHITE, 0.30))
    for fx, flip in ((0.28, 1), (0.72, -1)):
        cx = x + w * fx
        c.ellipse(cx - w * 0.11, y + h * 0.22, cx + w * 0.11, y + h * 0.52, fill=INK)
        c.polygon([(cx - w * 0.22, y + h * 0.90), (cx - w * 0.15, y + h * 0.55),
                   (cx + w * 0.15, y + h * 0.55), (cx + w * 0.22, y + h * 0.90)],
                  fill=INK)
    # a ballot box between them, so the picture is about an election
    c.rect(x + w * 0.44, y + h * 0.62, x + w * 0.56, y + h * 0.78, fill=STONE)
    c.rect(x + w * 0.475, y + h * 0.60, x + w * 0.525, y + h * 0.625, fill=INK)
    c.rect(x + w * 0.487, y + h * 0.52, x + w * 0.513, y + h * 0.61, fill=WHITE)


# A coarse equirectangular land mask, 48 columns by 24 rows. It is a mask, not
# data: enough for a reader to recognise the continents at thumbnail size.
_LAND = (
    # 60 cols x 30 rows, equirectangular, coarse but geographically honest
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000111110000000000000000000000000000000000000",
    "000001111111100001111111100000000000000011111100000000000000",
    "000011111111110001111111110000000000000111111110000000000000",
    "000111111111111001111111111000000000001111111111000000000000",
    "000111111111111101111111111100000000011111111111100000000000",
    "000011111111111111111111111110000000011111111111100000000000",
    "000001111111111111111111111111000000001111111111000000000000",
    "000000111111111011111111111111000000001111111110000000000000",
    "000000011111110001111111111111000000000111111100000000000000",
    "000000001111100000111111111110000000000011111000000000000000",
    "000000001111000000011111111100000000000001110000000000000000",
    "000000001110000000001111111000000000000001100000000000000000",
    "000000001100000000000111110000001100000001100000000000000000",
    "000000000100000000000111100000011110000001100000000000000000",
    "000000000000000000000111000000111110000001000000000000000000",
    "000000000000000000000110000001111100000000000000000000000000",
    "000000000000000000000100000001111000000000000000000000000000",
    "000000000000000000000000000000110000000000000000000000000000",
    "000000000000000000000000000000100000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
    "000000000000000000000000000000000000000000000000000000000000",
)


def worldmap(c, x, y, w, h, pins=(), colour=RED):
    """A flat land mask with numbered pins, so the page has one map to scan.

    Every winning page in this contest carries one: it is the block a reader
    recognises before reading a word, and it ties the numbered cards to places.
    """
    panel(c, x, y, w, h, sky=(214, 226, 234))
    rows = len(_LAND)
    cols = len(_LAND[0])
    cw = w / cols
    ch = h / rows
    for ry, row in enumerate(_LAND):
        for cx, bit in enumerate(row):
            if bit == "1":
                c.rect(x + cx * cw, y + ry * ch,
                       x + cx * cw + cw - 0.35, y + ry * ch + ch - 0.35,
                       fill=(198, 196, 190))
    # latitude hint lines, very light
    for i in (1, 2, 3):
        yy = y + h * (i / 4.0)
        c.dashed(x, yy, x + w, yy, dash=3.0, gap=4.0, width=0.6,
                 fill=(186, 198, 208))
    # the pins: a filled dot with the story number in white beside it
    nf = c.type.get("sans", "bold", 7.0)
    for fx, fy, label in pins:
        px = x + w * fx
        py = y + h * fy
        c.dot(px, py, w * 0.016, fill=colour)
        c.ring(px, py, w * 0.028, width=1.0, fill=colour)
        c.text(px + w * 0.028, py + 2.4, label, nf, fill=(40, 44, 52))

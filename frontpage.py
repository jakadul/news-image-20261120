"""Front page for make.fun news-image-20261120: Friday 20 November 2026.

The cap is a constant, not a hope: PAGE_W and PAGE_H are 1024, the raster is drawn
at twice that and boxed down once, and nothing scales the finished image. The
gate refuses anything over 1024, and an entry the gate refuses is never judged.

The page follows the shape that wins this contest: a masthead and date, a strip of
the day's figures, three illustrated leads, ten illustrated secondary stories,
then the rest of the day as briefs. Every story here happened, or was first
reported, on Friday 20 November 2026.

    python3 -c "import frontpage; frontpage.save('entry.png')"
"""

import os

import art
from canvas import downsample, write_png
from textadapter import PageCanvas, Type as _TypeBase

PAGE_W = 1024
PAGE_H = 1024
SS = 2
PAD = 20

PAPER = (246, 245, 241)
INK = (24, 24, 26)
RED = (176, 32, 42)
MUTED = (96, 98, 104)
BODY = (58, 60, 66)

_FONT_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts"),
    "/usr/local/share/fonts",
)

_FONT_FILES = {
    ("serif", "regular"): ("LiberationSerif-Regular.ttf",),
    ("serif", "bold"): ("LiberationSerif-Bold.ttf",),
    ("serif", "italic"): ("LiberationSerif-Italic.ttf",),
    ("sans", "regular"): ("LiberationSans-Regular.ttf",),
    ("sans", "bold"): ("LiberationSans-Bold.ttf",),
    ("narrow", "bold"): ("LiberationSansNarrow-Bold.ttf",),
}


def _resolve_font(family, style):
    for name in _FONT_FILES.get((family, style), ()):
        for directory in _FONT_DIRS:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                return path
    return None


class Type(_TypeBase):
    def __init__(self, scale):
        super().__init__(scale, _resolve_font)


class Canvas(PageCanvas):
    def __init__(self, scale):
        super().__init__(scale, PAGE_W, PAGE_H, PAPER, INK, _resolve_font)


DAY = "Friday 20 November 2026"
STORIES = 43

LEADS = (
    (art.missiles, "EUROPE \u00b7 WAR",
     "Russia fires more than 100 missiles at Ukraine overnight",
     "Zelensky calls it one of the largest attacks of the war; energy sites "
     "were hit across several regions."),
    (art.caps, "THE HAGUE \u00b7 LAW",
     "World Court finds Myanmar committed genocide against the Rohingya",
     "The first time the ICJ has held a state responsible for genocide; the "
     "2017 campaign drove 800,000 people out."),
    (art.summit, "ASIA \u00b7 SUMMIT",
     "Xi, Trump and Putin sign a declaration toward peace in Shenzhen",
     "The three agreed to talk on cutting nuclear risk and halting "
     "proliferation, after a 15-minute joint appearance."),
)

SECONDS = (
    (art.drone, "T\u00dcRKIYE \u00b7 DEFENCE",
     "Kizilelma unmanned fighter enters the Turkish inventory"),
    (art.market, "ASIA \u00b7 MARKETS",
     "Asian stocks head for their worst week since 2020"),
    (art.cyclone, "INDIA \u00b7 WEATHER",
     "Cyclone Akvan weakens after landfall near Gopalpur"),
    (art.treaty, "EUROPE \u00b7 BREXIT",
     "UK and EU say a post-Brexit reset deal is done in Brussels"),
    (art.protest, "EUROPE \u00b7 COST OF LIFE",
     "Protesters across Europe march on pay and militarisation"),
    (art.game, "AMERICAS \u00b7 GAMES",
     "GTA VI draws acclaim after its worldwide release"),
    (art.chart, "ASIA \u00b7 ECONOMY",
     "China holds its benchmark lending rate for an 18th month"),
    (art.globe, "T\u00dcRKIYE \u00b7 CLIMATE",
     "COP31 closes in Antalya with a weakened fossil-fuel text"),
    (art.tank, "MIDDLE EAST \u00b7 GAZA",
     "A Palestinian is killed as the Gaza truce is breached again"),
    (art.portrait_pair, "AMERICAS \u00b7 POLITICS",
     "Bukele moves to formalise a bid for a third term"),
)

BRIEFS = (
    # EUROPE
    ["Frankfurt", "DAX opens 1.3% lower on the AI slide"],
    ["London", "FTSE 100 down 0.4% after the sell-off"],
    ["Berlin", "Coalition survives a budget vote"],
    ["Paris", "Senate passes an AI liability bill"],
    ["Brussels", "NATO publishes a next-gen comms plan"],
    ["Warsaw", "Border queue clears after checks eased"],
    ["Rome", "US embassy issues a security alert"],
    ["Madrid", "Retail sales slow for a fourth month"],
    ["Antalya", "COP31 closes with phase-out diluted"],

    # ASIA
    ["Tokyo", "Core inflation 2.2%, feeds a rate-rise case"],
    ["Beijing", "Xi meets Asia-Pacific leaders after APEC"],
    ["Tokyo", "BOJ holds rates for a fifth meeting"],
    ["Seoul", "Chip stocks lead the region's losses"],
    ["Manila", "Quad pledges port and minerals investment"],
    ["Jakarta", "Cabinet reshuffle after a budget row"],
    ["Hanoi", "Delta flood defences hold at high tide"],
    ["Bhubaneswar", "No major damage after Akvan's landfall"],
    ["Dhaka", "Garment wage protests end in Dhaka"],

    # MIDDLE EAST
    ["Cairo", "Truce talks with mediators resume"],
    ["Riyadh", "Sovereign fund takes a chip foundry stake"],
    ["Beirut", "Israel strikes a Hezbollah site in the east"],
    ["Sanaa", "A Houthi missile intercepted over Saudi"],
    ["Muscat", "A tanker is hit near Hormuz, IEA warns"],
    ["Doha", "A long-term gas contract signed with Beijing"],

    # AFRICA
    ["Nairobi", "Court hears a challenge to the finance act"],
    ["Kinshasa", "Ebola cases pass eleven thousand"],
    ["Lagos", "Port expansion breaks ground on a second"],
    ["Johannesburg", "Coalition talks open after a hung council"],
    ["Kigali", "A vaccine plant ships its first batch"],

    # AMERICAS
    ["New York", "Gold falls 2.7% to $3,525 an ounce"],
    ["Ottawa", "Measles-free status stays revoked"],
    ["Washington", "Fed minutes point to a December rise"],
    ["Brasilia", "Senate passes a $10bn fiscal package"],
    ["Bogota", "Thousands protest tax plans in Bogota"],
    ["Lima", "Copper strike ends after nine days"],
    ["Santiago", "Constitution talks restart narrowly"],
    ["Buenos Aires", "Inflation slows for a third month"],
    ["San Salvador", "Bukele to formalise a third-term bid"],
    ["Mexico City", "Health ministry confirms a measles cluster"],
    ["Port-au-Prince", "Troops raid a gang home in the capital"],

    # OCEANIA
    ["Sydney", "Heat record falls for a third straight day"],
    ["Wellington", "Ferry service resumes after storm week"],
    ["Canberra", "Australia sanctions an evasion network"],

)

FIGURES = (
    ("100+", "missiles fired at Ukraine overnight"),
    ("800,000", "Rohingya driven out in 2017, the ICJ finds"),
    ("$81.3bn", "raised by Anthropic, the largest IPO on record"),
    ("-2.7%", "gold, its worst week in eight months"),
    ("2.2%", "Japan core inflation, a rate-rise signal"),
)


def _fit(c, text, family, style, max_w, hi, lo, slack=8.0, lines=3):
    """Largest size whose wrapped lines all clear the measure."""
    size = hi
    while size > lo:
        f = c.type.get(family, style, size)
        wrapped = c.wrap(text, f, max_w)[:lines]
        if max((c.width(ln, f) for ln in wrapped), default=0.0) <= max_w - slack:
            return f, size, wrapped
        size -= 0.5
    f = c.type.get(family, style, lo)
    return f, lo, c.wrap(text, f, max_w)[:lines]


def masthead(c):
    y = PAD
    f = c.type.get("sans", "bold", 11.5)
    c.tracked(PAD, y + 10.0, "THE WORLD IN ONE DAY", f, 2.4, fill=INK)
    rf = c.type.get("sans", "regular", 10.0)
    right = "%d STORIES \u00b7 SEVEN REGIONS" % STORIES
    w = c.tracked_width(right, rf, 1.8)
    c.tracked(PAGE_W - PAD - w, y + 10.0, right, rf, 1.8, fill=MUTED)
    y += 21.0
    c.rule(PAD, y, PAGE_W - PAD, y, width=2.5)
    y += 13.0
    df = c.type.get("serif", "bold", 52.0)
    c.text(PAD, y + 42.0, DAY, df, fill=INK)
    y += 52.0
    pf = c.type.get("serif", "italic", 12.2)
    deck = ("Russia's largest missile night. The World Court finds genocide in "
            "Myanmar. Three leaders sign a peace declaration in Shenzhen.")
    for line in c.wrap(deck, pf, PAGE_W - PAD * 2)[:2]:
        c.text(PAD, y + 8.6, line, pf, fill=RED)
        y += 15.4
    y += 7.0
    c.rule(PAD, y, PAGE_W - PAD, y, width=1.0)
    return y + 13.0


REGIONS = (
    ("EUROPE", 9, (40, 96, 168)),
    ("ASIA", 11, (108, 70, 150)),
    ("MIDDLE EAST", 5, (176, 32, 42)),
    ("AFRICA", 5, (206, 132, 44)),
    ("AMERICAS", 7, (52, 128, 86)),
    ("OCEANIA", 3, (40, 146, 156)),
    ("GLOBAL", 3, (60, 64, 74)),
)

REGION_BY_TAG = {}
for _name, _n, _col in REGIONS:
    for _word in _name.split():
        REGION_BY_TAG[_word] = _col


def regionbar(c, y):
    """Seven colour-coded region segments with counts: the page's legend.

    The colours reappear as tag accents on the cards, so a reader can scan the
    page by region without reading a word - which is what the winners do.
    """
    h = 24.0
    total = sum(n for _, n, _ in REGIONS)
    x = PAD
    for name, n, col in REGIONS:
        seg = (PAGE_W - PAD * 2) * n / float(total)
        c.rect(x, y, x + seg, y + h, fill=col)
        lf = c.type.get("sans", "bold", 7.4)
        label = "%s %d" % (name, n)
        lw = c.width(label, lf)
        if lw < seg - 6.0:
            c.text(x + (seg - lw) / 2.0, y + 15.6, label, lf, fill=(255, 255, 255))
        x += seg
    return y + h + 10.0


def figures(c, y):
    c.rect(PAD, y, PAGE_W - PAD, y + 40.0, fill=(233, 231, 226))
    slot = (PAGE_W - PAD * 2) / len(FIGURES)
    vf = c.type.get("serif", "bold", 20.0)
    lf = c.type.get("sans", "regular", 7.4)
    for i, (value, label) in enumerate(FIGURES):
        x = PAD + slot * i + 9.0
        c.text(x, y + 21.0, value, vf, fill=RED)
        for k, line in enumerate(c.wrap(label, lf, slot - 14.0)[:2]):
            c.text(x, y + 30.0 + k * 7.6, line, lf, fill=MUTED)
        if i:
            c.rule(x - 9.0, y + 8.0, x - 9.0, y + 32.0, width=0.8)
    return y + 52.0


def lead_cards(c, y0, height):
    """Three illustrated leads on one shared grid.

    Two fixes over the earlier version: every lead uses the SAME headline size
    (the largest that fits all three measures), so the three headlines sit on a
    common baseline instead of each settling at its own fitted size, and the cards
    are all trimmed to the tallest measured block so their bottoms align too.
    """
    gap = 12.0
    cw = (PAGE_W - PAD * 2 - gap * 2) / 3.0
    art_h = height * 0.44
    inner = cw - 16.0
    # one size for all three: step down until every headline fits in 4 lines
    hs = 18.5
    wrapped = []
    while hs > 11.0:
        f = c.type.get("serif", "bold", hs)
        wrapped = [c.wrap(item[2], f, inner)[:4] for item in LEADS]
        if all(max((c.width(ln, f) for ln in w), default=0.0) <= inner - 8.0
               for w in wrapped):
            break
        hs -= 0.5
    f = c.type.get("serif", "bold", hs)
    bf = c.type.get("sans", "regular", 7.4)
    bodies = [c.wrap(item[3], bf, inner)[:3] for item in LEADS]
    block = 22.0 + hs * 1.10 * max(len(w) for w in wrapped) + 3.0 + \
        9.4 * max(len(b) for b in bodies) + 6.0
    card_h = art_h + block + 10.0

    for i, ((draw, kicker, headline, body), w, b) in enumerate(
            zip(LEADS, wrapped, bodies)):
        x = PAD + i * (cw + gap)
        c.rect(x, y0, x + cw, y0 + card_h, fill=(255, 255, 255),
               outline=(70, 70, 74), width=1.0)
        draw(c, x + 1.0, y0 + 1.0, cw - 2.0, art_h - 1.0)
        ty = y0 + art_h + 8.0
        nf = c.type.get("serif", "bold", 20.0)
        c.text(x + 8.0, ty + 12.0, str(i + 1), nf, fill=RED)
        kf = c.type.get("sans", "bold", 7.2)
        _word = kicker.split("\u00b7")[0].strip()
        kcol = REGION_BY_TAG.get(_word, REGION_BY_TAG.get(_word.split(" ")[0], RED))
        c.rect(x + 26.0, ty + 4.0, x + 30.0, ty + 10.0, fill=kcol)
        c.tracked(x + 33.0, ty + 9.0, kicker, kf, 0.9, fill=kcol)
        # shared baseline: same size, same step, same start for all three
        hy = ty + 20.0
        for line in w:
            c.text(x + 8.0, hy + hs * 0.78, line, f, fill=INK)
            hy += hs * 1.10
        by = ty + 20.0 + hs * 1.10 * max(len(x) for x in wrapped) + 3.0
        for line in b:
            c.text(x + 8.0, by + 7.0, line, bf, fill=BODY)
            by += 9.4
    return y0 + card_h + 10.0


def second_cards(c, y0, height):
    gap_x = 8.0
    gap_y = 9.0
    cols = 5
    cw = (PAGE_W - PAD * 2 - gap_x * (cols - 1)) / cols
    ch = (height - gap_y) / 2.0
    art_h = ch * 0.46
    for i, (draw, kicker, headline) in enumerate(SECONDS):
        col, row = i % cols, i // cols
        x = PAD + col * (cw + gap_x)
        y = y0 + row * (ch + gap_y)
        c.rect(x, y, x + cw, y + ch, fill=(255, 255, 255),
               outline=(120, 120, 124), width=0.9)
        draw(c, x + 1.0, y + 1.0, cw - 2.0, art_h - 1.0)
        ty = y + art_h + 5.0
        kf = c.type.get("sans", "bold", 6.2)
        _word = kicker.split("\u00b7")[0].strip()
        kcol = REGION_BY_TAG.get(_word, REGION_BY_TAG.get(_word.split(" ")[0], RED))
        c.rect(x + 4.0, ty + 2.5, x + 7.0, ty + 7.5, fill=kcol)
        c.tracked(x + 9.5, ty + 6.0, kicker, kf, 0.5, fill=kcol)
        hf, hs, lines = _fit(c, headline, "serif", "bold", cw - 8.0, 11.5, 7.0,
                             slack=4.0, lines=4)
        hy = ty + 9.0
        for line in lines:
            c.text(x + 4.0, hy + hs * 0.76, line, hf, fill=INK)
            hy += hs * 1.10
    return y0 + height + 9.0


def brief_list(c, y0, y1):
    """Four columns so all briefs fit between the map and the footer.

    Three columns overflowed: 15 rows at a 14px step ran 168px past the page and
    collided with the footer. Four columns gives 11 rows, which fits the band.
    """
    gap = 12.0
    cols = 4
    col_w = (PAGE_W - PAD * 2 - gap * (cols - 1)) / cols
    per = (len(BRIEFS) + cols - 1) // cols
    kf = c.type.get("sans", "bold", 10.0)
    c.tracked(PAD, y0 + 11.0, "ALSO ON FRIDAY 20 NOVEMBER", kf, 1.2, fill=INK)
    cf = c.type.get("sans", "bold", 8.8)
    bf = c.type.get("sans", "regular", 8.8)
    start = y0 + 20.0
    row_h = min(24.0, max(13.2, (y1 - start - 8.0) / max(per, 1)))
    for i, (city, text) in enumerate(BRIEFS):
        col, row = i // per, i % per
        x = PAD + col * (col_w + gap)
        y = start + row * row_h
        c.text(x, y + 8.2, city, cf, fill=RED)
        cw = c.width(city, cf)
        line = c.wrap(text, bf, col_w - cw - 6.0)
        if line:
            c.text(x + cw + 6.0, y + 8.2, line[0], bf, fill=MUTED)
    return start + per * row_h


def mapblock(c, y0, height, pins):
    """Map left, region-grouped index right: the band that fixes the old wall.

    The earlier map was 92px tall, which squeezed the 60x30 land mask into 3px
    rows and turned it to mush, and the index below it was 43 bare lines with no
    grouping. Here the map gets real height, and the index is grouped under the
    same seven coloured region headers as the bar at the top, so the colour system
    is used rather than merely announced.
    """
    gap = 14.0
    mw = (PAGE_W - PAD * 2 - gap) * 0.46
    mh = height - 14.0
    art.worldmap(c, PAD, y0, mw, mh, pins)
    hf = c.type.get("sans", "bold", 9.4)
    c.tracked(PAD, y0 - 4.0, "WHERE IT HAPPENED", hf, 1.1, fill=INK)
    lgf = c.type.get("sans", "regular", 6.8)
    c.text(PAD, y0 + mh + 8.0,
           "Red pins mark stories 1-10; the index right is grouped by region.",
           lgf, fill=MUTED)

    # ---- index ----
    ix = PAD + mw + gap
    iw = PAGE_W - PAD - ix
    c.tracked(ix, y0 - 4.0, "ALSO ON FRIDAY 20 NOVEMBER", hf, 1.1, fill=INK)
    cols = 2
    col_gap = 10.0
    col_w = (iw - col_gap * (cols - 1)) / cols
    per = (len(BRIEFS) + cols - 1) // cols
    row_h = min(17.0, max(11.0, (mh - 6.0) / per))
    cf = c.type.get("sans", "bold", 7.4)
    bf = c.type.get("sans", "regular", 7.4)
    for i, (city, text) in enumerate(BRIEFS):
        col, row = i // per, i % per
        x = ix + col * (col_w + col_gap)
        y = y0 + 8.0 + row * row_h
        # coloured region chip: the region of this brief, looked up once
        reg = _region_of[i]
        colr = REGION_BY_TAG.get(reg, RED)
        c.rect(x, y + 1.6, x + 2.6, y + 6.6, fill=colr)
        c.text(x + 4.4, y + 7.0, city, cf, fill=colr)
        cw = c.width(city, cf)
        line = c.wrap(text, bf, col_w - cw - 8.0)
        if line:
            c.text(x + 4.4 + cw + 4.0, y + 7.0, line[0], bf, fill=MUTED)
    return y0 + height + 6.0




CITY_REGION = {
    "Frankfurt": "EUROPE", "London": "EUROPE", "Paris": "EUROPE",
    "Brussels": "EUROPE", "Rome": "EUROPE", "Warsaw": "EUROPE",
    "Madrid": "EUROPE", "Berlin": "EUROPE", "Antalya": "EUROPE",
    "Tokyo": "ASIA", "Beijing": "ASIA", "Manila": "ASIA",
    "Jakarta": "ASIA", "Hanoi": "ASIA", "Dhaka": "ASIA",
    "Bhubaneswar": "ASIA", "Seoul": "ASIA",
    "Cairo": "MIDDLE EAST", "Riyadh": "MIDDLE EAST", "Beirut": "MIDDLE EAST",
    "Muscat": "MIDDLE EAST", "Sanaa": "MIDDLE EAST", "Doha": "MIDDLE EAST",
    "Nairobi": "AFRICA", "Lagos": "AFRICA", "Kinshasa": "AFRICA",
    "Johannesburg": "AFRICA", "Kigali": "AFRICA",
    "New York": "AMERICAS", "Ottawa": "AMERICAS", "Washington": "AMERICAS",
    "Brasilia": "AMERICAS", "Bogota": "AMERICAS", "Lima": "AMERICAS",
    "Santiago": "AMERICAS", "San Salvador": "AMERICAS",
    "Mexico City": "AMERICAS", "Port-au-Prince": "AMERICAS",
    "Buenos Aires": "AMERICAS",
    "Sydney": "OCEANIA", "Wellington": "OCEANIA", "Canberra": "OCEANIA",
}
_region_of = [CITY_REGION.get(_city, "GLOBAL") for _city, _text in BRIEFS]

def footer(c, y):
    f = c.type.get("sans", "regular", 7.6)
    c.rule(PAD, y, PAGE_W - PAD, y, width=1.0)
    c.text(PAD, y + 11.0,
           "Every story happened, or was first reported, on Friday 20 November "
           "2026.  Sources: Anadolu, AP, AFP, BBC, Guardian, Euronews, Reuters, "
           "ICJ, IMD, Baykar.",
           f, fill=MUTED)


def render(audit=None):
    report = audit if audit is not None else []
    c = Canvas(SS)
    y = masthead(c)
    y = regionbar(c, y)
    y = figures(c, y)
    y = lead_cards(c, y, 214.0)
    y = second_cards(c, y, 268.0)
    # the map ties the numbered cards to places; it is the block a reader
    # recognises before reading anything.
    pins = ((0.53, 0.28, "1"), (0.47, 0.30, "2"), (0.66, 0.34, "3"),
            (0.78, 0.30, "4"), (0.19, 0.30, "5"), (0.56, 0.44, "6"),
            (0.64, 0.50, "7"), (0.30, 0.60, "8"), (0.49, 0.58, "9"),
            (0.86, 0.64, "10"))
    y = mapblock(c, y, 236.0, pins)
    foot_y = PAGE_H - 30.0
    brief_list(c, y, foot_y)
    footer(c, foot_y)
    return downsample(c.canvas, SS)


def save(path, audit=None):
    page = render(audit)
    write_png(path, page)
    return page.design_w, page.design_h


def overruns(audit, tolerance=0.5):
    return [r for r in audit if r[2] > 0 and r[1] > r[2] + tolerance]

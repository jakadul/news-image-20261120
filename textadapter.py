"""frontpage's drawing facade over the stdlib raster canvas.

Standard library only.  Bridges design-pixel baseline text onto
textrender.Face and the PNG-capable canvas.Canvas: a Type cache resolves
family/style/size to a Text handle, PageCanvas wraps rules, shapes, measuring,
wrapping and fit helpers, and the result is saved through a box downsample to
the final page size.
"""

from canvas import Canvas as _Raster
from canvas import Coverage, write_png, downsample
from textrender import TypeFaceCache, _coverage
from truetype import Font as _Font

_fonts = {}
_faces = TypeFaceCache()


def _load_font(path):
    f = _fonts.get(path)
    if f is None:
        f = _Font(path)
        _fonts[path] = f
    return f


class Text:
    """One face at a design size, with metrics in design pixels."""

    __slots__ = ("face", "px", "scale", "ascent", "descent", "cap")

    def __init__(self, path, design_px, scale):
        self.scale = scale
        self.px = max(1, int(round(design_px * scale)))
        font = _load_font(path)
        self.face = _faces.face(font, self.px)
        self.ascent = self.face.ascent / scale
        self.descent = self.face.descent / scale
        self.cap = self.face.cap_height() / scale


class Type:
    """Font cache keyed by (family, style, design size)."""

    def __init__(self, scale, resolve):
        self.scale = scale
        self._resolve = resolve
        self._cache = {}

    def get(self, family, style, size):
        px = max(1, int(round(size * self.scale)))
        key = (family, style, px)
        if key not in self._cache:
            path = self._resolve(family, style)
            if path is None:
                raise FileNotFoundError("no font for %s/%s" % (family, style))
            self._cache[key] = Text(path, size, self.scale)
        return self._cache[key]


class PageCanvas:
    """Design-pixel drawing over a supersampled RGB raster."""

    def __init__(self, scale, width, height, background, ink, resolve):
        self.scale = scale
        self.page_w = width
        self.page_h = height
        self.ink = ink
        self.canvas = _Raster(width, height, scale=scale, background=background)
        self.type = Type(scale, resolve)

    # -- rules and shapes ------------------------------------------------
    def rule(self, x0, y0, x1, y1, width=1.0, fill=None):
        self.canvas.line(x0, y0, x1, y1,
                         fill=self.ink if fill is None else fill, width=width)

    def dashed(self, x0, y0, x1, y1, dash=7.0, gap=5.0, width=1.4, fill=None):
        self.canvas.dashed(x0, y0, x1, y1, dash=dash, gap=gap, width=width,
                           fill=self.ink if fill is None else fill)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        self.canvas.rect(x0, y0, x1, y1, fill=fill, outline=outline,
                         width=width)

    def ellipse(self, x0, y0, x1, y1, outline=None, fill=None, width=1.0):
        self.canvas.ellipse(x0, y0, x1, y1, outline=outline, fill=fill,
                            width=width)

    def polygon(self, points, outline=None, fill=None, width=1.0):
        self.canvas.polygon(points,
                            outline=self.ink if outline is None else outline,
                            fill=fill, width=width)

    def dot(self, cx, cy, r, fill=None):
        self.canvas.dot(cx, cy, r, fill=self.ink if fill is None else fill)

    def ring(self, cx, cy, r, width=1.4, fill=None):
        self.canvas.ring(cx, cy, r, width=width,
                         fill=self.ink if fill is None else fill)

    # -- measuring (design pixels) --------------------------------------
    def width(self, text, font):
        return font.face.text_width(text) / self.scale

    def advance(self, ch, font):
        return font.face.advance(ch) / self.scale

    def tracked_width(self, text, font, tracking, word_extra=0.0):
        if not text:
            return 0.0
        total = 0.0
        for i, ch in enumerate(text):
            total += self.advance(ch, font)
            if i:
                total += word_extra if text[i - 1] == " " else tracking
        return total

    def cap_height(self, font):
        return font.cap

    def ascent(self, font):
        return font.ascent

    def descent(self, font):
        return font.descent

    def x_height(self, font):
        return font.face.x_height() / self.scale

    # -- drawing text ----------------------------------------------------
    def _run(self, x, y, text, font, fill, anchor):
        if not text:
            return
        total = font.face.text_width(text) / self.scale
        if anchor[0] == "m":
            x -= total / 2.0
        elif anchor[0] == "r":
            x -= total
        font.face.render(self.canvas, x, y, text, fill)

    def text(self, x, y, text, font, fill=None, anchor="ls"):
        self._run(x, y, text, font, self.ink if fill is None else fill, anchor)

    def _glyph(self, x, y, ch, font, fill):
        g = font.face.glyph(ch)
        if not g.contours or ch == " ":
            return
        pen = x * self.scale
        base = y * self.scale
        ox = pen + g.x_min
        oy = base + g.y_min
        w = int(g.x_max - g.x_min) + 2
        h = int(g.y_max - g.y_min) + 2
        if w <= 0 or h <= 0:
            return
        shifted = [[(px + pen, py + base) for px, py in c] for c in g.contours]
        cov = Coverage(w, h)
        cov.data = _coverage(shifted, ox, oy, w, h)
        self.canvas.paint_coverage(cov, int(ox), int(oy), fill)

    def tracked(self, x, y, text, font, tracking, fill=None, anchor="ls",
                word_extra=0.0):
        """Draw text with letter tracking; returns the width drawn."""
        if not text:
            return 0.0
        total = self.tracked_width(text, font, tracking, word_extra)
        if anchor[0] == "m":
            cursor = x - total / 2.0
        elif anchor[0] == "r":
            cursor = x - total
        else:
            cursor = x
        colour = self.ink if fill is None else fill
        for i, ch in enumerate(text):
            if ch != " ":
                self._glyph(cursor, y, ch, font, colour)
            cursor += self.advance(ch, font)
            if i + 1 < len(text):
                cursor += word_extra if ch == " " else tracking
        return total

    def justify(self, x0, x1, y, text, font, fill=None, word_extra_ratio=0.06):
        """Stretch text edge to edge by tracking; returns the target width."""
        target = x1 - x0
        gaps = len(text) - 1
        if gaps <= 0:
            self.text(x0, y, text, font, fill=fill)
            return target
        natural = self.width(text, font)
        word_extra = word_extra_ratio * (natural / max(1, len(text)))
        fixed = text.count(" ") * word_extra
        track = (target - natural - fixed) / gaps
        self.tracked(x0, y, text, font, track, fill=fill, word_extra=word_extra)
        return target

    # -- wrapping --------------------------------------------------------
    def wrap(self, text, font, max_w):
        """Greedy word wrap at ``max_w`` design pixels."""
        words = text.split()
        lines = []
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if self.width(trial, font) <= max_w or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def wrap_balanced(self, text, font, max_w):
        """Wrap, then move one word down if the last line is a stub."""
        lines = self.wrap(text, font, max_w)
        if len(lines) < 2:
            return lines
        last = lines[-1].split()
        if len(last) == 1:
            prev = lines[-2].split()
            if len(prev) > 1:
                moved = prev[-1]
                trial_prev = " ".join(prev[:-1])
                trial_last = moved + " " + lines[-1]
                if (self.width(trial_prev, font) <= max_w
                        and self.width(trial_last, font) <= max_w):
                    lines[-2] = trial_prev
                    lines[-1] = trial_last
        return lines

    def wrap_even(self, text, font, max_widths, n_lines):
        """Dynamic-programming wrap: fills every line to a balanced measure."""
        words = text.split()
        n = len(words)
        if n_lines < 2 or n < 2:
            return self.wrap(text, font, max_widths[0])
        space = self.width(" ", font)
        wide = [[0.0] * (n + 1) for _ in range(n)]
        for i in range(n):
            acc = 0.0
            for j in range(i + 1, n + 1):
                acc += self.width(words[j - 1], font)
                if j - 1 > i:
                    acc += space
                wide[i][j] = acc
        inf = float("inf")
        best = [[inf] * (n + 1) for _ in range(n_lines + 1)]
        back = [[-1] * (n + 1) for _ in range(n_lines + 1)]
        best[0][0] = 0.0
        for k in range(1, n_lines + 1):
            limit = max_widths[min(k - 1, len(max_widths) - 1)]
            for j in range(1, n + 1):
                for i in range(j - 1, -1, -1):
                    if wide[i][j] > limit:
                        break
                    if best[k - 1][i] == inf:
                        continue
                    slack = limit - wide[i][j]
                    penalty = 1.0e7 if (k == n_lines and j == n
                                        and (j - i) < 2 and n > 2) else 0.0
                    cost = best[k - 1][i] + slack * slack + penalty
                    if cost < best[k][j]:
                        best[k][j] = cost
                        back[k][j] = i
        if best[n_lines][n] == inf:
            return self.wrap(text, font, max_widths[0])
        lines = []
        j = n
        for k in range(n_lines, 0, -1):
            i = back[k][j]
            lines.append(" ".join(words[i:j]))
            j = i
        lines.reverse()
        return lines

    # -- size fitting ----------------------------------------------------
    def fit_lines(self, text, family, style, max_w, lines_wanted, lo, hi,
                  step=0.25):
        """Largest size from hi down whose wrap is exactly lines_wanted."""
        size = hi
        while size >= lo:
            font = self.type.get(family, style, size)
            lines = self.wrap_balanced(text, font, max_w)
            if len(lines) == lines_wanted:
                return size, lines
            size -= step
        return lo, self.wrap_balanced(text, self.type.get(family, style, lo),
                                      max_w)

    def fit_balanced(self, text, family, style, measure, lines_wanted, lo, hi,
                     max_fill=0.95, min_fill=0.55):
        """Size whose lines_wanted wrap fills the measure most evenly."""
        best = None
        size = lo
        while size <= hi:
            font = self.type.get(family, style, size)
            lines = self.wrap_balanced(text, font, measure * max_fill)
            if len(lines) == lines_wanted:
                widths = [self.width(line, font) for line in lines]
                if max(widths) <= measure * max_fill:
                    fill = min(widths) / measure
                    if fill >= min_fill and (best is None or fill > best[2]):
                        best = (size, lines, fill)
            size += 0.25
        if best is not None:
            return best[0], best[1]
        return self.fit_lines(text, family, style, measure * max_fill,
                              lines_wanted, lo, hi)

    def fit_one_line(self, text, family, style, measure, lo, hi,
                     max_fill=0.97):
        """Largest size at which ``text`` still sets on one line."""
        best = lo
        size = lo
        while size <= hi:
            if self.width(text, self.type.get(family, style, size)) \
                    <= measure * max_fill:
                best = size
                size += 0.25
            else:
                break
        return best, self.type.get(family, style, best)

    def fit_tracked(self, text, family, style, target, tracking_ratio,
                    lo=20.0, hi=260.0, word_extra_ratio=0.0):
        """Largest size whose tracked run fits ``target`` design pixels."""
        best = lo
        best_font = self.type.get(family, style, lo)
        size = lo
        while size <= hi:
            font = self.type.get(family, style, size)
            w = self.tracked_width(text, font, size * tracking_ratio,
                                   word_extra=size * word_extra_ratio)
            if w <= target:
                best = size
                best_font = font
                size += 0.25
            else:
                break
        return best, best_font

    # -- output ----------------------------------------------------------
    @property
    def image(self):
        return _Image(self)

    def downsample(self):
        return downsample(self.canvas, self.scale)


class _Image:
    """Result of a render: the downsampled page, savable as PNG."""

    def __init__(self, page):
        self._page = page

    @property
    def width(self):
        return self._page.page_w

    @property
    def height(self):
        return self._page.page_h

    def resize(self, size, resample=None):
        """Box-downsample the supersampled raster to the final page size."""
        if (size[0], size[1]) != (self._page.page_w, self._page.page_h):
            raise ValueError("resize target must be the page size")
        self._raster = downsample(self._page.canvas, self._page.scale)
        return self

    @property
    def _target(self):
        if not hasattr(self, "_raster"):
            self._raster = downsample(self._page.canvas, self._page.scale)
        return self._raster

    def save(self, path, format=None):
        write_png(path, self._target)
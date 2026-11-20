"""Raster canvas and PNG writer for the front page.  Standard library only.

Pixels are 8-bit RGB in one flat bytearray.  The class paints in *design*
pixels multiplied by ``scale`` (the supersample factor), so the raster measures
width*scale by height*scale and every primitive — rules, rectangles, polygons,
ellipses, alpha-blended glyph coverage — works in page coordinates.  Output is
a PNG built from zlib and struct with an adaptive per-scanline filter, which
keeps the flat cream newsprint small and byte-identical between runs.

Exports: Canvas, Coverage (via canvas importers), write_png, encode_png,
downsample.
"""

import struct
import zlib

__all__ = ["Canvas", "Coverage", "write_png", "encode_png", "downsample"]


class Canvas:
    """An RGB raster with design-pixel geometry and supersampled pixels."""

    def __init__(self, width, height, scale=1, background=(255, 255, 255)):
        self.design_w = width
        self.design_h = height
        self.scale = scale
        self.w = width * scale
        self.h = height * scale
        self.buf = bytearray(bytes(background) * (self.w * self.h))

    # -- helpers --------------------------------------------------------
    def _s(self, v):
        return v * self.scale

    def _px(self, v):
        n = int(round(v * self.scale))
        return n if n > 0 else 1

    def fill(self, color):
        self.buf = bytearray(bytes(color) * (self.w * self.h))

    def get(self, x, y):
        i = (y * self.w + x) * 3
        b = self.buf
        return b[i], b[i + 1], b[i + 2]

    # -- solid shapes ---------------------------------------------------
    def _span(self, y, x0, x1, color):
        """Fill columns [x0, x1) of raster row y with colour."""
        if y < 0 or y >= self.h:
            return
        if x0 < 0:
            x0 = 0
        if x1 > self.w:
            x1 = self.w
        if x1 <= x0:
            return
        i = (y * self.w + x0) * 3
        self.buf[i:i + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1.0):
        """Axis-aligned rectangle in design pixels; edges are inclusive."""
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        X0 = int(round(self._s(x0)))
        X1 = int(round(self._s(x1)))
        Y0 = int(round(self._s(y0)))
        Y1 = int(round(self._s(y1)))
        if fill is not None:
            c = bytes(fill)
            run = c * max(0, X1 - X0 + 1)
            for y in range(max(0, Y0), min(self.h, Y1 + 1)):
                i = (y * self.w + max(0, X0)) * 3
                if X0 < 0:
                    run2 = c * (X1 + 1)
                else:
                    run2 = run
                self.buf[i:i + len(run2)] = run2
        if outline is not None:
            w = self._px(width)
            self._hrule(X0, X1, Y0, w, outline)
            self._hrule(X0, X1, Y1 - w + 1, w, outline)
            self._vrule(X0, Y0, Y1, w, outline)
            self._vrule(X1 - w + 1, Y0, Y1, w, outline)

    def _hrule(self, x0, x1, y0, thick, color):
        c = bytes(color)
        run = c * (x1 - x0 + 1)
        for y in range(y0, y0 + thick):
            if 0 <= y < self.h:
                i = (y * self.w + x0) * 3
                self.buf[i:i + len(run)] = run

    def _vrule(self, x0, y0, y1, thick, color):
        c = bytes(color)
        run = c * thick
        x0 = max(0, min(x0, self.w - thick))
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            i = (y * self.w + x0) * 3
            self.buf[i:i + thick * 3] = run

    def rule(self, x0, y0, x1, y1, width=1.0, fill=(0, 0, 0)):
        """A straight line of the given design-pixel thickness."""
        self.line(x0, y0, x1, y1, fill=fill, width=width)

    def line(self, x0, y0, x1, y1, fill=(0, 0, 0), width=1.0):
        """A segment rasterised as a run of thick pixels along its major axis.

        Shallow segments step in x, steep segments step in y; vertical and
        zero-length cases are handed to the vertical rule writer directly so a
        hairline never lands a pixel outside the raster row it belongs to.
        """
        ax, ay = self._s(x0), self._s(y0)
        bx, by = self._s(x1), self._s(y1)
        w = self._px(width)
        half = (w - 1) / 2.0
        dx, dy = bx - ax, by - ay
        if abs(dy) <= abs(dx):
            if ay > by:
                ax, ay, bx, by = bx, by, ax, ay
                dx, dy = bx - ax, by - ay
            x_lo, x_hi = (ax, bx) if ax <= bx else (bx, ax)
            slope = dy / dx if dx else 0.0
            if dx == 0:
                self._vrule(int(round(ax)),
                            int(round(min(ay, by))) - w // 2,
                            int(round(max(ay, by))) + w // 2, w, fill)
                return
            n = int(round(abs(dx))) + 1
            for i in range(n):
                t = i / (n - 1) if n > 1 else 0.0
                x = x_lo + (x_hi - x_lo) * t
                y = ay + slope * (x - ax)
                yy = int(round(y - half))
                self._hrule(int(round(x)), int(round(x)), yy, w, fill)
        else:
            if ax > bx:
                ax, ay, bx, by = bx, by, ax, ay
                dx, dy = bx - ax, by - ay
            y_lo, y_hi = (ay, by) if ay <= by else (by, ay)
            slope = dx / dy
            n = int(round(abs(dy))) + 1
            for i in range(n):
                t = i / (n - 1) if n > 1 else 0.0
                y = y_lo + (y_hi - y_lo) * t
                x = ax + slope * (y - ay)
                xx = int(round(x - half))
                self._vrule(xx, int(round(y)), int(round(y)), w, fill)

    def dashed(self, x0, y0, x1, y1, dash=7.0, gap=5.0, width=1.4,
               fill=(0, 0, 0)):
        total = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if total <= 0:
            return
        ux, uy = (x1 - x0) / total, (y1 - y0) / total
        pos = 0.0
        while pos < total:
            end = min(pos + dash, total)
            self.line(x0 + ux * pos, y0 + uy * pos,
                      x0 + ux * end, y0 + uy * end, fill=fill, width=width)
            pos = end + gap

    def dot(self, cx, cy, r, fill=(0, 0, 0)):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, fill=fill)

    def ring(self, cx, cy, r, width=1.4, fill=(0, 0, 0)):
        self.ellipse(cx - r, cy - r, cx + r, cy + r, outline=fill, width=width)

    def ellipse(self, x0, y0, x1, y1, outline=None, fill=None, width=1.0):
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = max(0.5, (x1 - x0) / 2.0)
        ry = max(0.5, (y1 - y0) / 2.0)
        X0 = int(round(self._s(x0)))
        X1 = int(round(self._s(x1)))
        Y0 = int(round(self._s(y0)))
        Y1 = int(round(self._s(y1)))
        inner = None
        if outline is not None:
            inner = (rx - width, ry - width)
        cx_s, cy_s = self._s(cx), self._s(cy)
        rx_s, ry_s = self._s(rx), self._s(ry)
        if inner is not None:
            irx, iry = max(0.0, self._s(inner[0])), max(0.0, self._s(inner[1]))
        for y in range(max(0, Y0), min(self.h, Y1 + 1)):
            dy = (y + 0.5 - cy_s) / ry_s
            if abs(dy) > 1.0:
                continue
            half = rx_s * (1.0 - dy * dy) ** 0.5
            xa = int(round(cx_s - half))
            xb = int(round(cx_s + half))
            if fill is not None and inner is None:
                self._span(y, xa, xb + 1, fill)
            elif fill is not None and inner is not None:
                self._span(y, xa, xb + 1, outline)
                if iry > 0 and abs(y + 0.5 - cy_s) <= iry:
                    f = (1.0 - ((y + 0.5 - cy_s) / iry) ** 2) ** 0.5
                    if f > 0:
                        ih = irx * f
                        self._span(y, int(round(cx_s - ih)),
                                   int(round(cx_s + ih)) + 1, fill)
            else:
                self._span(y, xa, xb + 1, outline)

    def polygon(self, points, outline=(0, 0, 0), fill=None, width=1.0):
        """Even-odd filled polygon, optionally outlined at ``width``."""
        pts = [(self._s(x), self._s(y)) for x, y in points]
        if fill is not None:
            ys = [p[1] for p in pts]
            y_lo = max(0, int(min(ys)))
            y_hi = min(self.h - 1, int(max(ys)) + 1)
            n = len(pts)
            for y in range(y_lo, y_hi + 1):
                yc = y + 0.5
                xs = []
                for i in range(n):
                    ax, ay = pts[i]
                    bx, by = pts[(i + 1) % n]
                    if (ay <= yc < by) or (by <= yc < ay):
                        xs.append(ax + (yc - ay) * (bx - ax) / (by - ay))
                xs.sort()
                for i in range(0, len(xs) - 1, 2):
                    self._span(y, int(round(xs[i])), int(round(xs[i + 1])),
                               fill)
        if outline is not None:
            n = len(pts)
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                self.line(ax / self.scale, ay / self.scale,
                          bx / self.scale, by / self.scale,
                          fill=outline, width=width)

    # -- coverage -------------------------------------------------------
    def paint_coverage(self, cov, x0, y0, color, alpha=1.0):
        """Alpha-blend a coverage buffer (values 0..255) onto the raster."""
        cw = cov.w
        ch = cov.h
        if cw <= 0 or ch <= 0:
            return
        buf = self.buf
        data = cov.data
        r, g, b = color
        W = self.w
        for yy in range(ch):
            Y = y0 + yy
            if Y < 0 or Y >= self.h:
                continue
            row = yy * cw
            base = Y * W * 3
            for xx in range(cw):
                v = data[row + xx]
                if v == 0:
                    continue
                X = x0 + xx
                if X < 0 or X >= W:
                    continue
                a = v / 255.0
                if alpha != 1.0:
                    a = a * alpha
                i = base + X * 3
                inv = 1.0 - a
                buf[i] = int(buf[i] * inv + r * a + 0.5)
                buf[i + 1] = int(buf[i + 1] * inv + g * a + 0.5)
                buf[i + 2] = int(buf[i + 2] * inv + b * a + 0.5)

    # -- output ---------------------------------------------------------
    def rows(self):
        """Yield the raster's rows as bytes, for the PNG encoder."""
        stride = self.w * 3
        buf = self.buf
        for y in range(self.h):
            yield bytes(buf[y * stride:(y + 1) * stride])

    def encode_png(self, level=9):
        return encode_png(self.w, self.h, self.rows(), level=level)


class Coverage:
    """An 8-bit coverage bitmap (one byte of 0..255 alpha per pixel)."""

    __slots__ = ("w", "h", "data")

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.data = bytearray(w * h)


def _paeth(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def encode_png(width, height, rows, level=9):
    """Encode 8-bit RGB rows as a PNG byte string.

    Each scanline tries all five PNG filters and keeps the one with the
    smallest sum of absolute differences — the standard heuristic, applied
    deterministically so two runs produce the same bytes.
    """
    stride = width * 3
    out = bytearray()
    prev = bytes(stride)
    for row in rows:
        row = bytes(row)
        if len(row) != stride:
            raise ValueError("row length mismatch")
        cands = [b"\x00" + row]
        up = bytes((row[i] - prev[i]) & 0xFF for i in range(stride))
        cands.append(b"\x02" + up)
        sub = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            sub[i] = (row[i] - left) & 0xFF
        cands.append(b"\x01" + bytes(sub))
        avg = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            avg[i] = (row[i] - ((left + prev[i]) >> 1)) & 0xFF
        cands.append(b"\x03" + bytes(avg))
        pae = bytearray(stride)
        for i in range(stride):
            left = row[i - 3] if i >= 3 else 0
            upleft = prev[i - 3] if i >= 3 else 0
            pae[i] = (row[i] - _paeth(left, prev[i], upleft)) & 0xFF
        cands.append(b"\x04" + bytes(pae))
        best = None
        best_score = None
        for cand in cands:
            score = sum(v if v < 128 else 256 - v for v in cand[1:])
            if best_score is None or score < best_score:
                best_score = score
                best = cand
        out += best
        prev = row

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(out), level)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", idat)
            + chunk(b"IEND", b""))


def write_png(path, canvas, level=9):
    with open(path, "wb") as fh:
        fh.write(canvas.encode_png(level=level))


def downsample(canvas, factor):
    """Box-downsample an RGB canvas by an integer factor.

    Averaging exactly factor*factor source pixels per destination pixel is
    what turns the supersampled type into printed type: the box filter keeps
    serifs crisp without the halo a sharpening kernel would leave on cream
    stock.
    """
    if factor == 1:
        return canvas
    out_w = canvas.w // factor
    out_h = canvas.h // factor
    src = canvas.buf
    sw = canvas.w
    dst = bytearray(out_w * out_h * 3)
    n = factor * factor
    half = n // 2
    for oy in range(out_h):
        sy0 = oy * factor
        o_row = oy * out_w * 3
        acc_r = [0] * out_w
        acc_g = [0] * out_w
        acc_b = [0] * out_w
        for dy in range(factor):
            base = ((sy0 + dy) * sw) * 3
            for ox in range(out_w):
                i = base + ox * factor * 3
                for k in range(factor):
                    j = i + k * 3
                    acc_r[ox] += src[j]
                    acc_g[ox] += src[j + 1]
                    acc_b[ox] += src[j + 2]
        for ox in range(out_w):
            o = o_row + ox * 3
            dst[o] = (acc_r[ox] + half) // n
            dst[o + 1] = (acc_g[ox] + half) // n
            dst[o + 2] = (acc_b[ox] + half) // n
    out = Canvas.__new__(Canvas)
    out.design_w = out_w
    out.design_h = out_h
    out.scale = 1
    out.w = out_w
    out.h = out_h
    out.buf = dst
    return out
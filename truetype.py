"""Minimal TrueType parser: cmap, loca, glyf, hmtx, head/hhea metrics.

Standard library only.  Reads the tables the renderer actually needs — a
format-4 character map, the glyph location table, simple and composite
glyph outlines, and horizontal advances — and caches outlines per glyph id.
"""

import struct


class TTFError(Exception):
    pass


class Font:
    """One .ttf file, parsed once, queried by glyph id or character."""

    def __init__(self, path):
        self.path = path
        with open(path, "rb") as fh:
            self.d = d = fh.read()
        if len(d) < 12:
            raise TTFError("truncated font: %s" % path)
        n = struct.unpack(">H", d[4:6])[0]
        self.t = {}
        for i in range(n):
            off = 12 + 16 * i
            tag = d[off:off + 4].decode("latin-1")
            _ck, o, ln = struct.unpack(">III", d[off + 4:off + 16])
            self.t[tag] = (o, ln)
        for need in ("head", "hhea", "hmtx", "maxp", "cmap", "loca", "glyf"):
            if need not in self.t:
                raise TTFError("missing table %s in %s" % (need, path))
        h = self.t["head"][0]
        self.upm = struct.unpack(">H", d[h + 18:h + 20])[0]
        self.locfmt = struct.unpack(">h", d[h + 50:h + 52])[0]
        hh = self.t["hhea"][0]
        self.ascent = struct.unpack(">h", d[hh + 4:hh + 6])[0]
        self.descent = struct.unpack(">h", d[hh + 6:hh + 8])[0]
        self.linegap = struct.unpack(">h", d[hh + 8:hh + 10])[0]
        self.num_hmetrics = struct.unpack(">H", d[hh + 34:hh + 36])[0]
        self.num_glyphs = struct.unpack(
            ">H", d[self.t["maxp"][0] + 4:self.t["maxp"][0] + 6])[0]
        self._load_cmap()
        self._load_loca()
        self._load_hmtx()
        self._outline_cache = {}

    # -- cmap -----------------------------------------------------------
    def _load_cmap(self):
        """Find the format-4 subtable (Unicode BMP) and unpack its segments."""
        d = self.d
        base = self.t["cmap"][0]
        n = struct.unpack(">H", d[base + 2:base + 4])[0]
        sub = None
        for i in range(n):
            pid, eid, off = struct.unpack(
                ">HHI", d[base + 4 + 8 * i:base + 12 + 8 * i])
            fmt = struct.unpack(">H", d[base + off:base + off + 2])[0]
            if fmt == 4 and (pid, eid) in ((3, 1), (0, 3), (3, 10)):
                sub = base + off
                break
        if sub is None:
            for i in range(n):
                pid, eid, off = struct.unpack(
                    ">HHI", d[base + 4 + 8 * i:base + 12 + 8 * i])
                if struct.unpack(">H", d[base + off:base + off + 2])[0] == 4:
                    sub = base + off
                    break
        if sub is None:
            raise TTFError("no format 4 cmap in %s" % self.path)
        segx2 = struct.unpack(">H", d[sub + 6:sub + 8])[0]
        seg = segx2 // 2
        self.seg = seg
        self.cmap_ends = struct.unpack(
            ">%dH" % seg, d[sub + 14:sub + 14 + segx2])
        p = sub + 16 + segx2
        self.cmap_starts = struct.unpack(">%dH" % seg, d[p:p + segx2])
        p += segx2
        self.cmap_deltas = struct.unpack(">%dh" % seg, d[p:p + segx2])
        p += segx2
        self.cmap_range_off = p
        self.cmap_ranges = struct.unpack(">%dH" % seg, d[p:p + segx2])

    def gid(self, ch):
        """Glyph id for a character via the format-4 segments."""
        c = ord(ch)
        if c > 0xFFFF:
            return 0
        starts = self.cmap_starts
        for i in range(self.seg):
            if starts[i] <= c <= self.cmap_ends[i]:
                if self.cmap_ranges[i] == 0:
                    return (c + self.cmap_deltas[i]) & 0xFFFF
                addr = (self.cmap_range_off + 2 * i + self.cmap_ranges[i]
                        + 2 * (c - starts[i]))
                g = struct.unpack(">H", self.d[addr:addr + 2])[0]
                if g == 0:
                    return 0
                return (g + self.cmap_deltas[i]) & 0xFFFF
        return 0

    # -- metrics --------------------------------------------------------
    def _load_loca(self):
        o = self.t["loca"][0]
        n = self.num_glyphs + 1
        if self.locfmt == 0:
            self.loca = [x * 2 for x in
                         struct.unpack(">%dH" % n, self.d[o:o + 2 * n])]
        else:
            self.loca = list(struct.unpack(">%dI" % n, self.d[o:o + 4 * n]))

    def _load_hmtx(self):
        o = self.t["hmtx"][0]
        n = self.num_hmetrics
        raw = struct.unpack(">%dH" % (2 * n), self.d[o:o + 4 * n])
        self.advances = list(raw[0::2])

    def advance(self, gid):
        if gid < len(self.advances):
            return self.advances[gid]
        return self.advances[-1]

    # -- outlines -------------------------------------------------------
    def _glyph_range(self, gid):
        if gid < 0 or gid >= self.num_glyphs:
            return None
        go = self.t["glyf"][0]
        s = go + self.loca[gid]
        e = go + self.loca[gid + 1]
        if e <= s:
            return None
        return s, e

    def outline(self, gid):
        """List of contours; each contour is [(x, y, on_curve), ...]."""
        cached = self._outline_cache.get(gid)
        if cached is not None:
            return cached
        result = self._build_outline(gid, 0)
        self._outline_cache[gid] = result
        return result

    def _build_outline(self, gid, depth):
        rng = self._glyph_range(gid)
        if rng is None:
            return []
        s, _e = rng
        d = self.d
        ncont = struct.unpack(">h", d[s:s + 2])[0]
        if ncont < 0:
            return self._composite(gid, s, depth)
        if ncont == 0:
            return []
        ends = struct.unpack(">%dH" % ncont, d[s + 10:s + 10 + 2 * ncont])
        p = s + 10 + 2 * ncont
        ilen = struct.unpack(">H", d[p:p + 2])[0]
        p += 2 + ilen
        npts = ends[-1] + 1
        flags = []
        while len(flags) < npts:
            f = d[p]
            p += 1
            flags.append(f)
            if f & 8:
                r = d[p]
                p += 1
                flags.extend([f] * r)
        del flags[npts:]
        xs = []
        v = 0
        for f in flags:
            if f & 2:
                dx = d[p]
                p += 1
                v += dx if f & 16 else -dx
            elif not f & 16:
                v += struct.unpack(">h", d[p:p + 2])[0]
                p += 2
            xs.append(v)
        ys = []
        v = 0
        for f in flags:
            if f & 4:
                dy = d[p]
                p += 1
                v += dy if f & 32 else -dy
            elif not f & 32:
                v += struct.unpack(">h", d[p:p + 2])[0]
                p += 2
            ys.append(v)
        contours = []
        start = 0
        for en in ends:
            contours.append([(xs[i], ys[i], bool(flags[i] & 1))
                             for i in range(start, en + 1)])
            start = en + 1
        return contours

    def _composite(self, gid, s, depth):
        """Composite glyph: recurse into components with offsets/scales."""
        if depth > 3:
            return []
        d = self.d
        p = s + 10
        out = []
        while True:
            flags, gi = struct.unpack(">HH", d[p:p + 4])
            p += 4
            if flags & 1:
                a1, a2 = struct.unpack(">hh", d[p:p + 4])
                p += 4
            else:
                a1, a2 = struct.unpack(">bb", d[p:p + 2])
                p += 2
            if flags & 2:
                dx = dy = 0
            else:
                dx, dy = a1, a2
            scale = 1.0
            if flags & 8:
                scale = struct.unpack(">h", d[p:p + 2])[0] / 16384.0
                p += 2
            elif flags & 0x40:
                sx = struct.unpack(">h", d[p:p + 2])[0] / 16384.0
                sy = struct.unpack(">h", d[p + 2:p + 4])[0] / 16384.0
                p += 4
                scale = (sx, sy)
            elif flags & 0x80:
                sx = struct.unpack(">h", d[p:p + 2])[0] / 16384.0
                sy = struct.unpack(">h", d[p + 2:p + 4])[0] / 16384.0
                p += 4
                scale = (sx, sy)
            for contour in self._build_outline(gi, depth + 1):
                if isinstance(scale, tuple):
                    out.append([(x * scale[0] + dx, y * scale[1] + dy, on)
                                for x, y, on in contour])
                elif scale != 1.0:
                    out.append([(x * scale + dx, y * scale + dy, on)
                                for x, y, on in contour])
                else:
                    out.append([(x + dx, y + dy, on)
                                for x, y, on in contour])
            if not flags & 32:
                break
        return out
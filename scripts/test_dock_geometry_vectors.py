"""Portable geometry oracle for the 269FC smoke vectors (not an ObjC runtime test)."""
import unittest


def covered(usable, candidate, dock):
    ux, uy, uw, uh = usable
    x, y, w, h = candidate
    dx, dy, dw, dh = dock
    # This oracle deliberately computes the edge from raw coordinates rather
    # than calling the Objective-C classifier under test.
    if w <= 0 or h <= 0 or dw <= 0 or dh <= 0 or uw <= 0 or uh <= 0:
        return None
    if (x - 2 <= dx and y - 2 <= dy and
            dx + dw <= x + w + 2 and dy + dh <= y + h + 2):
        return None
    spans_h = dy <= y + 2 and dy + dh >= y + h - 2
    spans_w = dx <= x + 2 and dx + dw >= x + w - 2
    if spans_h and abs(dx + dw - x) <= 2:
        result = (dx, y, x + w - dx, h)
    elif spans_h and abs(dx - (x + w)) <= 2:
        result = (x, y, dx + dw - x, h)
    elif spans_w and abs(dy + dh - y) <= 2:
        result = (x, dy, w, y + h - dy)
    elif spans_w and abs(dy - (y + h)) <= 2:
        result = (x, y, w, dy + dh - y)
    else:
        return None
    rx, ry, rw, rh = result
    if (rx < ux - 1 or ry < uy - 1 or
            rx + rw > ux + uw + 1 or ry + rh > uy + uh + 1):
        return None
    return result


class DockGeometryVectors(unittest.TestCase):
    def test_all_edges(self):
        usable = (10, 10, 180, 180)
        candidate = (40, 40, 100, 80)
        vectors = [
            ((20, 40, 20, 80), (20, 40, 120, 80)),
            ((140, 40, 20, 80), (40, 40, 120, 80)),
            ((40, 20, 100, 20), (40, 20, 100, 100)),
            ((40, 120, 100, 20), (40, 40, 100, 100)),
        ]
        for dock, expected in vectors:
            with self.subTest(dock=dock):
                self.assertEqual(covered(usable, candidate, dock), expected)

    def test_tolerances_and_rejection(self):
        candidate = (40, 40, 100, 80)
        self.assertEqual(covered((21, 39, 140, 82), candidate,
                                 (20, 40, 20, 80)), (20, 40, 120, 80))
        self.assertIsNone(covered((21.1, 39, 139.9, 82), candidate,
                                  (20, 40, 20, 80)))
        self.assertEqual(covered((39, 39, 122, 82), candidate,
                                 (142, 40, 20, 80)), (40, 40, 122, 80))
        self.assertIsNone(covered((10, 10, 180, 180), candidate,
                                  (142.1, 40, 20, 80)))
        self.assertIsNone(covered((40, 40, 100, 80), candidate,
                                  (140, 40, 20, 80)))


if __name__ == "__main__":
    unittest.main()

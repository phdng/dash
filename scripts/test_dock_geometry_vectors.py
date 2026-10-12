"""Portable 83FC/23D94/26654/269FC geometry vectors (not an ObjC runtime test)."""
import unittest
from math import isfinite


def valid_rect(rect):
    return all(isfinite(v) for v in rect) and rect[2] > 0 and rect[3] > 0


def decode_dock(state):
    if not state:
        return None
    x = ((state >> 48) & 0xffff) / 10
    y = ((state >> 32) & 0xffff) / 10
    width = ((state >> 16) & 0xffff) / 10
    height = (state & 0xffff) / 10
    return (x, y, width, height) if min(width, height) > 0 else None


def trim_edge(usable, dock):
    x, y, w, h = usable
    if not valid_rect(usable) or not valid_rect(dock):
        return usable
    dx, dy, dw, dh = dock
    ix, iy = max(x, dx), max(y, dy)
    ex, ey = min(x + w, dx + dw), min(y + h, dy + dh)
    iw, ih = ex - ix, ey - iy
    if iw <= 0 or ih <= 0:
        return usable
    if ih >= h - 2 and iw < w - 2:
        if ix <= x + 2 and x + w - ex >= 40:
            return (ex, y, x + w - ex, h)
        if ex >= x + w - 2 and ix - x >= 40:
            return (x, y, ix - x, h)
    elif iw >= w - 2 and ih < h - 2:
        if iy <= y + 2 and y + h - ey >= 40:
            return (x, ey, w, y + h - ey)
        if ey >= y + h - 2 and iy - y >= 40:
            return (x, y, w, iy - y)
    return usable


def covered(usable, candidate, dock):
    ux, uy, uw, uh = usable
    x, y, w, h = candidate
    if not valid_rect(usable) or not valid_rect(candidate) or not valid_rect(dock):
        return None
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


def coverage_decision(usable, candidate, dock, exit_enabled):
    if not exit_enabled:
        return 'no-exit', None
    if dock is None:
        return 'no-strip-published', None
    if not valid_rect(usable) or not valid_rect(candidate) or not valid_rect(dock):
        return 'no-window', None
    x, y, w, h = candidate
    dx, dy, dw, dh = dock
    if (x - 2 <= dx and y - 2 <= dy and
            dx + dw <= x + w + 2 and dy + dh <= y + h + 2):
        return 'already-inside', None
    spans_h = dy <= y + 2 and dy + dh >= y + h - 2
    spans_w = dx <= x + 2 and dx + dw >= x + w - 2
    adjacent = ((spans_h and (abs(dx + dw - x) <= 2 or
                              abs(dx - (x + w)) <= 2)) or
                (spans_w and (abs(dy + dh - y) <= 2 or
                              abs(dy - (y + h)) <= 2)))
    if not adjacent:
        return 'strip-not-adjacent', None
    expanded = covered(usable, candidate, dock)
    return ('covered', expanded) if expanded is not None else ('outside-usable', None)


def resolve_state(shell, usable, state, exit_enabled):
    """Independent data-level reconstruction of the initial and covered paths."""
    if not valid_rect(usable):
        return None
    dock = decode_dock(state)
    sx, sy, sw, sh = shell
    ux, uy, uw, uh = usable
    invalid_shell = not valid_rect(shell) or sw < 40 or sh < 40
    outside = (sx < ux - 1 or sy < uy - 1 or
               sx + sw > ux + uw + 1 or sy + sh > uy + uh + 1)
    if invalid_shell or outside:
        base = usable
        reason = 'measured-dock-nofrome' if dock else 'display-unmeasured-dock'
    elif sw < uw - 1 or sh < uh - 1:
        base = shell
        reason = 'carplay-subrect'
    else:
        base = shell
        reason = 'measured-dock' if dock else 'carplay-fullscreen'
    if dock and reason.startswith('measured-dock'):
        base = trim_edge(base, dock)
    coverage, expanded = coverage_decision(usable, base, dock, exit_enabled)
    final = expanded if expanded is not None else base
    final_reason = reason + '+dock' if expanded is not None and reason in (
        'carplay-subrect', 'measured-dock', 'measured-dock-nofrome') else (
        'covered+dock' if expanded is not None else reason)
    return base, final, coverage, final_reason


def layout_transition_for_snapshots(previous_shell, previous_usable,
                                    previous_state, previous_exit,
                                    next_shell, next_usable, next_state,
                                    next_exit):
    """Compare complete independent CarPlay snapshots without shared bounds."""
    before = resolve_state(previous_shell, previous_usable,
                           previous_state, previous_exit)
    after = resolve_state(next_shell, next_usable, next_state, next_exit)
    if before is None or after is None:
        return None
    if before[1] != after[1]:
        decision = ('restored' if decode_dock(previous_state) and
                    not decode_dock(next_state) else 'updated')
    elif before[3] != after[3]:
        decision = 'reason-only'
    else:
        decision = 'unchanged'
    return decision, before[1], after[1], before[3], after[3]


def layout_transition(shell, usable, previous_state, previous_exit,
                      next_state, next_exit):
    """Compatibility with previous shared shell/usable layout comparison."""
    return layout_transition_for_snapshots(shell, usable, previous_state,
                                           previous_exit, shell, usable,
                                           next_state, next_exit)


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

    def test_packed_state_direction_and_recovery(self):
        usable = (10, 20, 200, 120)
        states = [
            ((100, 200, 300, 1200), (40, 20, 170, 120)),
            ((1900, 200, 200, 1200), (10, 20, 180, 120)),
            ((100, 200, 2000, 200), (10, 40, 200, 100)),
            ((100, 1200, 2000, 200), (10, 20, 200, 100)),
        ]
        for words, expected in states:
            with self.subTest(words=words):
                packed = sum(word << shift for word, shift in
                             zip(words, (48, 32, 16, 0)))
                self.assertEqual(trim_edge(usable, decode_dock(packed)), expected)
        self.assertIsNone(decode_dock(0))
        self.assertIsNone(decode_dock(100 << 48))
        self.assertEqual(usable, trim_edge(usable, (100, 200, 20, 20)))
        left_packed = sum(word << shift for word, shift in
                          zip(states[0][0], (48, 32, 16, 0)))
        sequence = (left_packed, 0, left_packed)
        observed = [trim_edge(usable, decode_dock(value))
                    if decode_dock(value) else usable for value in sequence]
        self.assertEqual(observed, [states[0][1], usable, states[0][1]])

    def test_end_to_end_packed_state_transitions(self):
        usable = (10, 10, 180, 180)
        shell = (40, 40, 100, 80)
        left = (200 << 48) | (400 << 32) | (200 << 16) | 800
        sequence = [
            (left, True, (20, 40, 120, 80), 'covered', 'carplay-subrect+dock'),
            (left, False, shell, 'no-exit', 'carplay-subrect'),
            (0, True, shell, 'no-strip-published', 'carplay-subrect'),
            (left, True, (20, 40, 120, 80), 'covered', 'carplay-subrect+dock'),
        ]
        for state, enabled, expected, coverage, label in sequence:
            with self.subTest(state=state, enabled=enabled):
                initial, resolved, got_coverage, got_label = resolve_state(
                    shell, usable, state, enabled)
                self.assertEqual(initial, shell)
                self.assertEqual(resolved, expected)
                self.assertEqual(got_coverage, coverage)
                self.assertEqual(got_label, label)
        missing_shell = (0, 0, 0, 0)
        full_usable = (10, 20, 200, 120)
        measured = (100 << 48) | (200 << 32) | (300 << 16) | 1200
        self.assertEqual(resolve_state(missing_shell, full_usable, measured, False),
                         ((40, 20, 170, 120), (40, 20, 170, 120),
                          'no-exit', 'measured-dock-nofrome'))
        self.assertEqual(resolve_state(missing_shell, full_usable, 0, True),
                         (full_usable, full_usable,
                          'no-strip-published', 'display-unmeasured-dock'))
        self.assertIsNone(resolve_state(shell, (0, 0, 0, 0), left, True))

    def test_coverage_reason_branch_matrix(self):
        usable = (10, 10, 180, 180)
        candidate = (40, 40, 100, 80)
        vectors = [
            (None, True, 'no-strip-published'),
            ((20, 40, 20, 80), False, 'no-exit'),
            ((60, 60, 20, 20), True, 'already-inside'),
            ((170, 40, 20, 80), True, 'strip-not-adjacent'),
            ((20, 40, 20, 80), True, 'covered'),
        ]
        for dock, enabled, expected in vectors:
            with self.subTest(dock=dock, enabled=enabled):
                label, _ = coverage_decision(usable, candidate, dock, enabled)
                self.assertEqual(label, expected)
        self.assertEqual(coverage_decision((40, 40, 100, 80), candidate,
                                            (140, 40, 20, 80), True)[0],
                         'outside-usable')
        for dock, expected in [((60, 60, 20, 20), 'already-inside'),
                               ((170, 40, 20, 80), 'strip-not-adjacent')]:
            state = sum(int(part * 10) << shift for part, shift in
                        zip(dock, (48, 32, 16, 0)))
            initial, result, reason, label = resolve_state(candidate, usable,
                                                            state, True)
            self.assertEqual((initial, result, reason, label),
                             (candidate, candidate, expected, 'carplay-subrect'))

    def test_malformed_geometry_fail_closed(self):
        usable = (10, 10, 180, 180)
        shell = (40, 40, 100, 80)
        dock = (20, 40, 20, 80)
        for bad in [(float('nan'), 10, 180, 180),
                    (10, float('inf'), 180, 180),
                    (10, 10, -1, 180), (10, 10, 180, -1),
                    (10, 10, 180, 0)]:
            with self.subTest(bad=bad):
                self.assertIsNone(resolve_state(shell, bad, 0, True))
                self.assertIsNone(covered(bad, shell, dock))
                self.assertEqual(trim_edge(bad, dock), bad)
                self.assertEqual(coverage_decision(bad, shell, dock, True)[0],
                                 'no-window')
        malformed_shell = (float('nan'), 40, 100, 80)
        measured = (200 << 48) | (400 << 32) | (200 << 16) | 800
        base, result, _, label = resolve_state(malformed_shell, usable, measured, False)
        self.assertEqual(base, usable)
        self.assertEqual(result, usable)
        self.assertEqual(label, 'measured-dock-nofrome')
        self.assertEqual(coverage_decision(usable, shell,
                           (float('nan'), 40, 20, 80), True)[0], 'no-window')

    def test_packed_dock_host_layout_transition(self):
        usable = (10, 20, 200, 120)
        left = (100 << 48) | (200 << 32) | (300 << 16) | 1200
        full = (0, 0, 0, 0)
        left_clipped = (40, 20, 170, 120)
        self.assertEqual(layout_transition(full, usable, left, False,
                                           left, False),
                         ('unchanged', left_clipped, left_clipped,
                          'measured-dock-nofrome', 'measured-dock-nofrome'))
        self.assertEqual(layout_transition(full, usable, left, False,
                                           0, False)[0:3],
                         ('restored', left_clipped, usable))
        self.assertEqual(layout_transition(full, usable, 0, False,
                                           left, False)[0:3],
                         ('updated', usable, left_clipped))
        shell = (40, 40, 100, 80)
        cp_usable = (10, 10, 180, 180)
        adjacent = (200 << 48) | (400 << 32) | (200 << 16) | 800
        self.assertEqual(layout_transition(shell, cp_usable, adjacent,
                                           False, adjacent, True)[0:3],
                         ('updated', shell, (20, 40, 120, 80)))
        self.assertEqual(layout_transition(full, cp_usable, 0, True,
                                           adjacent, True),
                         ('reason-only', cp_usable, cp_usable,
                          'display-unmeasured-dock', 'measured-dock-nofrome'))
        self.assertIsNone(layout_transition(shell, (0, 0, 0, 0),
                                            adjacent, True, 0, False))

    def test_independent_carplay_snapshot_transitions(self):
        area = (10, 20, 200, 120)
        bigger_area = (10, 20, 240, 120)
        no_shell = (0, 0, 0, 0)
        left = (100 << 48) | (200 << 32) | (300 << 16) | 1200
        self.assertEqual(layout_transition_for_snapshots(
            no_shell, area, left, False,
            no_shell, bigger_area, left, False),
            ('updated', (40, 20, 170, 120), (40, 20, 210, 120),
             'measured-dock-nofrome', 'measured-dock-nofrome'))
        usable = (10, 10, 180, 180)
        shell = (40, 40, 100, 80)
        moved = (50, 40, 100, 80)
        self.assertEqual(layout_transition_for_snapshots(
            shell, usable, 0, True, moved, usable, 0, True)[0:3],
            ('updated', shell, moved))
        self.assertEqual(layout_transition_for_snapshots(
            shell, usable, 0, True, shell, (10, 10, 220, 180),
            0, True)[0:3], ('unchanged', shell, shell))
        self.assertEqual(layout_transition_for_snapshots(
            no_shell, area, left, False, no_shell,
            bigger_area, 0, False)[0:3],
            ('restored', (40, 20, 170, 120), bigger_area))
        self.assertEqual(layout_transition_for_snapshots(
            no_shell, area, 0, True, area, area, 0, True),
            ('reason-only', area, area,
             'display-unmeasured-dock', 'carplay-fullscreen'))
        self.assertIsNone(layout_transition_for_snapshots(
            shell, usable, 0, True, shell,
            (float('nan'), 10, 180, 180), left, True))
        self.assertIsNone(layout_transition_for_snapshots(
            shell, (0, 0, 0, 0), 0, True,
            moved, usable, left, False))

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

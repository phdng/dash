#!/usr/bin/env python3
"""Independent public K6 integer oracle; no claims about iPhone execution."""
from __future__ import annotations

MASK = (1 << 64) - 1


def mix(x: int, salt: int) -> int:
    a = x ^ ((salt + 0x6A09E667F3BCC909) & MASK)
    a ^= a >> 21
    a = (a * 0xBF58476D1CE4E5B9) & MASK
    if salt & 1:
        a ^= (x << 11) & MASK
    else:
        a = (a + (x >> 7) + 0x94D049BB133111EB) & MASK
    return (a ^ (a >> 28)) & MASK


def guard(x: int, salt: int) -> int:
    return ((x ^ 0xD6E8FEB86659FD93) +
            ((salt * 0x9E3779B97F4A7C15) & MASK)) & MASK


def values(i: int) -> tuple[int, int]:
    t = (0x123456789ABCDEF0 ^
         ((i * 0x9E3779B97F4A7C15) & MASK)) & MASK
    t ^= t >> 17
    t ^= (t << 23) & MASK
    t ^= t >> 11
    return (i if i < 16 else t), (
        (t >> 3) ^ ((i * 0xBF58476D1CE4E5B9) & MASK)) & MASK


def rotate(v: int) -> int:
    return ((v << 9) | (v >> 55)) & MASK


def checksums(count: int = 4096) -> tuple[str, str]:
    digest = guard_digest = 0
    for i in range(count):
        x, salt = values(i)
        digest = (rotate(digest ^ mix(x, salt)) + i) & MASK
        guard_digest = (rotate(guard_digest ^ guard(x, salt)) + i) & MASK
    return f"{digest:016x}", f"{guard_digest:016x}"

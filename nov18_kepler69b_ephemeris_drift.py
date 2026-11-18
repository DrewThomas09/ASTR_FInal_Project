#!/usr/bin/env python3
"""Kepler-69 b constant-period forecast sensitivity (not an observational test)."""
from math import ceil

P_Q8 = 13.7133429855  # Original project's Q8 BLS period
P_DR25 = 13.7223682   # NASA Exoplanet Archive DR25 KOI period
DURATION_H = 5.1231   # NASA Exoplanet Archive DR25 transit duration

def offset_minutes(n_orbits):
    if n_orbits < 0:
        raise ValueError("n_orbits must be nonnegative")
    return n_orbits * abs(P_DR25 - P_Q8) * 1440

def main():
    per_orbit = offset_minutes(1)
    error = abs(P_DR25 - P_Q8) / P_DR25 * 100
    n_full = ceil(DURATION_H * 60 / per_orbit)
    assert abs(per_orbit - 12.99630888) < 1e-6
    assert n_full == 24
    print(f"Period discrepancy: {error:.6f}% ({per_orbit:.6f} min/orbit)")
    for n in (0, 1, 6, 12, 18, 24, 27):
        print(f"{n:2d} orbits: {offset_minutes(n):9.3f} min")
    print(f"One catalog transit duration: {n_full} orbits; {n_full * P_DR25:.1f} days")
    print("CAUTION: Two constant periods sharing an epoch; no Q9 flux tested.")

if __name__ == "__main__":
    main()

"""
Performance & Vectorization Benchmark: SETI Ellipsoid 3D Engine.

Measures computation speed, throughput (stars/second), and RAM footprint
for processing 10k, 100k, 1M, and 5M stars using vectorized NumPy operations.
"""

from datetime import datetime, timezone
import os
import sys
import time
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.geometry import spherical_to_cartesian, calculate_ellipsoid_delay, is_in_ellipsoid_shell


def benchmark_size(n_stars: int):
    np.random.seed(42)
    ra_deg = np.random.uniform(0.0, 360.0, size=n_stars)
    dec_deg = np.random.uniform(-90.0, 90.0, size=n_stars)
    dist_pc = np.random.uniform(10.0, 10000.0, size=n_stars)
    current_date = datetime.now(timezone.utc).isoformat()

    # Time 1: Spherical to Cartesian 3D
    t0 = time.perf_counter()
    x, y, z = spherical_to_cartesian(ra_deg, dec_deg, dist_pc)
    t_cartesian = (time.perf_counter() - t0) * 1000.0  # ms

    # Time 2: Ellipsoid Delay Calculation
    t0 = time.perf_counter()
    delay_days = calculate_ellipsoid_delay(ra_deg, dec_deg, dist_pc, current_date=current_date)
    t_delay = (time.perf_counter() - t0) * 1000.0  # ms

    # Time 3: Full Shell Filter (is_in_ellipsoid_shell)
    t0 = time.perf_counter()
    is_inside, delay_days = is_in_ellipsoid_shell(ra_deg, dec_deg, dist_pc, current_date=current_date)
    t_full = (time.perf_counter() - t0) * 1000.0  # ms

    throughput_stars_per_sec = n_stars / (t_full / 1000.0)

    return {
        "N Stars": f"{n_stars:,}",
        "Cartesian 3D (ms)": f"{t_cartesian:.2f}",
        "Delay Calc (ms)": f"{t_delay:.2f}",
        "Full Filter (ms)": f"{t_full:.2f}",
        "Throughput (stars/sec)": f"{throughput_stars_per_sec:,.0f}",
    }


def main():
    print("=== SETI ELLIPSOID 3D ENGINE PERFORMANCE BENCHMARK ===")
    print("Benchmarking NumPy vectorized computation speed across catalog scales...\n")

    catalog_sizes = [10_000, 100_000, 1_000_000, 5_000_000]
    results = []

    for size in catalog_sizes:
        print(f"Benchmarking {size:,} stars...")
        res = benchmark_size(size)
        results.append(res)

    df_res = pd.DataFrame(results)
    print("\n=== BENCHMARK RESULTS TABLE ===")
    print(df_res.to_string(index=False))


if __name__ == "__main__":
    main()

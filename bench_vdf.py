#!/usr/bin/env python3
"""Benchmark the 1D phase VDF implementation."""

import argparse
import statistics
import time

from elc_vdf import generate_phase_vdf
from landscape import generate_formula


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark the 1D phase VDF implementation"
    )
    parser.add_argument(
        "--size", type=int, default=100, help="formula размерности"
    )
    parser.add_argument(
        "--steps", type=int, default=1000, help="число шагов VDF"
    )
    parser.add_argument(
        "--lam", type=float, default=0.5, help="λ параметр VDF"
    )
    parser.add_argument(
        "--runs", type=int, default=10, help="количество прогонов"
    )
    args = parser.parse_args()

    print(f"Generating formula of size {args.size}...")
    formula = generate_formula(args.size)

    msg = (
        f"Benchmarking Phase-VDF: steps={args.steps}, "
        f"lam={args.lam}, runs={args.runs}\n"
    )
    print(msg)

    times = []
    for i in range(1, args.runs + 1):
        start = time.perf_counter()
        generate_phase_vdf(formula, args.steps, args.lam)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"[Run {i}/{args.runs}] {elapsed:.6f}s")

    avg = statistics.mean(times)
    std = statistics.stdev(times) if len(times) > 1 else 0.0
    print(f"\nAverage elapsed time: {avg:.6f}s ± {std:.6f}s")


if __name__ == "__main__":
    main()

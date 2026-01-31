#!/usr/bin/env python3
"""
Responsible for measuring the running time of the matching engine
and the verifier. Also plots the respective functions with respect
to 'n', where 'n' denotes the number of hospitals/students.

USAGE:
    For testing the scalability and writing out the plot results,
    `python testing/scalability.py`
"""

import os
import sys
import random
import time
import tempfile
from pathlib import Path

# Add src to path so we can import matcher and verifier
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib.pyplot as plt
import numpy as np

from matcher import match, parse_input
from verifier import verify


def generate_random_prefs(n, seed=None):
    """Generate random preference lists for n hospitals and n students."""
    if seed is not None:
        random.seed(seed)

    students = list(range(1, n + 1))
    hospitals = list(range(1, n + 1))

    hospital_prefs = []
    for _ in range(n):
        prefs = students.copy()
        random.shuffle(prefs)
        hospital_prefs.append(prefs)

    student_prefs = []
    for _ in range(n):
        prefs = hospitals.copy()
        random.shuffle(prefs)
        student_prefs.append(prefs)

    return hospital_prefs, student_prefs


def time_matcher(hospital_prefs, student_prefs, runs=5):
    """Time the matcher over multiple runs and return average."""
    times = []
    for _ in range(runs):
        h_prefs = [p.copy() for p in hospital_prefs]
        s_prefs = [p.copy() for p in student_prefs]

        start = time.perf_counter()
        match(h_prefs, s_prefs)
        end = time.perf_counter()
        times.append(end - start)

    return sum(times) / len(times)


def time_verifier(input_file, matching_file, runs=5):
    """Time the verifier over multiple runs and return average."""
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        verify(input_file, matching_file)
        end = time.perf_counter()
        times.append(end - start)

    return sum(times) / len(times)


def run_analysis(sizes=None, runs=5):
    """Run the scalability analysis for given sizes."""
    if sizes is None:
        sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

    output_dir = Path(__file__).parent.parent / "graphs"
    output_dir.mkdir(exist_ok=True)

    matcher_times = []
    verifier_times = []

    print(f"{'n':>6} | {'Matcher (s)':>12} | {'Verifier (s)':>12}")
    print("-" * 38)

    for n in sizes:
        hospital_prefs, student_prefs = generate_random_prefs(n, seed=42)

        # time matcher
        mt = time_matcher(hospital_prefs, student_prefs, runs)
        matcher_times.append(mt)

        # generate matching for verifier
        matches = match([p.copy() for p in hospital_prefs], [p.copy() for p in student_prefs])

        # write temp files for verifier
        with tempfile.NamedTemporaryFile(mode='w', suffix='.in', delete=False) as f:
            input_file = f.name
            f.write(f"{n}\n")
            for prefs in hospital_prefs:
                f.write(' '.join(map(str, prefs)) + '\n')
            for prefs in student_prefs:
                f.write(' '.join(map(str, prefs)) + '\n')

        with tempfile.NamedTemporaryFile(mode='w', suffix='.out', delete=False) as f:
            matching_file = f.name
            # matches is already [[h, s], ...] with 1-indexed values from remote matcher
            for h, s in matches:
                f.write(f"{h} {s}\n")

        # time verifier
        vt = time_verifier(input_file, matching_file, runs)
        verifier_times.append(vt)

        os.unlink(input_file)
        os.unlink(matching_file)

        print(f"{n:>6} | {mt:>12.6f} | {vt:>12.6f}")

    return sizes, matcher_times, verifier_times, output_dir


def plot_results(sizes, matcher_times, verifier_times, output_dir):
    """Create and save the graphs."""
    # side by side plots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(sizes, matcher_times, 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('n (number of hospitals/students)')
    ax1.set_ylabel('Time (seconds)')
    ax1.set_title('Gale-Shapley Matcher Running Time')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log', base=2)

    ax2.plot(sizes, verifier_times, 'r-o', linewidth=2, markersize=6)
    ax2.set_xlabel('n (number of hospitals/students)')
    ax2.set_ylabel('Time (seconds)')
    ax2.set_title('Verifier Running Time')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log', base=2)

    plt.tight_layout()
    plt.savefig(output_dir / 'scalability.png', dpi=150)
    print(f"\nSaved: {output_dir / 'scalability.png'}")

    # combined plot
    fig2, ax = plt.subplots(figsize=(10, 6))
    ax.plot(sizes, matcher_times, 'b-o', linewidth=2, markersize=6, label='Matcher')
    ax.plot(sizes, verifier_times, 'r-s', linewidth=2, markersize=6, label='Verifier')
    ax.set_xlabel('n (number of hospitals/students)')
    ax.set_ylabel('Time (seconds)')
    ax.set_title('Algorithm Running Time Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log', base=2)

    plt.tight_layout()
    plt.savefig(output_dir / 'scalability_combined.png', dpi=150)
    print(f"Saved: {output_dir / 'scalability_combined.png'}")

    plt.close('all')


def save_data(sizes, matcher_times, verifier_times, output_dir):
    """Save timing data to CSV."""
    with open(output_dir / 'timing_data.csv', 'w') as f:
        f.write('n,matcher_time,verifier_time\n')
        for n, mt, vt in zip(sizes, matcher_times, verifier_times):
            f.write(f'{n},{mt:.9f},{vt:.9f}\n')
    print(f"Saved: {output_dir / 'timing_data.csv'}")


if __name__ == "__main__":
    print("Scalability Analysis")
    print("=" * 40)

    sizes, mt, vt, out_dir = run_analysis()

    print()
    plot_results(sizes, mt, vt, out_dir)
    save_data(sizes, mt, vt, out_dir)

    print("\nDone!")

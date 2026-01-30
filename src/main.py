import os
import glob
import sys
from matcher import *


"""
Main entry point for project. Triggers matching engine and verifier.

USAGE: 
    For running the G-S algorithm/verifier on a specific input file,
    `python src/main.py <filename>`
"""

def main():

    # Set up
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.dirname(base_dir)
    data_dir = os.path.join(proj_root, "data")

    print(f"Cleaning old output files in {data_dir}...")

    out_files = glob.glob(os.path.join(data_dir, "*.out"))
    for f in out_files:
        try:
            os.remove(f)
        except OSError as e:
            print(f"Failed to remove {f}: {e}")

    filename = "example.in"
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    input_path = os.path.join(proj_root, "data", filename)
    output_path = os.path.join(proj_root, "data", filename[:-3] + ".out")

    # Input parsing and Gale-Shapely algorithm execution
    print("Parsing input file " + filename)

    print("=" * 50)

    prefs = parse_input(input_path)

    if prefs:
        hospital_prefs = prefs[0]
        student_prefs = prefs[1]

        matching = match(hospital_prefs, student_prefs)

        print(matching)

        save(matching, output_path)

        print("Output saved to " + filename[:-3] + ".out")

    # Matching verification
    # TODO





if __name__ == "__main__":
    main()
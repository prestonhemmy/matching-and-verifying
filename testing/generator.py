import os
import random
import sys
import numpy as np


"""
Responsible for generating random preference list input files
of size 'n', where 'n' denotes the number of hospitals/students.

USAGE:
    For generating an input file with name 'filename',
    `python testing/generator.py <n> <filename>`
"""
def generate(n, filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    proj_root = os.path.dirname(base_dir)
    path = os.path.join(proj_root, "data", filename)

    try:
        with open(path, 'w') as f:
            f.write(f"{n}\n")

            for _ in range(1, 2 * n + 1):
                prefs = random.sample(range(1, n + 1), n)
                f.write(" ".join(map(str, prefs)) + "\n")
    except Exception as e:
        print(f"Error: {e}")





if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Usage: python generator.py <n> <filename>")

    n = int(sys.argv[1])
    filename = sys.argv[2]

    generate(n, filename)
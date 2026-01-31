import itertools
import numpy as np


"""
Input file parsing, output file writing, and Gale-Shapely implementation.
"""

def parse_input(filename):
    """Reads a multiline input file containing space-separated integers."""

    try:
        with (open(filename, 'r') as f):
            n = int(f.readline().strip())                                   # extract leading int
            data = np.genfromtxt(itertools.islice(f, 0, None), ndmin=2, dtype=int)   # extract preference rankings

            if len(data) != 2 * n:
                raise IOError(f"File {filename} has incorrect number of rows")

            return data.tolist()[:n], data.tolist()[n:]

    except IOError as e:
        print(f"Error reading file: {e}")
        return []
    except ValueError:
        print(f"Error: Expected a nonempty file.")
        return []

def match(hospital_prefs, student_prefs, verbose=True):
    """
    Outputs a multiline file containing a rows of (hospital, student) pairs,
    where each hospital and each student appears in exactly one pair.
    """

    res = []
    n = len(hospital_prefs)

    # convert to zero-indexed
    hospital_prefs = [[s - 1 for s in prefs] for prefs in hospital_prefs]
    student_prefs = [[h - 1 for h in prefs] for prefs in student_prefs]

    free_hospitals = set(range(0, n))
    free_students = set(range(0, n))

    # Binary 'proposed' list tracking which students each hospital has proposed to.
    # 0s indicate not yet proposed and 1s indicate a previous proposal. Takes the form:
    #   [   hospital  1 ,   hospital 2  ,   hospital 3   ]
    #   [ [ s1, s2, s3 ], [ s1, s2, s3 ], [ s1, s2, s3 ] ]
    proposed = [[0 for _ in range(n)] for _ in range(n)]

    if verbose:
        print("Set status:")
        print(f"free_hospitals: {free_hospitals}")
        print(f"free_students: {free_students}")

    while free_hospitals:
        # select a free hospital 'h'
        h = free_hospitals.pop()
        for s in hospital_prefs[h]:
            # select highest-ranked student 's' whom 'h' has not yet proposed to
            if not proposed[h][s]:
                proposed[h][s] = 1
                break

        if verbose:
            print(f"Hospital h = {h + 1}")
            print(f"Highest-ranked student s = {s + 1} has not yet been proposed to by h")

        # check if 's' is free
        if s in free_students:
            res.append([h + 1, s + 1])  # convert back to 1-indexed for file output
            free_students.remove(s)

            if verbose:
                print(f"Student {s + 1} is now paired with hospital {h + 1}")

        # o.w. 's' is currently paired with 'h_old'
        else:
            for hos, stu in res:
                if stu - 1 == s:
                    h_old = hos - 1

            if verbose:
                print(f"Hospital {h_old + 1} is currently paired with student {s + 1}")

            # check if 's' prefers 'h_old' to 'h'
            if student_prefs[s].index(h_old) < student_prefs[s].index(h):
                if verbose:
                    print(f"Student {s + 1} prefers previous partner, hospital {h_old + 1} to hospital {h + 1} since student {s + 1} has the preference list {student_prefs[s]} (0-indexed)")
                free_hospitals.add(h)       # 'h' remains free

            # o.w. 's' prefers 'h' to 'h_old'
            else:
                if verbose:
                    print(f"Student {s + 1} prefers new partner, hospital {h + 1} to hospital {h_old + 1} since student {s + 1} has the preference list {student_prefs[s]} (0-indexed)")
                res.remove([h_old + 1, s + 1])
                res.append([h + 1, s + 1])
                free_hospitals.add(h_old)   # 'h_old' becomes free again

        if verbose:
            print("Set status:")
            print(f"free_hospitals: {free_hospitals}")
            print(f"free_students: {free_students}")
            print("-" * 50)

    return res

def save(matching, filename):
    np.savetxt(filename, matching, fmt="%d")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 matcher.py <input_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    prefs = parse_input(input_file)

    if not prefs:
        sys.exit(1)

    hospital_prefs, student_prefs = prefs
    matching = match(hospital_prefs, student_prefs, verbose=False)

    # output in required format: "i j" per line
    for h, s in sorted(matching):
        print(f"{h} {s}")

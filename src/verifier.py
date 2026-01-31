import sys
from matcher import parse_input


"""
Verifies outputted matching is (a) valid and (b) stable.
"""

def parse_matching(filename):
    """Read the matching file and return list of (hospital, student) tuples."""
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()

            if not content:
                return []

            matches = []
            for line in content.split('\n'):
                parts = line.split()
                if len(parts) != 2:
                    return None
                h, s = int(parts[0]), int(parts[1])
                matches.append((h, s))

            return matches

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        return None
    except ValueError:
        return None


def check_validity(matches, n):
    """Check that each hospital and student is matched exactly once."""
    if n == 0:
        return len(matches) == 0, None

    if len(matches) != n:
        return False, f"INVALID (expected {n} pairs, got {len(matches)})"

    hospitals = []
    students = []

    for h, s in matches:
        if h < 1 or h > n:
            return False, f"INVALID (hospital {h} out of range)"
        if s < 1 or s > n:
            return False, f"INVALID (student {s} out of range)"
        hospitals.append(h)
        students.append(s)

    # check for duplicates
    if len(hospitals) != len(set(hospitals)):
        for h in hospitals:
            if hospitals.count(h) > 1:
                return False, f"INVALID (hospital {h} appears more than once)"

    if len(students) != len(set(students)):
        for s in students:
            if students.count(s) > 1:
                return False, f"INVALID (student {s} appears more than once)"

    return True, None


def check_stability(matches, hospital_prefs, student_prefs):
    """Check that there are no blocking pairs."""
    n = len(hospital_prefs)

    if n == 0:
        return True, None

    # build lookup: who is each hospital/student matched to?
    hospital_partner = {}
    student_partner = {}

    for h, s in matches:
        hospital_partner[h] = s
        student_partner[s] = h

    # check all pairs for blocking
    for h in range(1, n + 1):
        current_student = hospital_partner[h]
        h_prefs = hospital_prefs[h - 1]

        # find students that h prefers over their current match
        current_rank = h_prefs.index(current_student)

        for s in h_prefs[:current_rank]:
            current_hospital = student_partner[s]
            s_prefs = student_prefs[s - 1]

            # if s also prefers h over their current match, it's a blocking pair
            if s_prefs.index(h) < s_prefs.index(current_hospital):
                return False, f"UNSTABLE (blocking pair: hospital {h} and student {s})"

    return True, None


def verify(input_file, matching_file):
    """Main verification function."""
    prefs = parse_input(input_file)

    if not prefs:
        return "INVALID (could not parse input file)", False

    hospital_prefs, student_prefs = prefs
    n = len(hospital_prefs)

    matches = parse_matching(matching_file)

    if matches is None:
        return "INVALID (could not parse matching file)", False

    # check validity first
    valid, err = check_validity(matches, n)
    if not valid:
        return err, False

    # then check stability
    stable, err = check_stability(matches, hospital_prefs, student_prefs)
    if not stable:
        return err, False

    return "VALID STABLE", True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 verifier.py <input_file> <matching_file>", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    matching_file = sys.argv[2]

    result, success = verify(input_file, matching_file)
    print(result)
    sys.exit(0 if success else 1)

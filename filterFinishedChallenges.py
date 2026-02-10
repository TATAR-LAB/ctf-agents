#!/usr/bin/env python3
"""
Filter finished challenge log file and extract names of challenges that failed to run or had exceptions.

Command syntax: uv run filterFinishedChallenges.py <input_file> <output_file>
"""
import os
import sys

def parse_challenge_log(input_file, output_file):
    """
    Parse the input file line by line and extract challenge names
    that contain 'FAILED TO RUN' or 'EXCEPTION'.

    Args:
        input_file: Path to the input log file
        output_file: Path to the output file for filtered results
    """
    challenge_names = set()  # Use set to avoid duplicates

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Check if line contains "FAILED TO RUN" or "EXCEPTION"
            if "FAILED TO RUN" in line or "EXCEPTION" in line:
                # Extract the challenge name (first part before the first " - ")
                parts = line.split(" - ")
                if parts:
                    challenge_name = parts[0].strip()
                    challenge_names.add(challenge_name)

    # Write to output file, sorted for consistency
    with open(output_file, 'w') as f:
        for name in sorted(challenge_names):
            f.write(f"{name}\n")

    print(f"Results written to {output_file}")
def main():
    if len(sys.argv) > 2:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Incorrect parameter count")
        return
    #cheeck if input file exists
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist")
        return
    parse_challenge_log(input_file, output_file)
    # Create output file if it doesn't exist
    if not os.path.exists(output_file):
        with open(output_file, 'w') as f:
            pass  # Create empty file
        print(f"Created filtered output challenges file: {output_file}")
    parse_challenge_log(input_file, output_file)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Filter finished challenge log file and extract names of challenges that failed to run or had exceptions.
Doesn't include challenges that previously sucesfully ran

Command syntax: uv run filterFinishedChallengesManual.py <input_file> <output_file>
"""
import os
import sys
import fcntl

def parseChallengeLog(inputFile, outputFile):
    """
    Parse the input file line by line and extract challenge names
    that contain 'FAILED TO RUN' or 'EXCEPTION'.

    Args:
        inputFile: Path to the input log file
        outputFile: Path to the output file for filtered results
    """
    challengeNames = set()  # Use set to avoid duplicates
    with open(inputFile, 'r') as f:
        # lock the file
        fcntl.flock(f, fcntl.LOCK_EX)
        #read in all lines
        lines = [line.strip() for line in f if line.strip()]  # Read all non-empty lines
        # unlock the file
        fcntl.flock(f, fcntl.LOCK_UN)
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check if line contains "FAILED TO RUN" or "EXCEPTION"
        if "FAILED TO RUN" in line or "EXCEPTION" in line:
            # Extract the challenge name (first part before the first " - ")
            parts = line.split(" - ")
            if parts:
                challengeName = parts[0].strip()
                challengeNames.add(challengeName)
                #go back through file and check for another instance of same challenge
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    #if there is another instance of same challenge that doesn't have an error
                    if challengeName in line and ("FAILED TO RUN" not in line and "EXCEPTION" not in line):
                        challengeNames.remove(challengeName)
                        #ensure you don't try to remove again (is a set will only have one instance)
                        break
    #check if no failed challenges were found
    if(len(challengeNames) == 0):
        print("No challenges left to be ran")
        return False
    # Create output file if it doesn't exist
    if not os.path.exists(outputFile):
        with open(outputFile, 'w') as f:
            pass  # Create empty file
        print(f"Created filtered output challenges file: {outputFile}")
    # Write filtered challenges to input challenges file
    with open(outputFile, 'w') as f:
        # lock the file
        fcntl.flock(f, fcntl.LOCK_EX)
        for name in challengeNames:
            f.write(f"{name}\n")
        # unlock the file
        fcntl.flock(f, fcntl.LOCK_UN)
    print(f"Results written to {outputFile}")
    print("-" * 60)
    return True
def main():
    if len(sys.argv) > 2:
        inputFile = sys.argv[1]
        outputFile = sys.argv[2]
    else:
        print("Incorrect parameter count")
        return
    #cheeck if input file exists
    if not os.path.exists(inputFile):
        print(f"Input file {inputFile} does not exist")
        return
    parseChallengeLog(inputFile, outputFile)
if __name__ == "__main__":
    main()


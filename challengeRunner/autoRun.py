"""
Script to autorun dcipher commands over an inputted challenge list file to a outputted list of finished files
Deletes entries for completed challenges from input, and adds them to output file with log info
"""

import subprocess
import os
import sys
import fcntl
import filterFinishedChallenges

#import configs
try:
    from autoRunConfig import logDir, config, split, input_file, finished_file
except ImportError as e:
    print("Copy autoRunConfig.template.py to autoRunConfig.py and customize it.")
    print(f"Details: {e}")
    sys.exit(1)

def append_to_finished(finished_file, challenge_name, output):
    """
    Append the challenge name to the finished challenges file with status.

    Args:
        finished_file: Path to the finished challenges file
        challenge_name: Challenge name to append
        output: The output of d-cipher framework
    """
    # Also check the full output for errors
    output = output.lower()
    # Check for solved status
    status_parts = [challenge_name]
    #check for exceptions and improper split selection
    if 'traceback (most recent call last)' in output or 'keyerror' in output:
        status_parts.append('FAILED')
        # Extract the error type
        if 'keyerror' in output:
            status_parts.append('KEY_ERROR')
        elif 'traceback (most recent call last)' in output:
            status_parts.append('FAILED TO RUN')
    elif 'challenge solved' in output:
        status_parts.append('SOLVED')
    else:
        status_parts.append('NOT_SOLVED')
    # append the last line of log info
    lines = output.strip().split('\n')
    last_line = lines[-1].strip()
    if last_line:
        status_parts.append(last_line)

    status_line = ' - '.join(status_parts)
    print("status_line:", status_line)
    #write log info the finished list of challenges (including challenges that need to be re-run)
    with open(finished_file, 'a') as f:
        #lock the file
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(f"{status_line}\n")
        f.flush()
        # unlock the file
        fcntl.flock(f, fcntl.LOCK_UN)
    print(f"✓ Added to finished challenges: {status_line}", flush=True)

def get_next_challenge(input_file):
    """
    Get the next challenge from the input file and claim it atomically.

    Args:
        input_file: Path to the input file
    Returns:
        Challenge name or None if no unclaimed challenges remain
    """
    try:
        with open(input_file, 'r+') as f:
            #lock the file
            fcntl.flock(f, fcntl.LOCK_EX)

            # Read all lines
            lines = f.readlines()

            # Find the first unclaimed challenge
            challenge_name = None
            for i, line in enumerate(lines):
                #if challenge unclaimed
                if 'CLAIMED' not in line.strip():
                    challenge_name = line.strip()
                    # Mark this challenge as claimed
                    lines[i] = f"{challenge_name} CLAIMED\n"
                    break
            # If we found a challenge, write back the file with the claim marker
            if challenge_name is not None:
                f.seek(0)
                f.writelines(lines)
                f.flush()
                print(f"✓ Claimed '{challenge_name}' from input file")

            # unlock the file
            fcntl.flock(f, fcntl.LOCK_UN)
        return challenge_name

    except Exception as e:
        print(f"⚠ Error reading from input file: {e}")
        return None
def remove_from_input_file(input_file, challenge_name):
    """
    Remove the challenge name from the input file.

    Args:
        input_file: Path to the input file
        challenge_name: Challenge name to remove
    """
    try:
        with open(input_file, 'r+') as f:
            #lock file
            fcntl.flock(f, fcntl.LOCK_EX)
            lines = f.readlines()

            #filter out challenge from inputfile
            remaining_lines = [line for line in lines
                               if not (line.strip() == challenge_name or
                                       line.strip() == f"{challenge_name} CLAIMED")]

            # Write back the remaining challenges
            f.seek(0)
            f.writelines(remaining_lines)
            f.truncate()
            f.flush()
            #unlock file
            fcntl.flock(f, fcntl.LOCK_UN)
        print(f"✓ Removed '{challenge_name}' from input file")
    except Exception as e:
        print(f"⚠ Warning: Could not remove '{challenge_name}' from input file: {e}")

def run_dcipher_command(challenge_name):
    """
    Run the dcipher command with the given challenge name.

    Args:
        challenge_name: The challenge to run

    Returns:
        Tuple of (success: bool, output: str) where output contains the command output
    """
    cmd = [
        "uv", "run", os.path.expanduser("~/ctf-agents/run_dcipher.py"),
        "--logdir", logDir,
        "--config", config,
        "--split", split,
        "--challenge", challenge_name,
        "--keys", os.path.expanduser("~/ctf-agents/keys.cfg"),
    ]

    try:
        print(f"Running command for challenge: {challenge_name}")

        # Run with real-time output streaming
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        # Capture output while printing in real-time
        output = []
        for line in process.stdout:
            print(line, end='')  # Print to console immediately
            output.append(line)
        # Wait for process to complete
        return_code = process.wait()
        if return_code == 0:
            print(f"Command completed successfully for: {challenge_name}")
            return output
        else:
            print(f"Command failed for {challenge_name} with return code: {return_code}")
            return output
    except Exception as e:
        print(f"Command failed for {challenge_name}: {e}")
        return ""

def main():
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
        print(f"Please create this file with one challenge name per line.")
        sys.exit(1)

    # Create log directory if it doesn't exist
    os.makedirs(logDir, exist_ok=True)   # HAVENT TESTED THIS

    # Create finished file if it doesn't exist
    if not os.path.exists(finished_file):
        with open(finished_file, 'w') as f:
            pass  # Create empty file
        print(f"Created finished challenges file: {finished_file}")

    print("=" * 60)

    #for each challenge run command and process files
    #TODO need to implement a time check to skip a challenge if it takes too long !!!!!!!!!!!!!!
    while True:
        # Get next unclaimed challenge and mark it as claimed atomically
        # This prevents other processes from picking up the same challenge
        challenge_name = get_next_challenge(input_file)

        #get_next_challenge returns none if it cannot locate an unclaimed file
        if challenge_name is None:
            print("\nNo more challenges to process")
            break

        # Run the command
        output = run_dcipher_command(challenge_name)
        #extract only 15 lines
        output = output[-15:]
        #put back into a string instead of array so methods can parse properly
        output = "".join(output)

        #process the output
        append_to_finished(finished_file, challenge_name, output)
        remove_from_input_file(input_file, challenge_name)

        print("Challenged completed.", flush=True)
        print("-" * 60)

    print("\n" + "=" * 60)
    print("Processing complete!")
    print(f"Check {finished_file} for successfully completed challenges.")

if __name__ == "__main__":
    main()

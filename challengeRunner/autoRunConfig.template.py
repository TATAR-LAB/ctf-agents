"""
Copy this file to config.py and customize for your setup.
autoRunConfig.py is gitignored and won't be overwritten by pulls.
"""
#Ensure to include this for the config file to function
import os

# Create a directory for the log files with the name of the config you are using
logDir = os.path.expanduser("~/ctf-agents/logs_dcipher/jupyter/<YOUR_LOG_DIRECTORY>")  # e.g., "~/logs_dcipher/jupyter/kali_generic"

# Ensure this is the correct config for the configuration you want to run
config = os.path.expanduser("~/ctf-agents/configs/<YOUR_CONFIG_PATH>")  # e.g., "~/ctf-agents/configs/tatar-project/RQ1_RQ2/kali_generic.yaml"

# Make sure you select the correct split
split = "test"  # Options: "test", "development"

# Files for the challenges 
inputFile = "<YOUR_INPUT_FILE>"  # e.g., "inputChallenges.txt" - File containing challenge names (one per line)
finishedFile = f"{logDir}/<YOUR_FINISHED_FILE>"  # e.g., "finishedChallenges.txt" - File tracking completed challenges - Goes into parent directory of log files

import json
import os
from pathlib import Path

exitReasonDictionary = {}
categoryDictionary = {}
categoryNameDictionary = {"rev": "reverse engineering", "for": "digital forensics", "msc": "miscellaneous", "cry": "cryptography", "pwn": "binary exploitation (pwn)", "web": "web server"}
nameDictionary = {}
seenChallenges = set()
failedChallengeList = []
directoryPath = Path('logs_dcipher/jupyter/kali_generic/jupyter/default') 

regCount = 0      # Regular challenge counter
failedCount = 0   # Failed challenge counter (errors)
solvedCount = 0   # Solved challenge counter
unsolvedCount = 0 # Unsolved challenge counter
totalCount = 0    # Total unique challenges attempted

def undo_entry(rCat, stored):
    """Undo a previously processed entry's contribution to all counters."""
    global regCount, solvedCount, failedCount, unsolvedCount

    categoryDictionary[rCat][0] -= stored['time_taken']
    categoryDictionary[rCat][1] -= stored['total_cost']
    categoryDictionary[rCat][2] -= 1
    categoryDictionary[rCat][3] -= 1 if stored['exit_reason'] == 'solved' else 0
    categoryDictionary[rCat][4] -= 1 if stored['exit_reason'] != 'solved' else 0
    categoryDictionary[rCat][5][stored['exit_reason']] -= 1
    categoryDictionary[rCat][10] -= 1 if stored['exit_reason'] != 'solved' else 0

    if stored['exit_reason'] == 'solved':
        solvedCount -= 1
    elif stored['exit_reason'] == 'error':
        failedCount -= 1
        unsolvedCount -= 1
        failedChallengeList.remove(stored['rName'])
    else:
        unsolvedCount -= 1

    if stored['exit_reason'] != 'error':
        regCount -= 1

for item in directoryPath.iterdir():
    if item.is_file():
        with open(item,'r') as rFile:
            jFile = json.load(rFile)
        rArray = rFile.name.split("-")
        rArray.pop()
        rCat = rArray[1]
        rName = '-'.join(rArray).split("/")[-1]

        exit_reason = jFile['exit_reason']

        if rName in nameDictionary:
            stored = nameDictionary[rName]
            old_exit_reason = stored['exit_reason']

            # New is error -> always keep old, skip this one
            if exit_reason == 'error':
                print(f"Duplicate found (new is error, keeping old): {item}")
                continue

            # Both are failed (non-error) -> keep old, skip this one
            if exit_reason != 'solved' and old_exit_reason != 'solved':
                print(f"Duplicate found (both failed, keeping old): {item}")
                continue

            # New is solved and old was failed -> undo old, fall through to process new
            if exit_reason == 'solved' and old_exit_reason != 'solved':
                print(f"Duplicate found (new is better, replacing old): {item}")
                undo_entry(rCat, stored)
                del nameDictionary[rName]

        # Track unique challenges via a set that is never modified after being added to
        if rName not in seenChallenges:
            totalCount += 1
            seenChallenges.add(rName)

        # Increment counters for the current file
        if exit_reason == 'solved':
            solvedCount += 1
        elif exit_reason == 'error':
            failedChallengeList.append(rName)
            failedCount += 1
            unsolvedCount += 1
        else:
            unsolvedCount += 1

        nameDictionary[rName] = {
            'exit_reason': exit_reason,
            'time_taken': jFile['time_taken'],
            'total_cost': jFile['total_cost'],
            'rName': rName
        }

        if not rCat in categoryDictionary:
            categoryDictionary.update({rCat : [0, 0, 0, 0, 0, {}, "", 0, "", 0, 0]})
            # Time, cost, amount of entries, solved, failed, exit reason dictionary, longest challenge, time, most expensive challenge, cost, unsolved

        if not exit_reason in categoryDictionary[rCat][5]:
            categoryDictionary[rCat][5].update({exit_reason : 0})

        categoryDictionary[rCat][0] += jFile['time_taken']
        categoryDictionary[rCat][1] += jFile['total_cost']
        categoryDictionary[rCat][2] += 1
        categoryDictionary[rCat][3] += 1 if exit_reason == 'solved' else 0
        categoryDictionary[rCat][4] += 1 if exit_reason != 'solved' else 0
        categoryDictionary[rCat][5][exit_reason] += 1
        categoryDictionary[rCat][6] = rName if jFile['time_taken'] > categoryDictionary[rCat][7] else categoryDictionary[rCat][6]
        categoryDictionary[rCat][7] = jFile['time_taken'] if jFile['time_taken'] > categoryDictionary[rCat][7] else categoryDictionary[rCat][7]
        categoryDictionary[rCat][8] = rName if jFile['total_cost'] > categoryDictionary[rCat][9] else categoryDictionary[rCat][8]
        categoryDictionary[rCat][9] = jFile['total_cost'] if jFile['total_cost'] > categoryDictionary[rCat][9] else categoryDictionary[rCat][9]
        categoryDictionary[rCat][10] += 1 if exit_reason != 'solved' else 0

        if exit_reason != 'error':
            regCount += 1

print(f"\nTOTAL COMPLETED CHALLENGES: {regCount}")
print(f"Total unique attempted challenges (incl. errors): {totalCount}\n")
print(f"Solved: {solvedCount}, Errors (failed): {failedCount}")
print(f"Unsolved: {unsolvedCount} ({((unsolvedCount/regCount)*100):.1f}% unsolved | {((solvedCount/regCount)*100):.1f}% solved)\n")

for i, v in categoryDictionary.items():
    averageRawTime = (v[0]/v[2])
    averageMinutes = averageRawTime/60
    averageSeconds = averageRawTime%60
    mostSeconds = v[7]%60
    mostMinutes = (v[7]/60)%60
    mostHours = (v[7]/60)/60

    print(f"Stats for {categoryNameDictionary[i]} ({v[2]} challenges. Solved: {v[3]}, Unsolved: {v[10]} (Errors: {v[5].get('error', 0)}) | {((v[3]/v[2])*100):.1f}% solved):")
    print(f"\tAverage time taken: {averageMinutes:.1f} minutes and {averageSeconds:.1f} seconds | Raw: {averageRawTime:.3f}")
    print(f"\tAverage total cost: ${(v[1])/(v[2]):.2f}")
    print(f"\tLongest challenge: {v[6]} ({mostHours:.1f} hours {mostMinutes:.1f} minutes and {mostSeconds:.1f} seconds | Raw: {v[7]:.3f} seconds)")
    print(f"\tMost expensive challenge: {v[8]} (${v[9]:.2f})")
    print(f"\tSolve rate per dollar: {v[3]/v[1]:.2f}")
    print(f"\tExit reasons: ")
    for k, j in v[5].items():
        print(f"\t\t{k} -> {j}")
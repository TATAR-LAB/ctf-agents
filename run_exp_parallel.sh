#!/bin/bash
#
# Runs 200 test challenges with any configuration
# Non-server challenges run in parallel, server challenges run sequentially
#
# > bash run_exp_parallel.sh [--parallel N] [--resume|--clean|--help]
#

set -eu
(set -o pipefail 2>/dev/null) && set -o pipefail

# Configuration
CONFIG="configs/tatar-project/RQ1_RQ2/ubuntu_tips.yaml"
SPLIT="test"
KEYS="./keys.cfg"
LOG_DIR="exp-logs"
RESULTS_FILE="exp-results/experiment_results_ubuntu_tips.log"
FAILED_FILE="exp-results/failed_challenges.txt"
COMPLETED_FILE="exp-results/completed_challenges.txt"
MAX_PARALLEL=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Stats tracking (use temp files for cross-process counting)
STATS_DIR=$(mktemp -d)
echo "0" > "$STATS_DIR/passed"
echo "0" > "$STATS_DIR/failed"
echo "0" > "$STATS_DIR/skipped"
echo "0" > "$STATS_DIR/total"

# Track child PIDs for cleanup
CHILD_PIDS=()

# -------------------------------------------------------------------
# Logging (thread-safe via flock)
# -------------------------------------------------------------------
log() {
    local level=$1
    shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)  echo -e "${BLUE}[$timestamp] [INFO]${NC} $msg" ;;
        OK)    echo -e "${GREEN}[$timestamp] [OK]${NC} $msg" ;;
        WARN)  echo -e "${YELLOW}[$timestamp] [WARN]${NC} $msg" ;;
        ERROR) echo -e "${RED}[$timestamp] [ERROR]${NC} $msg" ;;
    esac

    # Atomic append with flock
    (
        flock -x 200
        echo "[$timestamp] [$level] $msg" >> "$RESULTS_FILE"
    ) 200>>"$RESULTS_FILE.lock"
}

# Thread-safe file append
safe_append() {
    local file=$1
    local content=$2
    (
        flock -x 200
        echo "$content" >> "$file"
    ) 200>>"${file}.lock"
}

# Thread-safe counter increment
increment_stat() {
    local stat_file="$STATS_DIR/$1"
    (
        flock -x 200
        local val=$(cat "$stat_file")
        echo $((val + 1)) > "$stat_file"
    ) 200>>"${stat_file}.lock"
}

# -------------------------------------------------------------------
# Cleanup
# -------------------------------------------------------------------
cleanup() {
    echo -e "\n${YELLOW}Caught interrupt signal. Cleaning up...${NC}"

    # Kill all child processes
    for pid in "${CHILD_PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true

    # Kill all agent containers
    docker ps -q --filter "ancestor=ctfenv:multiagent" | xargs -r docker rm -f 2>/dev/null || true
    docker ps -q --filter "ancestor=ctfenv:kali" | xargs -r docker rm -f 2>/dev/null || true

    echo "--- Experiment interrupted at $(date) ---" >> "$RESULTS_FILE"
    print_summary
    rm -rf "$STATS_DIR"
    exit 130
}

trap cleanup SIGINT SIGTERM

# -------------------------------------------------------------------
# Prerequisites
# -------------------------------------------------------------------
check_prereqs() {
    log INFO "Checking prerequisites..."

    if [[ ! -f "$KEYS" ]]; then
        log ERROR "Keys file not found: $KEYS"
        exit 1
    fi

    if [[ ! -f "$CONFIG" ]]; then
        log ERROR "Config file not found: $CONFIG"
        exit 1
    fi

    if ! command -v uv &> /dev/null; then
        log ERROR "uv command not found. Please install uv."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        log ERROR "Docker is not running. Please start Docker."
        exit 1
    fi

    log OK "All prerequisites satisfied"
}

# -------------------------------------------------------------------
# Challenge classification
# -------------------------------------------------------------------
get_challenges() {
    uv run python3 -c "
from nyuctf.dataset import CTFDataset
d = CTFDataset(split='$SPLIT')
for c in sorted(d.dataset.keys()):
    print(c)
" 2>/dev/null
}

# Classify challenges as 'server' or 'noserver'
# A challenge is 'server' if it has a compose field in challenge.json
classify_challenges() {
    uv run python3 -c "
from nyuctf.dataset import CTFDataset
from nyuctf.challenge import CTFChallenge
d = CTFDataset(split='$SPLIT')
for name in sorted(d.dataset.keys()):
    chal = CTFChallenge(d.get(name), d.basedir)
    kind = 'server' if chal.container else 'noserver'
    print(f'{kind} {name}')
" 2>/dev/null
}

# -------------------------------------------------------------------
# Docker cleanup (per challenge)
# -------------------------------------------------------------------
cleanup_challenge_docker() {
    local challenge=$1
    local pre_containers=$2

    local post_containers
    post_containers=$(docker ps -q | sort)
    local new_containers
    new_containers=$(comm -23 <(echo "$post_containers") <(echo "$pre_containers"))

    if [[ -n "$new_containers" ]]; then
        log WARN "Cleaning up leftover containers from $challenge"
        echo "$new_containers" | xargs -r docker rm -f 2>/dev/null || true
    fi
}

# -------------------------------------------------------------------
# Run a single challenge
# -------------------------------------------------------------------
run_challenge() {
    local challenge=$1
    local idx=$2
    local total=$3

    log INFO "[$idx/$total] Starting challenge: $challenge"

    # Check if already completed
    if grep -q "^$challenge$" "$COMPLETED_FILE" 2>/dev/null; then
        log WARN "[$idx/$total] Skipping $challenge (already completed)"
        increment_stat "skipped"
        return 0
    fi

    # Check if already failed (skip on resume instead of re-running)
    if grep -q "^${challenge}:" "$FAILED_FILE" 2>/dev/null; then
        log WARN "[$idx/$total] Skipping $challenge (previously failed)"
        increment_stat "skipped"
        return 0
    fi

    # Snapshot containers
    local pre_containers
    pre_containers=$(docker ps -q | sort)

    local start_time=$(date +%s)
    local exit_code=0

    if timeout 600 uv run run_dcipher.py \
        --logdir "$LOG_DIR" \
        --config "$CONFIG" \
        --split "$SPLIT" \
        --challenge "$challenge" \
        --keys "$KEYS" \
        >> "${LOG_DIR}/batch_${challenge}.log" 2>&1; then
        exit_code=0
    else
        exit_code=$?
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [[ $exit_code -eq 0 ]]; then
        log OK "[$idx/$total] Completed: $challenge (${duration}s)"
        safe_append "$COMPLETED_FILE" "$challenge"
        increment_stat "passed"
    elif [[ $exit_code -eq 124 ]]; then
        log ERROR "[$idx/$total] Timeout: $challenge (exceeded 30 min)"
        safe_append "$FAILED_FILE" "$challenge:TIMEOUT"
        increment_stat "failed"
    else
        log ERROR "[$idx/$total] Failed: $challenge (exit code: $exit_code, ${duration}s)"
        safe_append "$FAILED_FILE" "$challenge:EXIT_$exit_code"
        increment_stat "failed"
    fi

    # Cleanup Docker containers
    cleanup_challenge_docker "$challenge" "$pre_containers"

    return 0
}

# -------------------------------------------------------------------
# Semaphore: limit concurrent background jobs
# -------------------------------------------------------------------
wait_for_slot() {
    # Wait until fewer than MAX_PARALLEL jobs are running
    while true; do
        local running=0
        local new_pids=()
        for pid in "${CHILD_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                ((running++)) || true
                new_pids+=("$pid")
            fi
        done
        CHILD_PIDS=("${new_pids[@]+"${new_pids[@]}"}")

        if [[ $running -lt $MAX_PARALLEL ]]; then
            break
        fi
        sleep 2
    done
}

# -------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------
print_summary() {
    local passed=$(cat "$STATS_DIR/passed")
    local failed=$(cat "$STATS_DIR/failed")
    local skipped=$(cat "$STATS_DIR/skipped")
    local total=$(cat "$STATS_DIR/total")
    local run=$((total - skipped))

    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║             PARALLEL EXPERIMENT SUMMARY                      ║${NC}"
    echo -e "${BLUE}╠═══════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${BLUE}║${NC} Config:      $CONFIG"
    echo -e "${BLUE}║${NC} Split:       $SPLIT"
    echo -e "${BLUE}║${NC} Parallelism: $MAX_PARALLEL"
    echo -e "${BLUE}║${NC} Total:       $total challenges"
    echo -e "${BLUE}║${NC} Passed:      ${GREEN}$passed${NC}"
    echo -e "${BLUE}║${NC} Failed:      ${RED}$failed${NC}"
    echo -e "${BLUE}║${NC} Skipped:     ${YELLOW}$skipped${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
}

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
main() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     RQ1+RQ2 Experiment: Ubuntu + Tips (PARALLEL)             ║${NC}"
    echo -e "${BLUE}║     Max parallel: $MAX_PARALLEL                                           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    echo "=== Experiment started at $(date) ===" >> "$RESULTS_FILE"
    echo "Config: $CONFIG | Parallelism: $MAX_PARALLEL" >> "$RESULTS_FILE"
    touch "$COMPLETED_FILE" "$FAILED_FILE"
    check_prereqs
    mkdir -p "$LOG_DIR"

    # Classify all challenges
    log INFO "Classifying challenges (server vs non-server)..."
    local classified
    classified=$(classify_challenges)

    local noserver_challenges=()
    local server_challenges=()

    while IFS=' ' read -r kind name; do
        if [[ "$kind" == "server" ]]; then
            server_challenges+=("$name")
        else
            noserver_challenges+=("$name")
        fi
    done <<< "$classified"

    local total_noserver=${#noserver_challenges[@]}
    local total_server=${#server_challenges[@]}
    local total=$((total_noserver + total_server))
    echo "$total" > "$STATS_DIR/total"

    log INFO "Found $total challenges: $total_noserver non-server (parallel), $total_server server (sequential)"

    # ---------------------------------------------------------------
    # Phase 1: Non-server challenges in parallel
    # ---------------------------------------------------------------
    log INFO "=== Phase 1: Running $total_noserver non-server challenges (parallel, max $MAX_PARALLEL) ==="

    local idx=0
    for challenge in "${noserver_challenges[@]}"; do
        idx=$((idx + 1))

        # Wait for a free slot
        wait_for_slot

        # Launch in background
        run_challenge "$challenge" "$idx" "$total" &
        CHILD_PIDS+=($!)

        # Small stagger to avoid thundering herd on API
        sleep 1
    done

    # Wait for all parallel jobs to finish
    log INFO "Waiting for remaining parallel jobs to complete..."
    for pid in "${CHILD_PIDS[@]}"; do
        wait "$pid" 2>/dev/null || true
    done
    CHILD_PIDS=()

    log OK "Phase 1 complete: all non-server challenges finished"

    # ---------------------------------------------------------------
    # Phase 2: Server challenges sequentially
    # ---------------------------------------------------------------
    log INFO "=== Phase 2: Running $total_server server challenges (sequential) ==="

    for challenge in "${server_challenges[@]}"; do
        idx=$((idx + 1))
        run_challenge "$challenge" "$idx" "$total"
        sleep 2
    done

    log OK "Phase 2 complete: all server challenges finished"

    # Summary
    echo "=== Experiment completed at $(date) ===" >> "$RESULTS_FILE"
    print_summary

    local passed=$(cat "$STATS_DIR/passed")
    local failed=$(cat "$STATS_DIR/failed")
    local skipped=$(cat "$STATS_DIR/skipped")
    echo "STATS: Total=$total Passed=$passed Failed=$failed Skipped=$skipped Parallel=$MAX_PARALLEL" >> "$RESULTS_FILE"

    # Cleanup temp dir
    rm -rf "$STATS_DIR"
}

# -------------------------------------------------------------------
# Argument parsing
# -------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --parallel)
            MAX_PARALLEL="$2"
            shift 2
            ;;
        --resume)
            log INFO "Resuming from previous run..."
            shift
            ;;
        --clean)
            log INFO "Starting fresh (removing previous progress)..."
            rm -f "$COMPLETED_FILE" "$FAILED_FILE"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--parallel N] [--resume|--clean|--help]"
            echo ""
            echo "Options:"
            echo "  --parallel N  Max concurrent non-server challenges (default: 3)"
            echo "  --resume      Resume from previous run (skip completed challenges)"
            echo "  --clean       Start fresh (remove previous progress files)"
            echo "  --help        Show this help message"
            echo ""
            echo "How it works:"
            echo "  Phase 1: Non-server challenges run in parallel (up to N at a time)"
            echo "  Phase 2: Server challenges run sequentially (to avoid port conflicts)"
            echo ""
            echo "Output files:"
            echo "  $RESULTS_FILE      - Main experiment log"
            echo "  $COMPLETED_FILE    - List of completed challenges"
            echo "  $FAILED_FILE       - List of failed challenges with error codes"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

main

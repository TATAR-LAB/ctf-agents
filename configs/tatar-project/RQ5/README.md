# RQ5: Reproducibility — How consistent are LLM CTF solvers?

## Hypothesis
H5.1: Running the same challenge with identical configuration multiple times will 
yield different success outcomes due to LLM non-determinism.

## Experiment Design

Run the same configuration **5 times** on each challenge to measure variance.

## Configuration
- Temperature: 1.0 (D-CIPHER paper found optimal)
- Model: Gemini 3 Pro (or best performer from RQ3)
- Uses dcipher prompts

## Metrics
- Success rate variance across runs
- Standard deviation of rounds used
- Confidence intervals

## Usage

```bash
# Run 5 times on same challenge
for i in {1..5}; do
  uv run run_dcipher.py --config configs/tatar-project/RQ5/reproducibility_gemini3_pro.yaml \
    --challenge "2016q-for-kill" \
    --keys ./keys.cfg \
    --logfile "logs/rq5_run_${i}.json"
done
```

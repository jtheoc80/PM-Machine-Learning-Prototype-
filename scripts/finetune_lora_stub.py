import os
from pathlib import Path

"""
This is a stub script for LoRA fine-tuning on a domain Q/A dataset.
It expects a JSONL with fields: instruction, input, output.
Integrate with libraries like axolotl/litgpt/trl later as needed.
"""

def main():
    dataset = os.getenv("DATASET", "/workspace/data/qna.jsonl")
    model = os.getenv("BASE_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    out_dir = Path(os.getenv("OUT_DIR", "/workspace/data/lora"))
    out_dir.mkdir(parents=True, exist_ok=True)
    print("[stub] Would fine-tune", model, "on", dataset, "and save to", out_dir)

if __name__ == "__main__":
    main()

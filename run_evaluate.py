import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.evaluator import Evaluator

def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate LLM responses using LLM-as-a-Judge")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--judge_api_key", type=str, default=None)
    parser.add_argument("--judge_base_url", type=str, default=None)
    parser.add_argument("--judge_model", type=str, default="gpt-4o-mini")

    return parser.parse_args()

def main():
    args = parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    judge_api_key = args.judge_api_key or os.environ.get("JUDGE_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
    judge_base_url = args.judge_base_url or os.environ.get("JUDGE_BASE_URL", os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))

    if not judge_api_key:
        print("Error: No judge API key provided.")
        sys.exit(1)

    evaluator = Evaluator(
        api_key=judge_api_key,
        base_url=judge_base_url,
        model=args.judge_model
    )

    if args.output:
        output_file = args.output
    else:
        base, ext = os.path.splitext(args.input)
        output_file = f"{base}_eval{ext}"

    metrics = evaluator.evaluate_file(args.input, output_file)

    print(f"\nEvaluation Results:")
    print(f"ASR (Attack Success Rate): {metrics['asr']:.2%}")
    print(f"HPR (Helpful Response Rate): {metrics['hpr']:.2%}")
    print(f"HS  (Harmfulness Score): {metrics['hs']:.2f}")

if __name__ == "__main__":
    main()

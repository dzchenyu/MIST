import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.jailbreak_generator import JailbreakGenerator
from src.api_client import LLMClient
from src.evaluator import Evaluator

DATASET_MAP = {
    "advbench": "data/advbench.json",
    "harmbench": "data/harmbench_prompts.json",
    "jailbreakbench": "data/jailbreak-bench.json",
    "behavior200": "data/behavior200.json",
    "defense": "data/defense.json",
}

def parse_args():
    parser = argparse.ArgumentParser(description="Jailbreak Attack Pipeline")
    parser.add_argument("--data_name", type=str, required=True, choices=list(DATASET_MAP.keys()))
    parser.add_argument("--victim_model", type=str, default="gpt-4o")
    parser.add_argument("--begin", type=int, default=0)
    parser.add_argument("--end", type=int, default=-1)
    parser.add_argument("--safe_words_count", type=int, default=1)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--eval", action="store_true")
    
    # API configuration
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument("--judge_api_key", type=str, default=None)
    parser.add_argument("--judge_base_url", type=str, default=None)
    parser.add_argument("--judge_model", type=str, default="gpt-4o-mini")

    return parser.parse_args()

def main():
    args = parse_args()
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Load behaviors
    data_file = os.path.join(base_dir, DATASET_MAP[args.data_name])
    if not os.path.exists(data_file):
        print(f"Error: File not found: {data_file}")
        sys.exit(1)

    with open(data_file, 'r', encoding='utf-8') as f:
        all_behaviors = json.load(f)

    end_idx = args.end if args.end > 0 else len(all_behaviors)
    behaviors = all_behaviors[args.begin:end_idx]

    # Initialize MIST generator
    generator = JailbreakGenerator(
        safe_words_count=args.safe_words_count
    )

    # Generate prompts
    prompts = []
    for behavior in behaviors:
        generator._prepare_dynamic_delimiters()
        obfuscated = generator.process_sentence_with_moderation(behavior)
        prompt = generator.generate_prompt(obfuscated)
        prompts.append({
            "original": behavior,
            "jailbreak_prompt": prompt
        })

    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    prompts_file = os.path.join(results_dir, f"{args.data_name}_{args.victim_model}_prompts.json")
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, indent=4, ensure_ascii=False)

    # Call victim model
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    base_url = args.base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if not api_key:
        print("Warning: No API key provided. Skipping LLM generation step.")
        return

    client = LLMClient(api_key=api_key, base_url=base_url, model=args.victim_model)
    output_file = args.output or os.path.join(results_dir, f"{args.data_name}_{args.victim_model}_responses.json")
    client.process_prompts_file(prompts_file, output_file)

    # Evaluation
    if args.eval:
        judge_api_key = args.judge_api_key or os.environ.get("JUDGE_API_KEY", api_key)
        judge_base_url = args.judge_base_url or os.environ.get("JUDGE_BASE_URL", base_url)

        evaluator = Evaluator(
            api_key=judge_api_key,
            base_url=judge_base_url,
            model=args.judge_model
        )

        eval_output = os.path.join(results_dir, f"{args.data_name}_{args.victim_model}_eval.json")
        metrics = evaluator.evaluate_file(output_file, eval_output)

        print(f"\nEvaluation Results ({args.victim_model} on {args.data_name}):")
        print(f"ASR: {metrics['asr']:.2%} | HPR: {metrics['hpr']:.2%} | HS: {metrics['hs']:.2f}")

if __name__ == "__main__":
    main()

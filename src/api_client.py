import json
import os
import openai
from tqdm import tqdm
import time

# ============================================================
# API Configuration — Set via environment variables or arguments
# ============================================================
# Attack model (target LLM)
DEFAULT_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEFAULT_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_MODEL = os.environ.get("ATTACK_MODEL", "gpt-4o")

# Judge model (LLM-as-a-Judge for evaluation)
DEFAULT_JUDGE_API_KEY = os.environ.get("JUDGE_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
DEFAULT_JUDGE_BASE_URL = os.environ.get("JUDGE_BASE_URL", os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
DEFAULT_JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gpt-4o-mini")


class LLMClient:
    def __init__(self, api_key: str = DEFAULT_API_KEY, base_url: str = DEFAULT_BASE_URL, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=30.0)

    def get_response(self, prompt: str, stop_event=None) -> str:
        """Send a single prompt to the target LLM and get a response. Retries up to 3 times on failure."""
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            if stop_event and stop_event.is_set():
                print("Request aborted by stop_event.")
                return "I'm sorry, operation stopped."

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                if content and content.strip():
                    return content.strip()
                print("Warning: Received empty response from API. Retrying...")
            except Exception as e:
                print(f"Error calling API: {e}. Retrying ({attempts + 1}/{max_retries})...")

            if stop_event and stop_event.is_set():
                print("Request aborted by stop_event during retry.")
                return "I'm sorry, operation stopped."

            attempts += 1
            time.sleep(1)

        print("Failed to get response after 3 attempts. Returning default refusal so evaluation skips it.")
        return "I'm sorry, I cannot answer that."

    def process_prompts_file(self, input_file: str, output_file: str, progress_callback=None, stop_event=None, evaluator=None):
        """
        Process a JSON file containing jailbreak prompts and save LLM responses.
        Supports progress callback and stop event for graceful termination.
        """
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} not found.")
            return

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            results = []
            total = len(data)
            print(f"Sending {total} prompts to LLM ({self.model})...")

            processed_count = 0
            for item in tqdm(data, desc="Processing LLM Requests"):
                if stop_event and stop_event.is_set():
                    print("Process stopped by user.")
                    break

                prompt = item.get("jailbreak_prompt", "")
                if not prompt:
                    processed_count += 1
                    if progress_callback:
                        progress_callback(processed_count, total)
                    continue

                original_prompt = item.get("original", "")
                
                response = self.get_response(prompt, stop_event=stop_event)

                result_item = {
                    "original": original_prompt,
                    "jailbreak_prompt": prompt,
                    "llm_response": response
                }
                results.append(result_item)

                processed_count += 1
                if progress_callback:
                    progress_callback(processed_count, total)

            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            if stop_event and stop_event.is_set():
                print(f"Saved partial LLM responses to {output_file}")
            else:
                print(f"Saved LLM responses to {output_file}")

        except Exception as e:
            print(f"Error processing prompts file: {e}")
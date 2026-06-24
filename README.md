<div align="center">
<h2>MIST: Malicious In-Distribution Stealth Attack on LLMs via Benign Interspersion</h2>

Yuxiang Chen, Zekai He, Haibo Hong

*Affiliations TBD*

</div>

<p align="center">
  <a href="#" alt="Paper"> <img src="https://img.shields.io/badge/Paper-Coming_Soon-blue" /> </a>
</p>

<p align="justify">
Jailbreak attacks pose a critical threat to Large Language Models (LLMs), prompting various defense mechanisms, where input-side approaches such as keyword filtering and intent classification intercept malicious queries before generation. Despite their diversity, these defenses share a common assumption: adversarial prompts inevitably introduce anomalies in natural language statistical characteristics that distinguish them from benign inputs. However, this assumption has not been examined against perturbations that are structurally adversarial yet distributionally indistinguishable from natural text. 

In this paper, we observe a phenomenon termed <b>In-Distribution Stealth</b>: inserting high-frequency benign words (e.g., common English words) between individual characters of a malicious term yields prompts whose perplexity is even lower than that of unmodified harmful queries, indicating that the perturbed text conforms more closely to natural language statistics than the original malicious input. 

Building on this insight, we propose <b>MIST</b>, a single-turn black-box jailbreak framework integrating two complementary components. <b>Benign Interspersion</b> exploits this distributional blind spot by scattering common words between each character of the harmful payload, producing a low-perplexity sequence that can bypass input-side safety detection with higher probability. The <b>MIST Template</b> circumvents the model's safety alignment through three structured modules, <i>Rules</i>, <i>Tasks</i>, and <i>Format</i>, which respectively suppress safety reminders, instruct the model to recover the original query, and elicit step-by-step responses. We evaluate MIST on frontier LLMs, achieving a state-of-the-art average Attack Success Rate (ASR), outperforming representative single-turn and multi-turn baselines while incurring lower token overhead.
</p>

<br>

<p align="center">
  <img src="./assets/flow.png" alt="MIST Framework Overview" style="zoom:100%;" />
  <br>
  <i>Figure 1: Overview of the MIST jailbreak framework, showcasing the benign interspersion and structural template execution.</i>
</p>


## Datasets

The `data/` directory contains five evaluation datasets. You can specify which one to use via the `--data_name` parameter during execution:

| Dataset Parameter | File Path | Description |
|------------------|-----------|-------------|
| `advbench` | `data/advbench.json` | AdvBench behaviors |
| `harmbench` | `data/harmbench_prompts.json` | HarmBench behaviors |
| `jailbreakbench` | `data/jailbreak-bench.json` | JailbreakBench behaviors |
| `behavior200` | `data/behavior200.json` | Our curated benchmark Behavior-200 |
| `defense` | `data/defense.json`| Subset used for defense evaluation experiments |

## Usage

### Quick Start

To evaluate MIST, run the following commands. We provide Python command-line interfaces for both attack generation and evaluation.

1. **Install the environment**
    Ensure you install all the necessary requirements for the full pipeline:
    ```bash
    pip install -r requirements.txt
    ```

2. **Set up API keys**
    Obtain the API keys from your preferred providers (e.g., OpenAI, Anthropic, or DeepInfra).
    ```bash
    # For target models and LLM Judge
    export OPENAI_API_KEY="your_api_key"
    export OPENAI_BASE_URL="https://api.openai.com/v1"
    
    # Alternatively, you can specify them when running the scripts
    ```

3. **Run MIST Attack**
    Use `run_attack.py` to generate jailbreak prompts and send them to the victim model.
    ```bash
    # Run attack on GPT-4o using AdvBench subset (first 50 behaviors)
    python run_attack.py --data_name advbench --victim_model gpt-4o --begin 0 --end 50
    
    # Run attack on GPT-5.1 using HarmBench
    python run_attack.py --data_name harmbench --victim_model gpt-5.1
    
    # Run full pipeline: attack + evaluation
    python run_attack.py --data_name advbench --victim_model gpt-4o --eval
    ```

4. **Evaluate Results (LLM-as-a-Judge)**
    Use `run_evaluate.py` to independently evaluate the responses generated from the attacks. By default, it uses `gpt-4o-mini` as the judge model.
    ```bash
    python run_evaluate.py --input results/advbench_gpt-4o_responses.json
    ```

## Main Results

The evaluation metrics include Attack Success Rate (ASR), Helpful Rate (HPR), and Harmfulness Score (HS).

We first conduct comprehensive evaluations across three full-scale benchmark datasets (AdvBench, HarmBench, and JailbreakBench) to verify the generalizability of MIST. The results are shown below:

<p align="center">
  <img src="./assets/table1.png" alt="Results on three full-scale datasets" style="zoom:100%;" />
</p>

The following table presents a detailed baseline comparison experiment conducted on our custom evaluation dataset, **Behavior-200**, which harmonizes diverse hazard categories to ensure a strict and fair head-to-head comparison with state-of-the-art baselines.

<p align="center">
  <img src="./assets/table2.png" alt="Baseline comparison on Behavior-200" style="zoom:100%;" />
</p>


## Repository Structure
```bash
MIST/
├── data/                  # Benchmark datasets (AdvBench, HarmBench, JailbreakBench, behavior200, defense)
├── bengin_words/          # Curated benign word dictionaries for Inner-Token Mimicry
├── shiyan/                # Historical experimental results
├── assets/                # Figures and tables (flow.png, table1.png, table2.png)
├── src/                   # Core source code
│   ├── jailbreak_generator.py # ITM and OTM implementation
│   ├── api_client.py      # LLM API interaction
│   └── evaluator.py       # LLM-as-a-Judge evaluation logic
├── run_attack.py          # CLI for running attacks
└── run_evaluate.py        # CLI for evaluating results
```

## Citations
*Paper coming soon.*

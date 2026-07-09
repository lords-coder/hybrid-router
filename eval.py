#!/usr/bin/env python3
"""
Local evaluation script for the Hybrid Token-Efficient Routing Agent.
Tests all 8 capability categories with practice tasks.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from router.engine import RoutingEngine
from router.fireworks_client import llm_client
from config.models import ALL_FIREWORKS_MODELS, LOCAL_MODELS
from config.settings import settings


PRACTICE_TASKS = [
    {
        "task_id": "t1",
        "category": "factual_knowledge",
        "prompt": "What is the capital of Australia, and what state is it in?",
        "expected_keywords": ["canberra", "australian capital territory", "act"],
    },
    {
        "task_id": "t2",
        "category": "math_reasoning",
        "prompt": "A store has 150 apples. They sell 35% on Monday and 20 on Tuesday. How many remain?",
        "expected_keywords": ["67", "67.5", "68"],
    },
    {
        "task_id": "t3",
        "category": "text_summarization",
        "prompt": "Summarize the following text in exactly one sentence: Lithium-ion batteries are rechargeable batteries that use lithium ions as the primary component of their electrochemistry. These batteries are commonly used in portable electronics and electric vehicles. They have a high energy density, no memory effect, and only a slow loss of charge when not in use.",
        "expected_keywords": ["lithium-ion", "batteries", "rechargeable"],
    },
    {
        "task_id": "t4",
        "category": "named_entity_recognition",
        "prompt": "Extract all named entities and their types from this text: Maria Santos joined Fireworks AI in Berlin last March. She previously worked at Google DeepMind in London. Her colleague Dr. James Chen will present at NeurIPS in New Orleans this December.",
        "expected_keywords": ["maria santos", "fireworks ai", "berlin", "google deepmind", "london", "james chen", "neurips", "new orleans"],
    },
    {
        "task_id": "t5",
        "category": "text_summarization",
        "prompt": "Summarize in one sentence: Three friends—Alice, Bob, and Lee—each ordered a different drink: coffee, tea, or juice. Alice didn't order coffee. Bob ordered tea. What did Lee order?",
        "expected_keywords": ["alice", "bob", "lee", "coffee", "tea", "juice"],
    },
    {
        "task_id": "t6",
        "category": "code_generation",
        "prompt": "Write a Python function that returns the second-largest number in a list, handling duplicates correctly.",
        "expected_keywords": ["def", "return", "sorted", "second"],
    },
    {
        "task_id": "t7",
        "category": "logical_reasoning",
        "prompt": "If all roses are flowers, and some flowers fade quickly, can we conclude that some roses fade quickly?",
        "expected_keywords": ["cannot conclude", "not necessarily", "invalid"],
    },
    {
        "task_id": "t8",
        "category": "sentiment_classification",
        "prompt": "Classify the sentiment: 'The product arrived late, the packaging was damaged, and customer support was unhelpful. I am very disappointed.'",
        "expected_keywords": ["negative"],
    },
]


def evaluate_answer(answer: str, expected_keywords: list) -> float:
    answer_lower = answer.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return matches / max(len(expected_keywords), 1)


def run_eval():
    print("=" * 70)
    print("HYBRID TOKEN-EFFICIENT ROUTING AGENT - LOCAL EVALUATION")
    print("=" * 70)

    engine = RoutingEngine()
    results = []

    total_fireworks_tokens = 0
    total_local_tokens = 0
    total_accuracy = 0

    for task in PRACTICE_TASKS:
        print(f"\n{'=' * 60}")
        print(f"Task {task['task_id']}: {task['category']}")
        print(f"Prompt: {task['prompt'][:100]}...")

        analysis = engine.route(task["prompt"])
        model_data = analysis["selected_model"]

        selected_model = None
        for m in ALL_FIREWORKS_MODELS + LOCAL_MODELS:
            if m.name == model_data["name"]:
                selected_model = m
                break
        if not selected_model:
            selected_model = LOCAL_MODELS[0]

        print(f"  Router: {selected_model.display_name} ({selected_model.provider.value})")
        print(f"  Local: {analysis['is_local']}")
        print(f"  Reason: {analysis['selection_reason'][:100]}...")

        api_result = llm_client.chat_completion(
            model=selected_model,
            prompt=analysis["optimized_prompt"],
            system_prompt=analysis["system_prompt"],
            temperature=0.3,
            max_tokens=512,
        )

        if not api_result["success"]:
            print(f"  FAILED: {api_result.get('error', 'unknown')}")
            api_result = llm_client.try_fallback(
                selected_model,
                analysis["optimized_prompt"],
                analysis["system_prompt"],
                0.3, 512,
            )

        answer = api_result.get("content", "") if api_result.get("success") else ""
        accuracy = evaluate_answer(answer, task["expected_keywords"])

        fw_tokens = api_result.get("fireworks_tokens", 0)
        local_tok = api_result.get("total_tokens", 0) - fw_tokens if not analysis["is_local"] else api_result.get("total_tokens", 0)

        total_fireworks_tokens += fw_tokens
        total_local_tokens += local_tok
        total_accuracy += accuracy

        results.append({
            "task_id": task["task_id"],
            "category": task["category"],
            "model": selected_model.display_name,
            "provider": selected_model.provider.value,
            "is_local": analysis["is_local"],
            "fireworks_tokens": fw_tokens,
            "accuracy": round(accuracy, 2),
            "answer_preview": answer[:100],
        })

        print(f"  Answer: {answer[:150]}...")
        print(f"  Accuracy: {accuracy:.0%}")
        print(f"  Fireworks tokens: {fw_tokens}")

    print(f"\n{'=' * 70}")
    print("EVALUATION SUMMARY")
    print(f"{'=' * 70}")
    print(f"Total tasks: {len(PRACTICE_TASKS)}")
    print(f"Average accuracy: {total_accuracy / len(PRACTICE_TASKS):.0%}")
    print(f"Total Fireworks tokens: {total_fireworks_tokens}")
    print(f"Total local tokens: {total_local_tokens}")
    print(f"Local task ratio: {sum(1 for r in results if r['is_local'])}/{len(results)}")

    print(f"\nPer-task breakdown:")
    for r in results:
        status = "LOCAL" if r["is_local"] else "FW"
        print(f"  {r['task_id']}: [{status}] {r['model']:<30} acc={r['accuracy']:.0%}  tokens={r['fireworks_tokens']}")

    print(f"\nScoring simulation:")
    print(f"  Fireworks tokens (lower is better): {total_fireworks_tokens}")
    print(f"  Accuracy (higher is better): {total_accuracy / len(PRACTICE_TASKS):.0%}")

    output_path = os.path.join(os.path.dirname(__file__), "eval_results.json")
    with open(output_path, "w") as f:
        json.dump({
            "total_tasks": len(PRACTICE_TASKS),
            "avg_accuracy": round(total_accuracy / len(PRACTICE_TASKS), 2),
            "total_fireworks_tokens": total_fireworks_tokens,
            "total_local_tokens": total_local_tokens,
            "local_ratio": sum(1 for r in results if r["is_local"]) / len(results),
            "results": results,
        }, f, indent=2)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    run_eval()

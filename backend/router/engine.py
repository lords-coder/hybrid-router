import re
import time
from config.models import (
    TaskCategory, ComplexityLevel, ModelInfo, ModelProvider,
    ALL_FIREWORKS_MODELS, LOCAL_MODELS,
    COMPLEXITY_REQUIREMENTS, TASK_KEYWORDS, CATEGORY_TO_SYSTEM_PROMPT,
)
from config.settings import settings
from typing import Tuple, List, Optional


COMPLEXITY_KEYWORDS = {
    ComplexityLevel.TRIVIAL: ["yes or no", "true or false", "hi", "hello", "hey"],
    ComplexityLevel.SIMPLE: ["what is", "who is", "define", "name", "list"],
    ComplexityLevel.MEDIUM: ["explain", "describe", "compare", "why", "how"],
    ComplexityLevel.COMPLEX: ["analyze", "evaluate", "prove", "derive", "multi-step"],
    ComplexityLevel.VERY_COMPLEX: ["prove that", "derive from first principles", "step-by-step proof"],
}


class PromptAnalyzer:
    def classify_task(self, prompt: str) -> TaskCategory:
        prompt_lower = prompt.lower().strip()
        scores = {cat: 0.0 for cat in TaskCategory}

        for cat, keywords in TASK_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt_lower:
                    scores[cat] += 1.0
                    if prompt_lower.startswith(kw):
                        scores[cat] += 0.5

        code_indicators = ["def ", "class ", "import ", "function(", "const ", "let ", "print("]
        code_count = sum(1 for ind in code_indicators if ind in prompt)
        if code_count >= 2:
            scores[TaskCategory.CODE_GENERATION] += 2.0

        math_indicators = ["+", "-", "*", "/", "=", "^", "sqrt", "log"]
        math_count = sum(1 for m in math_indicators if m in prompt)
        if math_count >= 2:
            scores[TaskCategory.MATH_REASONING] += 2.0

        has_percent = "%" in prompt or "percent" in prompt
        has_number = bool(re.search(r'\d+', prompt))
        if has_percent and has_number:
            scores[TaskCategory.MATH_REASONING] += 1.0

        if "one sentence" in prompt_lower or "in a sentence" in prompt_lower:
            scores[TaskCategory.TEXT_SUMMARIZATION] += 3.0

        if "sentiment" in prompt_lower or "positive" in prompt_lower or "negative" in prompt_lower:
            scores[TaskCategory.SENTIMENT_CLASSIFICATION] += 2.0

        if "extract" in prompt_lower and ("named" in prompt_lower or "entit" in prompt_lower):
            scores[TaskCategory.NAMED_ENTITY_RECOGNITION] += 3.0
        if "find all names" in prompt_lower or "list all named" in prompt_lower:
            scores[TaskCategory.NAMED_ENTITY_RECOGNITION] += 3.0

        if ("debug" in prompt_lower or "fix" in prompt_lower or "bug" in prompt_lower or "error" in prompt_lower):
            has_code = any(ind in prompt for ind in code_indicators)
            if has_code:
                scores[TaskCategory.CODE_DEBUGGING] += 3.0

        if "if " in prompt_lower and ("then" in prompt_lower or "must be true" in prompt_lower or "conclude" in prompt_lower):
            scores[TaskCategory.LOGICAL_REASONING] += 2.0

        best = max(scores, key=scores.get)
        if scores[best] < 0.5:
            return TaskCategory.FACTUAL_KNOWLEDGE
        return best

    def estimate_complexity(self, prompt: str) -> ComplexityLevel:
        prompt_lower = prompt.lower().strip()
        words = prompt.split()
        word_count = len(words)

        scores = {level: 0.0 for level in ComplexityLevel}

        for level, keywords in COMPLEXITY_KEYWORDS.items():
            for kw in keywords:
                if kw in prompt_lower:
                    scores[level] += 1.0

        if word_count <= 5:
            scores[ComplexityLevel.TRIVIAL] += 2.0
        elif word_count <= 15:
            scores[ComplexityLevel.SIMPLE] += 1.5
        elif word_count <= 40:
            scores[ComplexityLevel.MEDIUM] += 1.5
        elif word_count <= 80:
            scores[ComplexityLevel.COMPLEX] += 1.5
        else:
            scores[ComplexityLevel.VERY_COMPLEX] += 2.0

        sentences = len(re.split(r'[.!?]+', prompt))
        if sentences > 3:
            scores[ComplexityLevel.COMPLEX] += 1.0
        if sentences > 5:
            scores[ComplexityLevel.VERY_COMPLEX] += 1.0

        nested = len(re.findall(r',\s*(which|that|who|whom|where|when|because|although|while|if)', prompt_lower))
        scores[ComplexityLevel.COMPLEX] += nested * 0.5

        if "?" in prompt:
            scores[ComplexityLevel.SIMPLE] += 0.3

        return max(scores, key=scores.get)

    def estimate_reasoning(self, task: TaskCategory, complexity: ComplexityLevel) -> float:
        base = {
            TaskCategory.FACTUAL_KNOWLEDGE: 0.3,
            TaskCategory.SENTIMENT_CLASSIFICATION: 0.25,
            TaskCategory.TEXT_SUMMARIZATION: 0.4,
            TaskCategory.NAMED_ENTITY_RECOGNITION: 0.3,
            TaskCategory.MATH_REASONING: 0.65,
            TaskCategory.CODE_DEBUGGING: 0.7,
            TaskCategory.LOGICAL_REASONING: 0.8,
            TaskCategory.CODE_GENERATION: 0.7,
        }
        mult = {
            ComplexityLevel.TRIVIAL: 0.3,
            ComplexityLevel.SIMPLE: 0.5,
            ComplexityLevel.MEDIUM: 0.7,
            ComplexityLevel.COMPLEX: 0.9,
            ComplexityLevel.VERY_COMPLEX: 1.0,
        }
        return min(base.get(task, 0.5) * mult.get(complexity, 0.5), 1.0)

    def estimate_tokens(self, prompt: str) -> int:
        return int(len(prompt.split()) * 1.3)


class ModelSelector:
    def get_allowed_models(self) -> List[ModelInfo]:
        if settings.ALLOWED_MODELS:
            return [m for m in ALL_FIREWORKS_MODELS if m.name in settings.ALLOWED_MODELS]
        return ALL_FIREWORKS_MODELS

    def should_use_local(
        self, task: TaskCategory, complexity: ComplexityLevel, reasoning: float
    ) -> bool:
        if not settings.LOCAL_MODEL_ENABLED:
            return False
        if complexity in (ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE):
            if reasoning <= 0.4:
                local = LOCAL_MODELS[0]
                if task.value in local.capabilities:
                    return True
        return False

    def select_model(
        self, task: TaskCategory, complexity: ComplexityLevel, reasoning: float
    ) -> Tuple[ModelInfo, str, bool]:
        if self.should_use_local(task, complexity, reasoning):
            local = LOCAL_MODELS[0]
            return local, (
                f"LOCAL model selected (0 tokens!): {local.display_name} for '{task.value}' "
                f"(complexity: {complexity.value}, reasoning needed: {reasoning:.2f}). "
                f"Local inference = zero Fireworks tokens = best possible score."
            ), True

        allowed = self.get_allowed_models()
        min_reasoning = COMPLEXITY_REQUIREMENTS[complexity.value]
        task_name = task.value

        candidates = []
        for m in allowed:
            if task_name in m.capabilities or reasoning <= m.reasoning_score:
                if m.reasoning_score >= min_reasoning:
                    candidates.append(m)

        if not candidates:
            candidates = [m for m in allowed if m.reasoning_score >= min_reasoning]

        if not candidates:
            candidates = allowed

        gemma_candidates = [m for m in candidates if "gemma" in m.name.lower()]
        non_gemma_candidates = [m for m in candidates if "gemma" not in m.name.lower()]

        if gemma_candidates:
            candidates = gemma_candidates
            if complexity in (ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE):
                candidates.sort(key=lambda m: (m.cost_per_1k_input, -m.reasoning_score))
                reason_prefix = "Gemma Bonus: cheapest Gemma model"
            elif complexity == ComplexityLevel.MEDIUM:
                candidates.sort(key=lambda m: (-m.reasoning_score, m.cost_per_1k_input))
                reason_prefix = "Gemma Bonus: best Gemma model"
            else:
                candidates.sort(key=lambda m: (-m.reasoning_score, m.cost_per_1k_input))
                reason_prefix = "Gemma Bonus: best reasoning Gemma model"
        elif non_gemma_candidates:
            candidates = non_gemma_candidates
            if complexity in (ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE):
                candidates.sort(key=lambda m: (m.cost_per_1k_input, -m.reasoning_score))
                reason_prefix = "Simple task -> cheapest capable model"
            elif complexity == ComplexityLevel.MEDIUM:
                candidates.sort(key=lambda m: (-m.reasoning_score, m.cost_per_1k_input))
                reason_prefix = "Medium task -> best cost/quality model"
            else:
                candidates.sort(key=lambda m: (-m.reasoning_score, m.cost_per_1k_input))
                reason_prefix = "Complex task -> best reasoning model"
        else:
            if complexity in (ComplexityLevel.TRIVIAL, ComplexityLevel.SIMPLE):
                candidates.sort(key=lambda m: (m.cost_per_1k_input, -m.reasoning_score))
                reason_prefix = "Simple task -> cheapest capable model"
            else:
                candidates.sort(key=lambda m: (-m.reasoning_score, m.cost_per_1k_input))
                reason_prefix = "Complex task -> best reasoning model"

        best = candidates[0]
        is_gemma = "gemma" in best.name.lower()
        gemma_note = " [GEMMA BONUS]" if is_gemma else ""

        reason = (
            f"{reason_prefix}: {best.display_name}{gemma_note} for '{task_name}' "
            f"(complexity: {complexity.value}, reasoning: {reasoning:.2f}). "
            f"Tokens routed via FIREWORKS_BASE_URL."
        )
        return best, reason, False


class PromptOptimizer:
    FILLER_WORDS = re.compile(
        r'\b(please|kindly|could you|would you|I want you to|I would like you to|'
        r'can you|I need you to|I was wondering if you could|do me a favor and)\b',
        re.IGNORECASE,
    )
    REDUNDANT_SPACES = re.compile(r'\s+')

    def compress(self, prompt: str) -> Tuple[str, dict]:
        original_tokens = int(len(prompt.split()) * 1.3)
        optimized = self.FILLER_WORDS.sub('', prompt)
        optimized = self.REDUNDANT_SPACES.sub(' ', optimized).strip()
        optimized_tokens = int(len(optimized.split()) * 1.3)
        saved = original_tokens - optimized_tokens

        return optimized, {
            "original_tokens": original_tokens,
            "optimized_tokens": optimized_tokens,
            "tokens_saved": max(saved, 0),
            "compression_ratio": round(optimized_tokens / max(original_tokens, 1), 2),
        }

    def get_system_prompt(self, task: TaskCategory) -> str:
        return CATEGORY_TO_SYSTEM_PROMPT.get(
            task.value,
            "You are a helpful assistant. Answer accurately and concisely.",
        )


class RoutingEngine:
    def __init__(self):
        self.analyzer = PromptAnalyzer()
        self.selector = ModelSelector()
        self.optimizer = PromptOptimizer()

    def route(self, prompt: str) -> dict:
        start = time.time()

        task = self.analyzer.classify_task(prompt)
        complexity = self.analyzer.estimate_complexity(prompt)
        reasoning = self.analyzer.estimate_reasoning(task, complexity)
        input_tokens = self.analyzer.estimate_tokens(prompt)

        optimized, opt_info = self.optimizer.compress(prompt)
        system_prompt = self.optimizer.get_system_prompt(task)

        model, selection_reason, is_local = self.selector.select_model(
            task, complexity, reasoning
        )

        return {
            "task_type": task.value,
            "complexity": complexity.value,
            "reasoning_level": round(reasoning, 2),
            "selected_model": {
                "name": model.name,
                "display_name": model.display_name,
                "provider": model.provider.value,
                "reasoning_score": model.reasoning_score,
                "context_length": model.context_length,
                "max_output_tokens": model.max_output_tokens,
                "cost_per_1k_input": model.cost_per_1k_input,
                "cost_per_1k_output": model.cost_per_1k_output,
            },
            "is_local": is_local,
            "selection_reason": selection_reason,
            "estimated_tokens": {
                "input": input_tokens,
                "output": min(input_tokens * 2, model.max_output_tokens),
                "total": input_tokens + min(input_tokens * 2, model.max_output_tokens),
            },
            "optimization": opt_info,
            "system_prompt": system_prompt,
            "optimized_prompt": optimized,
            "confidence": round(min(reasoning + 0.25, 1.0), 2),
        }

from enum import Enum
from typing import List, Dict
from pydantic import BaseModel


class TaskCategory(str, Enum):
    FACTUAL_KNOWLEDGE = "factual_knowledge"
    MATH_REASONING = "math_reasoning"
    SENTIMENT_CLASSIFICATION = "sentiment_classification"
    TEXT_SUMMARIZATION = "text_summarization"
    NAMED_ENTITY_RECOGNITION = "named_entity_recognition"
    CODE_DEBUGGING = "code_debugging"
    LOGICAL_REASONING = "logical_reasoning"
    CODE_GENERATION = "code_generation"


class ComplexityLevel(str, Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class ModelProvider(str, Enum):
    FIREWORKS = "fireworks"
    LOCAL = "local"


class ModelInfo(BaseModel):
    name: str
    display_name: str
    provider: ModelProvider
    capabilities: List[str]
    reasoning_score: float
    context_length: int
    max_output_tokens: int
    cost_per_1k_input: float
    cost_per_1k_output: float
    speed_tier: int


ALL_FIREWORKS_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="accounts/fireworks/models/minimax-m3",
        display_name="MiniMax M3",
        provider=ModelProvider.FIREWORKS,
        capabilities=[
            "factual_knowledge", "math_reasoning", "sentiment_classification",
            "text_summarization", "named_entity_recognition", "code_debugging",
            "logical_reasoning", "code_generation",
        ],
        reasoning_score=0.75,
        context_length=512000,
        max_output_tokens=8192,
        cost_per_1k_input=0.0003,
        cost_per_1k_output=0.0012,
        speed_tier=1,
    ),
    ModelInfo(
        name="accounts/fireworks/models/kimi-k2p7-code",
        display_name="Kimi K2.7 Code",
        provider=ModelProvider.FIREWORKS,
        capabilities=[
            "code_generation", "code_debugging", "math_reasoning",
            "logical_reasoning", "factual_knowledge", "text_summarization",
        ],
        reasoning_score=0.85,
        context_length=262144,
        max_output_tokens=8192,
        cost_per_1k_input=0.00095,
        cost_per_1k_output=0.004,
        speed_tier=2,
    ),
    ModelInfo(
        name="accounts/fireworks/models/gemma-4-31b-it",
        display_name="Gemma 4 31B IT (Gemma Bonus)",
        provider=ModelProvider.FIREWORKS,
        capabilities=[
            "factual_knowledge", "math_reasoning", "sentiment_classification",
            "text_summarization", "named_entity_recognition", "code_debugging",
            "logical_reasoning", "code_generation",
        ],
        reasoning_score=0.80,
        context_length=262144,
        max_output_tokens=8192,
        cost_per_1k_input=0.0003,
        cost_per_1k_output=0.0012,
        speed_tier=1,
    ),
    ModelInfo(
        name="accounts/fireworks/models/gemma-4-26b-a4b-it",
        display_name="Gemma 4 26B A4B IT (Gemma Bonus)",
        provider=ModelProvider.FIREWORKS,
        capabilities=[
            "factual_knowledge", "math_reasoning", "sentiment_classification",
            "text_summarization", "named_entity_recognition", "code_debugging",
            "logical_reasoning", "code_generation",
        ],
        reasoning_score=0.75,
        context_length=262144,
        max_output_tokens=8192,
        cost_per_1k_input=0.0003,
        cost_per_1k_output=0.0012,
        speed_tier=1,
    ),
    ModelInfo(
        name="accounts/fireworks/models/gemma-4-31b-it-nvfp4",
        display_name="Gemma 4 31B IT NVFP4 (Gemma Bonus)",
        provider=ModelProvider.FIREWORKS,
        capabilities=[
            "factual_knowledge", "math_reasoning", "sentiment_classification",
            "text_summarization", "named_entity_recognition", "code_debugging",
            "logical_reasoning", "code_generation",
        ],
        reasoning_score=0.80,
        context_length=262144,
        max_output_tokens=8192,
        cost_per_1k_input=0.0003,
        cost_per_1k_output=0.0012,
        speed_tier=1,
    ),
]

LOCAL_MODELS: List[ModelInfo] = [
    ModelInfo(
        name="local-qwen2.5-0.5b",
        display_name="Qwen 2.5 0.5B (Local)",
        provider=ModelProvider.LOCAL,
        capabilities=[
            "factual_knowledge", "sentiment_classification", "text_summarization",
            "named_entity_recognition", "logical_reasoning", "code_generation",
        ],
        reasoning_score=0.35,
        context_length=32768,
        max_output_tokens=512,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        speed_tier=1,
    ),
]


COMPLEXITY_REQUIREMENTS: Dict[str, float] = {
    ComplexityLevel.TRIVIAL.value: 0.1,
    ComplexityLevel.SIMPLE.value: 0.25,
    ComplexityLevel.MEDIUM.value: 0.45,
    ComplexityLevel.COMPLEX.value: 0.65,
    ComplexityLevel.VERY_COMPLEX.value: 0.80,
}

TASK_KEYWORDS: Dict[str, List[str]] = {
    TaskCategory.FACTUAL_KNOWLEDGE.value: [
        "what is", "who is", "where is", "when did", "why does", "how does",
        "explain", "describe", "tell me about", "define", "meaning of",
        "capital of", "population", "invented", "discovered", "created",
        "history of", "difference between", "facts about", "known for",
    ],
    TaskCategory.MATH_REASONING.value: [
        "calculate", "solve", "compute", "math", "equation", "sum", "product",
        "add", "subtract", "multiply", "divide", "percentage", "ratio",
        "algebra", "geometry", "probability", "statistics", "formula",
        "how many", "total cost", "average", "find x", "simplify",
        "store has", "apples", "miles", "km", "dollars", "percent",
    ],
    TaskCategory.SENTIMENT_CLASSIFICATION.value: [
        "sentiment", "emotion", "positive", "negative", "neutral",
        "opinion", "feeling", "tone", "attitude", "classify",
        "label the sentiment", "is this positive", "is this negative",
    ],
    TaskCategory.TEXT_SUMMARIZATION.value: [
        "summarize", "summary", "tldr", "brief", "overview", "condense",
        "shorten", "gist", "in one sentence", "in a few words",
        "one sentence", "briefly describe", "short summary",
    ],
    TaskCategory.NAMED_ENTITY_RECOGNITION.value: [
        "extract", "entities", "named entities", "find names", "identify people",
        "who are", "organizations", "locations", "dates", "NER",
        "list all named", "find all names", "entities in",
    ],
    TaskCategory.CODE_DEBUGGING.value: [
        "debug", "fix", "bug", "error", "issue", "not working", "broken",
        "exception", "traceback", "wrong output", "incorrect", "fails",
        "this code", "this function", "this program",
    ],
    TaskCategory.LOGICAL_REASONING.value: [
        "if", "then", "logic", "reason", "deduce", "conclude", "puzzle",
        "riddle", "paradox", "syllogism", "premise", "argument",
        "which is true", "must be true", "can we conclude",
    ],
    TaskCategory.CODE_GENERATION.value: [
        "write a function", "write code", "implement", "create a function",
        "write a program", "code that", "function that", "class that",
        "def ", "function(", "return", "algorithm",
    ],
}

CATEGORY_TO_SYSTEM_PROMPT: Dict[str, str] = {
    TaskCategory.FACTUAL_KNOWLEDGE.value: (
        "You are a factual knowledge assistant. Provide accurate, concise answers. "
        "State facts directly. If unsure, say so. Keep responses brief and precise."
    ),
    TaskCategory.MATH_REASONING.value: (
        "You are a math reasoning assistant. Solve step by step. "
        "Show your work clearly. Give the final answer on its own line after 'Answer:'."
    ),
    TaskCategory.SENTIMENT_CLASSIFICATION.value: (
        "You are a sentiment classifier. Label the sentiment as positive, negative, or neutral. "
        "Provide a brief 1-sentence justification. Format: 'Sentiment: [label]. Justification: [reason]'"
    ),
    TaskCategory.TEXT_SUMMARIZATION.value: (
        "You are a summarizer. Condense the text to the requested length. "
        "Preserve key facts. Be concise and accurate. No extra commentary."
    ),
    TaskCategory.NAMED_ENTITY_RECOGNITION.value: (
        "You are an NER system. Extract all named entities and classify them as PERSON, ORGANIZATION, LOCATION, DATE, or OTHER. "
        "Format as a comma-separated list: 'EntityName (TYPE)'."
    ),
    TaskCategory.CODE_DEBUGGING.value: (
        "You are a code debugger. Identify the bug, explain why it fails, "
        "and provide the corrected code. Be specific about the error."
    ),
    TaskCategory.LOGICAL_REASONING.value: (
        "You are a logical reasoning assistant. Analyze the premises carefully. "
        "Apply deductive reasoning. State your conclusion clearly after 'Answer:'."
    ),
    TaskCategory.CODE_GENERATION.value: (
        "You are a code generation assistant. Write clean, correct, well-structured code. "
        "Include necessary imports. Follow the requested language's conventions. "
        "Add brief comments for clarity."
    ),
}

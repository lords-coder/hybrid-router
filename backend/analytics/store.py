from datetime import datetime
from typing import List, Optional
from collections import defaultdict
import json
import os


class AnalyticsEntry:
    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.timestamp = data.get("timestamp", datetime.now().isoformat())
        self.prompt = data.get("prompt", "")
        self.task_type = data.get("task_type", "")
        self.complexity = data.get("complexity", "")
        self.reasoning_level = data.get("reasoning_level", 0)
        self.model_name = data.get("model_name", "")
        self.model_display = data.get("model_display", "")
        self.provider = data.get("provider", "")
        self.is_local = data.get("is_local", False)
        self.input_tokens = data.get("input_tokens", 0)
        self.output_tokens = data.get("output_tokens", 0)
        self.total_tokens = data.get("total_tokens", 0)
        self.fireworks_tokens = data.get("fireworks_tokens", 0)
        self.tokens_saved = data.get("tokens_saved", 0)
        self.processing_time_ms = data.get("processing_time_ms", 0)
        self.confidence = data.get("confidence", 0)
        self.success = data.get("success", True)
        self.response_preview = data.get("response_preview", "")

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "prompt": self.prompt,
            "task_type": self.task_type,
            "complexity": self.complexity,
            "reasoning_level": self.reasoning_level,
            "model_name": self.model_name,
            "model_display": self.model_display,
            "provider": self.provider,
            "is_local": self.is_local,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "fireworks_tokens": self.fireworks_tokens,
            "tokens_saved": self.tokens_saved,
            "processing_time_ms": self.processing_time_ms,
            "confidence": self.confidence,
            "success": self.success,
            "response_preview": self.response_preview,
        }


class AnalyticsStore:
    def __init__(self):
        self.entries: List[AnalyticsEntry] = []
        self._file_path = os.path.join(os.path.dirname(__file__), "analytics_data.json")
        self._load()

    def _load(self):
        try:
            if os.path.exists(self._file_path):
                with open(self._file_path, "r") as f:
                    data = json.load(f)
                    self.entries = [AnalyticsEntry(e) for e in data]
        except Exception:
            self.entries = []

    def _save(self):
        try:
            with open(self._file_path, "w") as f:
                json.dump([e.to_dict() for e in self.entries], f, indent=2)
        except Exception:
            pass

    def log(self, entry_data: dict) -> AnalyticsEntry:
        entry = AnalyticsEntry(entry_data)
        self.entries.append(entry)
        self._save()
        return entry

    def get_all(self, limit: int = 100) -> List[dict]:
        sorted_entries = sorted(self.entries, key=lambda e: e.timestamp, reverse=True)
        return [e.to_dict() for e in sorted_entries[:limit]]

    def get_summary(self) -> dict:
        if not self.entries:
            return {
                "total_requests": 0,
                "total_tokens": 0,
                "total_fireworks_tokens": 0,
                "total_local_tokens": 0,
                "local_requests": 0,
                "fireworks_requests": 0,
                "tokens_saved_by_local": 0,
                "avg_processing_time": 0,
                "avg_confidence": 0,
                "model_usage": {},
                "task_distribution": {},
                "complexity_distribution": {},
            }

        total_tokens = sum(e.total_tokens for e in self.entries)
        total_fw_tokens = sum(e.fireworks_tokens for e in self.entries)
        local_entries = [e for e in self.entries if e.is_local]
        fw_entries = [e for e in self.entries if not e.is_local]
        avg_time = sum(e.processing_time_ms for e in self.entries) / len(self.entries)
        avg_conf = sum(e.confidence for e in self.entries) / len(self.entries)

        model_usage = defaultdict(lambda: {"count": 0, "tokens": 0, "fireworks_tokens": 0})
        for e in self.entries:
            model_usage[e.model_display]["count"] += 1
            model_usage[e.model_display]["tokens"] += e.total_tokens
            model_usage[e.model_display]["fireworks_tokens"] += e.fireworks_tokens

        task_dist = defaultdict(int)
        complexity_dist = defaultdict(int)
        for e in self.entries:
            task_dist[e.task_type] += 1
            complexity_dist[e.complexity] += 1

        return {
            "total_requests": len(self.entries),
            "total_tokens": total_tokens,
            "total_fireworks_tokens": total_fw_tokens,
            "total_local_tokens": total_tokens - total_fw_tokens,
            "local_requests": len(local_entries),
            "fireworks_requests": len(fw_entries),
            "local_percent": round(len(local_entries) / max(len(self.entries), 1) * 100, 1),
            "tokens_saved_by_local": sum(e.total_tokens for e in local_entries),
            "avg_processing_time": round(avg_time, 2),
            "avg_confidence": round(avg_conf, 2),
            "model_usage": dict(model_usage),
            "task_distribution": dict(task_dist),
            "complexity_distribution": dict(complexity_dist),
        }

    def get_history(self, limit: int = 50, search: Optional[str] = None) -> List[dict]:
        entries = sorted(self.entries, key=lambda e: e.timestamp, reverse=True)
        if search:
            search_lower = search.lower()
            entries = [e for e in entries if search_lower in e.prompt.lower() or search_lower in e.model_display.lower()]
        return [e.to_dict() for e in entries[:limit]]

    def get_model_comparison(self) -> List[dict]:
        model_stats = defaultdict(lambda: {"count": 0, "total_tokens": 0, "fireworks_tokens": 0, "avg_time": 0})
        for e in self.entries:
            model_stats[e.model_display]["count"] += 1
            model_stats[e.model_display]["total_tokens"] += e.total_tokens
            model_stats[e.model_display]["fireworks_tokens"] += e.fireworks_tokens
            model_stats[e.model_display]["avg_time"] += e.processing_time_ms

        result = []
        for model, stats in model_stats.items():
            result.append({
                "model": model,
                "requests": stats["count"],
                "total_tokens": stats["total_tokens"],
                "fireworks_tokens": stats["fireworks_tokens"],
                "avg_time": round(stats["avg_time"] / max(stats["count"], 1), 2),
            })

        return sorted(result, key=lambda x: x["requests"], reverse=True)

    def clear(self):
        self.entries = []
        self._save()


analytics_store = AnalyticsStore()

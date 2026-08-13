from typing import List, Dict, Any


def calculate_evaluation_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculates comprehensive benchmark metrics over the evaluation run."""
    total = len(results)
    if total == 0:
        return {}

    intent_correct = sum(1 for r in results if r["intent_match"])
    sql_valid_count = sum(1 for r in results if r.get("is_valid_sql") is True or r["category"] in ["chitchat", "security_malicious"])
    security_blocked = sum(1 for r in results if r["category"] == "security_malicious" and r.get("security_passed"))
    security_total = sum(1 for r in results if r["category"] == "security_malicious")

    latencies = [r["latency_ms"] for r in results if "latency_ms" in r]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    retries_list = [r.get("retries", 0) for r in results]
    avg_retries = round(sum(retries_list) / len(retries_list), 2) if retries_list else 0.0

    return {
        "total_evaluations": total,
        "intent_accuracy": round((intent_correct / total) * 100, 2),
        "sql_validity_rate": round((sql_valid_count / total) * 100, 2),
        "security_defense_rate": round((security_blocked / security_total * 100), 2) if security_total > 0 else 100.0,
        "average_latency_ms": avg_latency,
        "average_retries": avg_retries
    }

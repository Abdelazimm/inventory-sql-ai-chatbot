# Inventory SQL AI Assistant — Evaluation Benchmark Suite

This directory contains the automated evaluation framework and benchmarking dataset for the Text-to-SQL Inventory Assistant.

## Benchmark Dataset
The evaluation dataset (`dataset.json`) contains **35 curated enterprise queries** across 7 categories:
1. **Lookup**: Single-table attribute lookups (e.g. status, serial numbers, emails).
2. **Aggregation**: `SUM`, `AVG`, `COUNT` calculations on inventory values, bills, and quantities.
3. **Joins**: Multi-table relational joins across `Assets`, `Sites`, `Locations`, `Vendors`, `PurchaseOrders`, `SalesOrders`.
4. **Ranking & Top-N**: `ORDER BY ... LIMIT` queries for cost, asset counts, line totals.
5. **Empty Results Handling**: Questions targeting non-existent dates/records to verify empty responses.
6. **Chitchat**: Greetings and conversational inquiries.
7. **Security & Prompt Injections**: Adversarial SQL injection attempts (`DROP TABLE`, stacked queries, `ATTACH DATABASE`).

## Running the Benchmark

```bash
python -m eval.run_evaluation
```

## Metrics Measured
- **Intent Accuracy**: Accuracy in routing messages to `database_query`, `chitchat`, or `mutation`.
- **SQL Validity Rate**: Percentage of generated queries passing AST syntax and read-only validation.
- **Security Defense Rate**: Percentage of malicious and destructive injection attempts successfully neutralized.
- **Average Latency**: End-to-end processing latency in milliseconds.
- **Average Retries**: Average number of self-correction attempts required.

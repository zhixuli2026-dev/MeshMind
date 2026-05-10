# 混合检索策略

## 融合方式

向量检索 + BM25 分数进行**加权求和**：

```
final_score = 0.7 × vector_score + 0.3 × bm25_score
```

- `vector_score`：cosine similarity，归一化到 [0, 1]
- `bm25_score`：pg full-text search `ts_rank` 归一化到 [0, 1]

## 权重

| 来源 | 权重 | 说明 |
|------|------|------|
| 向量检索 | 0.7 | 语义相似度为主 |
| BM25 | 0.3 | 关键词精确匹配为辅 |

后续根据实际效果调整权重比例。

## 实现

```python
async def hybrid_search(query: str, workspace_id: UUID, limit: int = 20) -> list[SearchResult]:
    embedding = encoder.encode(query)
    vector_results = await node_repo.search_by_embedding(embedding, workspace_id, limit=limit*2)
    bm25_results = await node_repo.search_by_text(query, workspace_id, limit=limit*2)

    # 合并去重 + 加权
    scores = {}
    for node, dist in vector_results:
        scores[node.id] = 0.7 * (1 - dist)  # cosine distance → similarity
    for node in bm25_results:
        bm25_norm = min(node.rank / max(r.rank for r in bm25_results), 1.0)
        scores[node.id] = scores.get(node.id, 0) + 0.3 * bm25_norm

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [SearchResult(node_id=id, score=s) for id, s in ranked]
```

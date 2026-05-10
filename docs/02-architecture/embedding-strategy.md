# Embedding 策略

## 模型

| 配置 | 值 |
|------|-----|
| 模型 | BAAI/bge-m3 |
| 维度 | 1024 |
| 最大序列长度 | 8192 tokens |
| 模型大小 | ~2.3 GB (FP16) |
| 部署 | 本地 GPU (RTX 3060 12GB) / sentence-transformers |

## 生成策略

### 何时生成

| 场景 | 说明 |
|------|------|
| 新知识点创建 | 对 `title + "\n" + summary` 生成 embedding |
| 文档提炼产生多个知识点 | 每个新节点各生成一个 embedding |
| 知识摘要更新 | 内容变化时重新生成 embedding |

### 输入格式

```
model.encode(f"{node.title}\n{node.summary}")
```

只用 L1 标题 + L2 摘要生成向量，不含 L3 文档全文。

## 存储

- pgvector `vector(1024)` 列存储
- 使用 IVFFlat 索引加速，`vector_cosine_ops` 余弦距离

## 缓存策略

开发阶段不引入额外缓存层，sentence-transformers 的 `encode` 调用本身有内存缓存。后续如果需要可加 Redis 缓存已编码文本的 embedding 结果。

## 批量处理

文档提炼时可能一次产生多个知识点：

```python
texts = [f"{node.title}\n{node.summary}" for node in new_nodes]
embeddings = model.encode(texts, batch_size=32)
```

batch_size=32 适合 RTX 3060 的 12GB 显存。

## 性能估算

| 指标 | 值 |
|------|-----|
| 单次编码延迟 | ~28ms |
| 吞吐量 | ~3,400 texts/sec |
| 启动时间（加载模型） | ~5-10s |

# LLM 路由设计

## 双模型分层策略

所有 LLM 调用分为两个层级。统一使用 DeepSeek。

| 层级 | 模型 | 用途 |
|------|------|------|
| **复杂任务** | `deepseek-v4-pro` | 深度推理、分析、知识提炼、Agent 决策 |
| **简单任务** | `deepseek-v4-flash` | 快速判断、相似度比较、简单分类 |

## 任务分配

### 复杂任务（Pro）

- 对话知识提炼（区分是不是知识、哪类知识）
- 文档拆解（整篇 vs 拆散，知识点提取）
- Agent React Loop 的 Think 阶段
- 知识冲突的语义判断
- 回答的最终整理和溯源
- 知识入库的维护判断（一样/相似/矛盾）

### 简单任务（Flash）

- 向量检索后的相似度快速筛除（明显不相关的候选）
- 知识类型的基础分类（已有明确上下文的）
- 简单的关系确认（两个节点已经非常接近）
- 活力值衰减计算（数值计算）

## 路由逻辑

```python
def route_task(task: Task) -> Model:
    if task.complexity == Complexity.HIGH:
        return "deepseek-v4-pro"
    if task.requires_deep_reasoning():
        return "deepseek-v4-pro"
    return "deepseek-v4-flash"  # 待确认具体模型名称
```

## 设计原则

- **只分两层**：不做多级粒度划分，保持路由逻辑简单
- **Pro 是默认**：不确定复杂度时，默认走 Pro，保证质量
- **Flash 做减法**：只在明确可以快速判断时用 Flash，节省延迟和成本
- **Harness 统一管理**：路由逻辑封装在 LLM Harness 层，业务代码不感知

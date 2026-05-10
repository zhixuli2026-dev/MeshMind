"""LLM prompt templates for knowledge extraction and analysis."""

# ── Knowledge Extraction ────────────────────────────────────────────

EXTRACT_FROM_CONVERSATION = """\
Analyze the following conversation and extract knowledge points worth preserving.

For each knowledge point, provide:
- title: One short sentence identifying the knowledge
- summary: One sentence explaining the knowledge content
- type: One of "law" (foundational truth, nearly immutable), "rule" (team norm, changes slowly),
  "best_practice" (current recommended approach, evolves), "event" (time-bounded occurrence)

Rules:
- Not every sentence is knowledge. Only extract meaningful, reusable insights.
- If nothing qualifies, return an empty list.
- Law type should only be assigned when the knowledge represents a foundational, nearly immutable truth.
- Do NOT invent knowledge. Only extract what is explicitly stated or strongly implied.

Conversation:
{conversation_text}
"""

EXTRACT_FROM_DOCUMENT_DECISION = """\
Analyze the following markdown document and decide how to process it.

Document title: {title}

Choose ONE approach:
1. "whole" — The document covers a single focused topic. Extract one knowledge point with a summary.
2. "split" — The document covers multiple distinct topics. Break it into separate knowledge points.

Respond with a JSON object:
{{"strategy": "whole"|"split"}}

Document (first 3000 chars):
{content_preview}
"""

EXTRACT_FROM_DOCUMENT_SPLIT = """\
Extract knowledge points from this document section.

For each knowledge point:
- title: One short sentence
- summary: One sentence
- type: "law"|"rule"|"best_practice"|"event"

Document title: {title}
Content:
{content}
"""

EXTRACT_FROM_DOCUMENT_WHOLE = """\
Summarize this document as a single knowledge point.

- title: One short sentence capturing the document's knowledge
- summary: 2-3 sentences covering the key points
- type: "law"|"rule"|"best_practice"|"event"

Document title: {title}
Content:
{content}
"""

# ── Graph Connection ─────────────────────────────────────────────────

GRAPH_CONNECT_JUDGMENT = """\
A new knowledge point is being added to the knowledge graph. Compare it with the existing candidate below.

New knowledge:
  Title: {new_title}
  Summary: {new_summary}
  Type: {new_type}

Existing candidate:
  Title: {existing_title}
  Summary: {existing_summary}
  Type: {existing_type}

Determine the relationship between them. Choose exactly one:

1. "duplicate" — They express fundamentally the same thing. Skip adding the new one.
2. "similar" — Very closely related but the new one adds value. Update existing, merge authors.
3. "conflict" — They contradict each other on the same topic. Mark both as conflicting.
4. "related" — Connected but distinct. Choose a relation type:
   - "prerequisite": Understanding the existing node is needed before the new one
   - "complementary": Both together form a complete understanding
   - "derived_from": The new node is derived from the existing one
5. "unrelated" — No meaningful connection.

Respond with JSON:
{{"decision": "...", "relation_type": "..."|null, "reasoning": "brief explanation"}}
"""

# ── Maintenance ──────────────────────────────────────────────────────

MAINTENANCE_CHECK = """\
A knowledge point is being retrieved and used to answer a question. Evaluate whether this knowledge was actually helpful.

Question: {question}
Answer: {answer}

Knowledge used:
  Title: {node_title}
  Summary: {node_summary}

Did this knowledge point have a decisive impact on the answer?
Respond with JSON:
{{"helpful": true|false, "reasoning": "brief explanation"}}
"""

# ── Agent Think ──────────────────────────────────────────────────────

AGENT_THINK = """\
You are a knowledge agent researching the following question.

Question: {question}

Currently loaded knowledge:
{loaded_knowledge}

Analyze the situation:
1. Is the loaded knowledge sufficient to answer the question?
2. If not, what specific information is still missing?
3. What should be searched next?

Respond with JSON:
{{
    "enough": true|false,
    "missing": ["list", "of", "missing", "topics"],
    "search_query": "next search query"|null
}}
"""

# ── Answer Composition ───────────────────────────────────────────────

COMPOSE_ANSWER = """\
Answer the user's question based on the retrieved knowledge.

Question: {question}

Retrieved knowledge:
{knowledge_context}

Rules:
- Cite knowledge sources inline using [N] markers where N is the source number
- If knowledge is insufficient to fully answer, state what's unclear
- Be concise and direct

Answer:
"""

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

---

## MeshMind 项目治理规范

### 优先级体系

项目的目标优先级从高到低：

1. **设计理念与原则 (`docs/01-philosophy/`)** — 项目的灵魂，所有决策的最高依据
2. **功能与特性 (`docs/03-features/`)** — 项目对外交付的价值载体
3. **架构 (`docs/02-architecture/`)** — 服务于以上两者，是支撑手段而非目的

架构为了理念和功能而存在，不可本末倒置。

### 技能使用规范

| 场景 | 技能 | 约束 |
|------|------|------|
| 前端设计 | `ui-ux-pro-max` | **必须使用** |
| 前端设计 | `frontend-design` | 灵活选择 |
| 后端开发 | `superpowers` | **必须使用** |
| 架构设计 | `superpowers` | **必须使用** |
| 功能开发 | `superpowers` | **必须使用** |

### 文档规范

- 文档是给 Claude（我）看的，不是给人类开发者看的
- 边写代码边记录，不事后补文档
- 文档结构：
  - `CLAUDE.md`（根目录）— 项目治理框架
  - `docs/01-philosophy/` — 设计理念与原则
  - `docs/02-architecture/` — 架构
  - `docs/03-features/` — 功能与特性

### 严禁事项

- **严禁 Hard Coding**：不允许为了通过测试而写死代码。所有逻辑必须有真实的实现。
- **严禁猜测后继续**：coding 过程中如果有不明白的地方，**必须暂停并询问用户**，不允许自行假设后继续。

### 上下文管理

- 每次 **context compaction（上下文压缩）** 之后，必须重新加载 `docs/` 中的关键文档，防止上下文丢失导致项目规范被遗忘。

### 测试策略

- **优先 E2E 测试和功能测试**：以最终用户/Agent 可感知的功能验证为主。
- **单元测试适度**：不对每个函数都写单元测试，重点关注关键逻辑和对外接口。
- 测试服务于功能验证，不为测试覆盖率而测试。

### Agent 设计原则

项目中部分模块采用 LLM-based 智能体设计，这类模块需要**柔性化策略**：
- 使用 LLM 的推理能力做判断，而非硬编码规则
- 允许模糊匹配和语义理解，而非精确字符串匹配
- 给 LLM 足够的上下文和判断空间，而非严苛的输入约束

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

## Superpowers Skill Library

This project uses the [Superpowers skill library](~/.claude/skills/superpowers/) to enforce structured workflows and best practices.

### The 1% Rule
**If there's even a 1% chance a skill applies, you MUST use it.**

### Available Skills

| Skill | Use When... |
|-------|-------------|
| `test-driven-development` | Writing code (TDD cycle) |
| `systematic-debugging` | Debugging issues |
| `brainstorming` | Planning new features |
| `writing-plans` | Creating implementation plans |
| `executing-plans` | Running plans step by step |
| `verification-before-completion` | Before claiming work is done |
| `using-superpowers` | How to use the skill system |

### Core Principles

1. **Test-Driven Development** – Write tests first, always
2. **Systematic over ad-hoc** – Process over guessing
3. **Verify before claiming** – Prove it works
4. **Plan before coding** – Think first

### Usage

Before responding to any request, check if a skill applies. If yes, read the skill file and follow its workflow exactly. Never skip steps.

---

## UI/UX Pro Max - Design Intelligence

This project uses the [UI/UX Pro Max skill](.claude/skills/ui-ux-pro-max/) for comprehensive UI/UX design guidance.

### When to Use

**Must Use:**
- Designing new pages (Landing Page, Dashboard, Admin, SaaS, Mobile App)
- Creating or refactoring UI components (buttons, modals, forms, tables, charts)
- Choosing color schemes, typography systems, spacing standards
- Reviewing UI code for UX, accessibility, or visual consistency
- Implementing navigation, animations, or responsive behavior

### Quick Start

```bash
# Generate complete design system
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<product_type> <keywords>" --design-system -p "Project Name"

# Domain searches
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain>
```

**Available domains:** `product`, `style`, `typography`, `color`, `landing`, `chart`, `ux`, `google-fonts`

### Core Features

- **67+ UI Styles** - Glassmorphism, minimalism, brutalism, neumorphism, bento grid, etc.
- **161 Color Palettes** - By product type and industry
- **57 Font Pairings** - With Google Fonts imports
- **99 UX Guidelines** - Best practices and anti-patterns
- **25 Chart Types** - Data visualization recommendations

### Priority Rules

1. **Accessibility (CRITICAL)** - Contrast 4.5:1, focus states, keyboard nav
2. **Touch & Interaction (CRITICAL)** - Min 44×44px touch targets
3. **Performance (HIGH)** - WebP/AVIF, lazy loading, CLS < 0.1
4. **Style Selection (HIGH)** - Match product type, consistency
5. **Layout & Responsive (HIGH)** - Mobile-first breakpoints

---

## Frontend Design (Anthropic Official)

This project uses the [Frontend Design skill](.claude/skills/frontend-design/) — Anthropic's official skill for creating distinctive, production-grade frontend interfaces.

### When to Use

Use when building:
- Web components, pages, or applications
- Landing pages, dashboards, or marketing sites
- React/Vue/HTML components
- Any web UI that needs styling or beautification

### Design Philosophy

Avoid generic "AI slop" aesthetics (purple gradients, Inter font, predictable layouts). Instead:

**Choose a BOLD aesthetic direction:**
- Brutally minimal
- Maximalist chaos
- Retro-futuristic
- Organic/natural
- Luxury/refined
- Playful/toy-like
- Editorial/magazine
- Brutalist/raw
- Art deco/geometric
- Soft/pastel
- Industrial/utilitarian

### Five Design Dimensions

| Dimension | Guidelines |
|-----------|------------|
| **Typography** | Avoid Inter/Roboto/Arial/Space Grotesk. Choose distinctive, characterful fonts |
| **Color & Theme** | Dominant colors with sharp accents. Use CSS variables. No clichéd purple-on-white |
| **Motion** | High-impact orchestrated animations. CSS for vanilla, Framer Motion for React |
| **Spatial Composition** | Asymmetry, overlap, diagonal flow, grid-breaking, generous negative space |
| **Backgrounds & Details** | Gradient meshes, noise textures, geometric patterns, layered transparencies |

### Key Rules

- **NEVER** use generic fonts (Inter, Roboto, Arial, system fonts)
- **NEVER** use clichéd purple gradients on white
- **ALWAYS** commit to a clear aesthetic direction
- **ALWAYS** make unexpected, context-specific choices

---

## MCP (Model Context Protocol) Servers

This project uses MCP servers to extend Claude Code capabilities.

### Playwright MCP

**Package:** `@playwright/mcp`
**Config:** [`.claude/mcp.json`](.claude/mcp.json)

**Capabilities:**
- Browser automation and control
- Page navigation and interaction
- Screenshot capture
- Element inspection and manipulation
- Form filling and submission
- Network monitoring

**Usage:**
When you need to:
- Test web applications in real browsers
- Capture screenshots of UI components
- Debug UI issues visually
- Automate browser interactions

**Requirements:**
- Playwright browsers installed (Chromium, Firefox, WebKit)

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

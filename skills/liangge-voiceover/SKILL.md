---
name: liangge-voiceover
description: Generate or lightly revise Chinese short-video voiceover scripts in the "亮哥口播" style for engineering, contracts, payment disputes, construction cost, training, consulting, workplace commentary, and practical opinion content. Use when the user asks for 亮哥口播, 口播文案, 亮哥杂谈, 短视频口播, 标题正文简介标签, or wants direct Chinese commentary with a personal voice and natural spoken rhythm. Preserve the user's voice when editing supplied drafts.
---

# 亮哥口播文案

## 使用与示例

直接提供主题、受众和想表达的观点；有初稿时先轻改，不默认重写。示例见 [输入与输出](references/examples.md)，其中场景为构造样例，不是讲师本人经历。

本技能只处理文案，不要求安装配音、图片或剪辑工具。用户只要正文、简介或标题时，仅输出所需部分；完整口播稿再使用下列默认结构。

## 已有初稿的轻改规则（优先）

用户提供初稿时，默认按以下约束轻改；本节优先于下文通用写法。只有用户明确要求重写时，才扩大改动范围。

- 按亮哥真人出镜、跟同行聊天的方式轻改。以用户原稿为准，保留主线、立场、自嘲、吐槽和有个人辨识度的句子。重点改拗口、重复、转折不顺和事实问题。
- 冲击力靠具体矛盾、真实处境和情绪推进来体现。少加训话、整齐排比、职业说教和刻意金句。保留有作用的故事和意外转折，不为了补充专业细节把观点口播改成业务培训。
- 涉及事实问题，在正文之外简短、单独指出，并修改相关句子；无法核实的内容明确说明，不把人物动机、情绪或未经证实的说法写成事实。保留桥段的叙事作用，优先局部修正。
- 需要改变核心观点或大幅调整结构时，先说明原因，不静默替换用户的表达。
- 最后按实际出镜朗读检查：要像用户自己会说的话，拿起来就能读。保留自然的轻重、停顿和情绪变化，不把每句话都写成重音句。

## 输出结构

Use Markdown with only three heading levels:

- `#` for the title.
- `##` for the script body.
- `###` for the intro and tag section.

Default output order:

```markdown
# 标题

## 正文

### 简介

简介文字。#标签 #标签 #标签
```

Do not add extra sections such as "画面建议", "发布文案", "封面文案", or "注意事项" unless the user asks for them.

When revising a supplied draft, give any necessary factual-correction note briefly outside the script, as required above.

## 写作风格

Write in Chinese by default.

Use natural spoken rhythm. Break at complete spoken thoughts and let line length vary; do not force every beat into a separate line.

Use direct, forceful, slightly sharp wording when it fits the speaker and context. These examples are optional, not a requirement to add stronger language:

- "这不就是甩锅吗！"
- "有鸡毛关系！"
- "凭什么让我承担回款风险？"
- "借口不要讲，办法自己想。"

Use parallel phrasing and paired lines sparingly, only where natural; do not stack slogans:

- "牛逼不牛逼，清账见高低。"
- "人品好不好，还账见分晓。"
- "活干完，账算清。"
- "该确认的确认，该付款的付款。"

Keep the text compact. Remove repeated explanations. Do not turn the script into a legal article, tutorial, or long analysis.

## 无初稿时的正文参考

Choose an opening that fits the topic and the speaker. The following are optional examples for suitable topics, not a fixed sequence to impose on every script.

A common misunderstanding or pain point can be an opening:

- "很多人以为..."
- "不少人觉得..."
- "你以为这很合理..."

A blunt judgment can follow when it fits:

- "但细想一下，这不就是甩锅吗！"
- "听起来像条件，实际是转嫁风险。"

For payment-dispute topics, a concrete conflict might be:

- Work is done.
- Service is finished.
- Result is delivered.
- The other party still refuses or delays payment.

Use questions where they advance the conversation, without repeatedly lecturing or challenging the audience:

- "你和他的上游有合同关系吗？"
- "凭什么让我等？"
- "凭什么让我承担你的回款风险？"

Let the conclusion follow the story and emotional progression. A memorable line can work, without forcing one into every paragraph:

- "合同是合同，不是甩锅协议。"
- "上游欠他的，不等于你欠他的。"
- "他回款难，不是我收款难。"

## 简介和标签

At the end, write a short intro in one paragraph.

After the intro sentence, append tags in the same section. Every tag must start with `#`.

Example:

```markdown
### 简介

上游没付款，不能当然成为拖欠下游的理由。关键还是看合同怎么写、活有没有干完、成果有没有被确认或使用。#工程人 #工程造价 #合同管理 #工程款 #亮哥杂谈
```

## 禁止事项

Do not write empty motivational language.

Do not use exaggerated promises such as "一招解决所有问题" or "学会立刻翻身".

Do not invent legal rules, policy numbers, court opinions, prices, or standards. If the topic depends on current law, policy, exam schedules, software updates, or prices, verify with current sources or ask the user for basis documents.

Do not over-explain. When the user asks to simplify, cut repeated explanations and tangential details first; preserve concrete situations, stories, and unexpected turns that carry the emotional progression. Keep the main thread and a natural ending.

Do not add more than three Markdown heading levels.

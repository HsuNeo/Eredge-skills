---
name: exam-paper-generator
description: Generate training exam papers from course materials, PDFs, PPTs, outlines, or user-provided teaching content. Use when the user asks to 出试卷, 出题, 生成培训试题, 生成考试题, make single-choice or multiple-choice questions, write answers and explanations, or create a question bank based on a training course, especially for construction cost, highway engineering, Office workflow, or other professional training materials.
---

# Exam Paper Generator

## Core Rule

Create exam questions from the material the user says they will teach, but do not expose the material as the authority in the question text or explanation.

Never write phrases such as:

- 根据课件
- 根据培训
- 根据上面的内容
- 课件中提到
- 培训中提到
- 按本PPT

Instead, anchor wording to one of:

- named standards, specifications, quota books, laws, contract documents, or industry documents if the material clearly supports that source;
- professional practice, such as `在公路工程造价实务中`, `在桥梁桩基造价中`, `某公路工程编制施工图预算时`;
- the discipline itself, such as `公路工程`, `工程造价管理`, `清单计量规则`, `预算定额应用`.

If a point appears in the source material but no explicit standard source can be confirmed, phrase it as practical judgment or exam background, not as a quoted rule.

## Workflow

1. Locate and read the source materials.
   - Prefer the exact files and folders the user provides.
   - For PDFs/PPTs, extract text with page or slide markers when possible.
   - If visuals matter, inspect representative rendered pages or slides.
   - If there are existing sample exams or templates, read them before writing.

2. Build a coverage map before drafting.
   - Identify the taught modules, not every page.
   - Distribute questions across the main modules.
   - For technical training, include concepts, calculation rules,计量规则,定额套用,易错点, and case-style application.
   - Avoid over-concentrating on the first chapter unless the source material itself is clearly weighted that way.

3. Follow the requested exam format exactly.
   - Match the requested number of single-choice, multiple-choice, judgment, calculation, or short-answer questions.
   - If the user gives a template, preserve its structure: question text, options, reference answer, explanation.
   - For single-choice questions, provide exactly one correct option unless the user asks otherwise.
   - For multiple-choice questions, provide at least two correct options and ensure distractors are plausible.

4. Write professional question stems.
   - Prefer realistic background: `某公路工程...`, `在编制施工图预算时...`, `在桥梁桩基造价中...`, `某隧道工程...`.
   - Make the stem test one clear point.
   - Avoid trick wording that depends on guessing language rather than understanding.
   - Do not use course-internal references such as page numbers, slide numbers, lecturer wording, or `课件`.

5. Write options carefully.
   - Keep options parallel in grammar and scope.
   - Distractors may include content not present in the source material, if they are reasonable wrong answers.
   - Avoid impossible or joke options unless the user explicitly wants an easy quiz.
   - Do not make the correct answer consistently the same letter.

6. Write answers and explanations.
   - The reference answer should be compact, such as `参考答案：B` or `参考答案：ABCD`.
   - Explanations should cite or paraphrase the proper authority when known:
     - `根据《公路工程建设项目概算预算编制办法》（JTG 3830-2018）...`
     - `根据《公路工程预算定额》（JTG/T 3832-2018）...`
     - `根据《公路工程标准施工招标文件》（2018年版）...`
     - `按公路工程清单计量规则...`
   - If the source point is practical rather than a confirmed rule, explain with `公路工程造价实务中...`, `编制造价文件时通常...`, or `施工组织和组价时应...`.
   - Do not write `资料显示`, `课件说明`, or `培训中讲到`.

7. Verify before final delivery.
   - Count each question type.
   - Count answers and explanations.
   - Search the output for banned words: `课件`, `培训中`, `根据培训`, `根据课件`, `上面的内容`.
   - Check that every question is tied to the material's taught content, even if the wording is framed by standards or engineering practice.
   - Save the output in the user-requested folder when the user asks for a file.

## Highway Cost Exam Defaults

When generating highway engineering cost questions and the user does not specify another authority, use these common anchors when supported by the material:

- 《公路工程建设项目概算预算编制办法》（JTG 3830-2018）
- 《公路工程预算定额》（JTG/T 3832-2018）
- 《公路工程标准施工招标文件》（2018年版）
- 公路工程清单计量规则
- 公路工程造价实务

Useful scenario wording:

- `某公路工程编制施工图预算时...`
- `在路基土石方清单计量中...`
- `在桥梁钻孔灌注桩造价中...`
- `某隧道工程进行洞身开挖组价时...`
- `在交通安全设施工程计量中...`

## Output Template

Use this structure unless the user provides a different one:

```markdown
## 一、单项选择题

1. 某公路工程编制施工图预算时，关于……的说法正确的是（    ）。
A. ……
B. ……
C. ……
D. ……

参考答案：B
解析：
根据《……》或按公路工程造价实务，……。

## 二、多项选择题

1. 在……中，正确的有（    ）。
A. ……
B. ……
C. ……
D. ……
E. ……

参考答案：ABCD
解析：
根据《……》或按公路工程造价实务，……。
```

## Quality Bar

The final paper should look like a real professional exam, not a course note summary. It should test whether the learner can use the taught content in工程造价、计量、定额套用、识图算量、软件实操 or similar working contexts.

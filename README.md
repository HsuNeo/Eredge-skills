# Eredge Skills

可单独安装的 Codex Skill。每个技能保存在 `skills/<技能名>/` 下，包含说明及其需要的脚本、参考资料。

| Skill | 用途 |
| --- | --- |
| [total-commander-config](skills/total-commander-config/SKILL.md) | 维护 Windows Total Commander 的菜单、工具栏、标签组和图标，处理目录迁移及失效引用 |
| [liangge-voiceover](skills/liangge-voiceover/SKILL.md) | 保留“亮哥口播”风格，起草或轻改工程行业短视频文案；含输入输出示例 |
| [de-ai-writer](skills/de-ai-writer/SKILL.md) | 中文文章润色与去模板化，保留事实、立场及场景语气；含修改前后对照 |
| [short-video-assets](skills/short-video-assets/SKILL.md) | 根据字幕或口播制作横竖图、动画和封面，也支持单张工程科普图文；含依赖与交付示例 |

## 安装

在 Codex 中输入：

```text
使用 $skill-installer 安装 https://github.com/HsuNeo/Eredge-skills/tree/main/skills/total-commander-config
```

安装其他技能时，将链接末尾改为 `liangge-voiceover`、`de-ai-writer` 或 `short-video-assets`。各技能可独立安装，不要求装全套。

也可下载仓库，将需要的 `skills/<技能名>` 整个文件夹复制到自己的 `~/.codex/skills/`。安装后从下轮对话开始使用。目标目录已有同名 Skill 时，先备份并保留个人修改。

## TC 技能的版本与适配范围

其中 `total-commander-config` 根据 **Total Commander 11.03 飞扬时空定制版本**的菜单、标签与图标维护工作整理。

其他版本的操作方式类似，但没有逐一进行适配验证。**是否适配当前版本、定制版和实际配置，需要使用者自行测试。** 使用前应备份现有配置，检查脚本通过也不等于真实 TC 界面已经验收。

## 使用

```text
使用 $total-commander-config，在我的培训菜单中新增一个项目标签，图标与相邻项目一致。
TC 安装目录：D:\Tools\TotalCommander
项目目录：D:\Work\Training\NewProject
```

TC Skill 让 Codex 先读取现有配置、备份，再修改并检查；它不是替换整套 TC 配置的安装包。TC 内部引用使用 `%Commander_path%`，保留已有目录布局、面板选项及不属于本次任务的入口。

TC 公开版的 `references/personal-layout.md` 是通用模板，不包含发布者的真实项目目录。日常优先使用自己的布局时，可在本机安装后的该文件中记录已确认的目录、必留菜单与模板；升级时保留这些修改。

内容制作技能的调用示例：

```text
使用 $liangge-voiceover 轻改这段工程口播，保留原观点，只改不顺口的地方。
使用 $de-ai-writer 润色这篇产品介绍，保留功能限制，不增加案例与效果承诺。
使用 $short-video-assets 根据附件 SRT 做素材包，先复用我提供的照片，成品保存到指定主题目录。
```

口播和润色技能只处理文本，不要求配音、绘图或剪辑工具。短视频素材技能需要当前环境实际提供相应的文件读取、图片生成/编辑或动画导出能力；工具和素材库不随仓库附送，见其 [依赖说明](skills/short-video-assets/references/tools-and-paths.md)。未配置个人素材库也能使用；本机偏好可记录在该技能的 `references/local-preferences.md`，升级时保留个人修改。

## 内容来源与示例

这三个内容技能依据本地使用工作流整理，示例为说明行为而构造，不是客户案例或实际生成结果。`de-ai-writer` 本次用中文重新整理编辑流程，不包含第三方 `humanizer` 的正文、程序或其他同名项目的规则引擎；本地同步记录与同名检索不足以证明最初作者，因此不作“已证实原创来源”的声明。

“去AI味”表示减少模板化表达，不承诺检测分数。短视频素材示例中的文件和动画是交付约定，实际产出须按工具能力完成并检查，不能把规划清单当成成品。

## 检查脚本

所有技能的入口和相对引用可通过标准库脚本检查：

```text
python tools/check_skills.py --self-test
python tools/check_skills.py
```

在 Windows PowerShell 5.1 或 PowerShell 7 中运行：

```powershell
# 临时目录自检，不接触真实 TC。
& .\skills\total-commander-config\scripts\Test-TcConfig.SelfTest.ps1

# 只读检查现有安装；按实际布局修改目录参数。
$result = & .\skills\total-commander-config\scripts\Test-TcConfig.ps1 `
  -Root 'D:\Tools\TotalCommander' -MenuDirectory 'Bar\xpl' -TabDirectory 'Tab'
$result | ConvertTo-Json -Depth 6
```

遇到旧中文 ANSI 文件可显式传入 `-LegacyCodePage 936`。检查结果将配置结构或引用错误与未核实的业务目录分开列出；不会执行菜单命令，也不证明真实 TC 界面、系统资源图标索引或压缩包条目已验收。

仓库只提供 Skill 和检查脚本，不附带 Total Commander 程序、注册文件、第三方图标库或用户业务资料。

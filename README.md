# Eredge Skills

可单独安装的 Codex Skill。每个技能保存在 `skills/<技能名>/` 下，包含说明及其需要的脚本、参考资料。

| Skill | 用途 |
| --- | --- |
| [total-commander-config](skills/total-commander-config/SKILL.md) | 维护 Windows Total Commander 的菜单、工具栏、标签组和图标，处理目录迁移及失效引用 |

## 安装

在 Codex 中输入：

```text
使用 $skill-installer 安装 https://github.com/HsuNeo/Eredge-skills/tree/main/skills/total-commander-config
```

也可下载仓库，将 `skills/total-commander-config` 整个文件夹复制到自己的 `~/.codex/skills/`。安装后从下轮对话开始使用。目标目录已有同名 Skill 时，先备份并保留个人修改。

## 版本与适配范围

本 Skill 根据 **Total Commander 11.03 飞扬时空定制版本**的菜单、标签与图标维护工作整理。

其他版本的操作方式类似，但没有逐一进行适配验证。**是否适配当前版本、定制版和实际配置，需要使用者自行测试。** 使用前应备份现有配置，检查脚本通过也不等于真实 TC 界面已经验收。

## 使用

```text
使用 $total-commander-config，在我的培训菜单中新增一个项目标签，图标与相邻项目一致。
TC 安装目录：D:\Tools\TotalCommander
项目目录：D:\Work\Training\NewProject
```

这个 Skill 让 Codex 先读取现有配置、备份，再修改并检查；它不是替换整套 TC 配置的安装包。TC 内部引用使用 `%Commander_path%`，保留已有目录布局、面板选项及不属于本次任务的入口。

公开版的 `references/personal-layout.md` 是通用模板，不包含发布者的真实项目目录。日常优先使用自己的布局时，可在本机安装后的该文件中记录已确认的目录、必留菜单与模板；升级时保留这些修改。

## 检查脚本

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

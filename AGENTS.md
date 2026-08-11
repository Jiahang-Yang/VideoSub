# VideoSub 项目指南

本工作区是「油管视频 → 中英双语字幕」流水线。完整工作流见 `README.md`，脚本细节见工作流技能。

## 字幕任务必读技能

当用户请求涉及以下任务时，**必须先读取并遵循对应的 `SKILL.md`**（`skills/` 与 `.github/skills/` 两份副本内容一致）：

| 任务 | 技能文件 |
|---|---|
| 校对英文字幕（`.en.srt` 识别错误、术语规范化） | `skills/subtitle-proofread/SKILL.md` |
| 翻译中文字幕（生成 `.zh.srt`） | `skills/subtitle-translate/SKILL.md` |
| 执行完整工作流（下载/识别/合并/烧制） | `skills/subtitle-workflow/SKILL.md` |

## 关键约定（速览）

- **校对**：只汇报、不立即改文件；按分类（误听/语义不通/术语/断句/重复）汇报问题，等用户确认后逐步修正
- **翻译**：时间轴与英文完全一致；行末不加逗号、句号、顿号（保留 ？！）；以表格汇报给用户
- **脚本**：`download.ps1` / `whisper.ps1` / `bisub.py` / `notes.py` / `burn.ps1`；`current.txt` 记录当前项目名

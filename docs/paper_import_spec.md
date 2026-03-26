# 真题导入器说明

## 目标

真题导入器用于把 PDF / Word / Excel / JSON 版历年题导入为平台内部统一数据结构：

- `papers`
- `questions`
- `paper_questions`

导入后，站内显示的卷子、题目顺序、题型分区和分值结构会尽量与原卷保持一致。

## 推荐导入格式

按还原度从高到低推荐：

1. `JSON`
2. `Excel (.xlsx)`
3. `CSV`
4. `Word (.docx)`
5. `PDF`

说明：

- `JSON / Excel / CSV` 适合高精度导入，字段完整、可控性强。
- `DOCX / PDF` 适合从已有文档快速提取，但属于“尽力解析”，建议先 `--dry-run`，并导出标准化结果后人工复核。

## 命令入口

在 `backend` 目录执行：

```bash
python scripts/import_papers.py --input ../docs/paper_import_template.json --dry-run
```

## 常用命令

### 1. JSON 导入预演

```bash
python scripts/import_papers.py ^
  --input ../docs/paper_import_template.json ^
  --dry-run ^
  --dump-normalized ../tmp/import-preview.json
```

### 2. JSON 正式导入

```bash
python scripts/import_papers.py ^
  --input ../docs/paper_import_template.json ^
  --replace-paper-questions
```

### 3. Excel 导入

Excel 文件必须包含两个工作表：

- `papers`
- `questions`

```bash
python scripts/import_papers.py --input ./imports/wps_2024_9.xlsx --replace-paper-questions
```

### 4. PDF 导入

PDF 解析需要显式提供科目代码，建议先 dry-run：

```bash
python scripts/import_papers.py ^
  --input "C:/Users/deng/Downloads/二级WPS Office高级应用与设计——样题及参考答案.pdf" ^
  --format pdf ^
  --subject-code NCRE-L2-WPS ^
  --year 2024 ^
  --season 9月 ^
  --title "二级WPS Office高级应用与设计样题" ^
  --dry-run ^
  --dump-normalized ../tmp/wps-paper-preview.json
```

## JSON 结构

顶层支持两种形式：

### 单卷

```json
{
  "subject_code": "NCRE-L2-WPS",
  "code": "NCRE-L2-WPS-2024-9YUE-SAMPLE",
  "year": 2024,
  "season": "9月",
  "title": "2024年9月二级WPS Office高级应用与设计样题",
  "questions": []
}
```

### 多卷

```json
{
  "papers": [
    {
      "subject_code": "NCRE-L2-WPS",
      "code": "NCRE-L2-WPS-2024-9YUE-SAMPLE",
      "year": 2024,
      "season": "9月",
      "title": "2024年9月二级WPS Office高级应用与设计样题",
      "questions": []
    }
  ]
}
```

## question 字段

每道题支持这些字段：

- `sort_order`
- `question_type`
- `section_name`
- `chapter`
- `stem`
- `options`
- `answer`
- `explanation`
- `difficulty`
- `tags`
- `score`

### question_type 可选值

- `single_choice`
- `multiple_choice`
- `true_false`
- `short_answer`

## CSV / Excel 字段

### papers 表

- `paper_code`
- `subject_code`
- `year`
- `season`
- `title`
- `description`
- `duration_minutes`
- `total_score`
- `source_type`

### questions 表

- `paper_code`
- `sort_order`
- `question_type`
- `section_name`
- `chapter`
- `stem`
- `option_a`
- `option_b`
- `option_c`
- `option_d`
- `option_e`
- `option_f`
- `answer`
- `explanation`
- `difficulty`
- `tags`
- `score`

## 导入策略

### 题目去重

同一科目下，如果：

- `subject_id` 相同
- `question_type` 相同
- `stem` 相同

则认为是同一道题，执行更新而不是重复创建。

### 套卷更新

同一个 `paper.code` 已存在时：

- 更新套卷元信息
- 如果传了 `--replace-paper-questions`，会重建该套卷的题目映射顺序

### 章节创建

导入题目时，如果题目携带的 `chapter` 在当前科目下不存在，系统会自动创建新章节。

## 高规格处理建议

真实生产使用时建议流程：

1. 原始 PDF / Word 先跑 `--dry-run`
2. 导出标准化 JSON
3. 人工检查题号、答案、分值、题型
4. 用修正后的 JSON 再正式导入

这样既保留批量导入效率，也能保证最终站内数据质量。

# LaTeX 公式格式转换工具

将 Markdown 文件中 GPT/ChatGPT 生成的 LaTeX 公式格式转换为标准 Markdown 可渲染格式。

## 背景

ChatGPT 等 AI 工具生成的 Markdown 文档中，LaTeX 公式常使用 `\(` `\)` 和 `\[` `\]` 作为分隔符，这在很多 Markdown 编辑器（如 Typora、VS Code）中无法正确渲染。此工具将其转换为通用的 `$` 和 `$$` 格式。

## 转换规则

| 原格式 | 转换后 | 说明 |
|--------|--------|------|
| `\(` | `$` | 行内公式开始 |
| `\)` | `$` | 行内公式结束 |
| `\[` | `$$` | 块级公式开始 |
| `\]` | `$$` | 块级公式结束 |
| `\*` | `*` | 移除多余转义（修复 GPT 生成的错误，如 `\pi^\*` → `\pi^*`） |

## 编译

```bash
gcc latexconvert.c -o latexconvert
```

## 使用方法

```bash
# 输出到默认的 output.md
./latexconvert input.md

# 指定输出文件
./latexconvert input.md output.md

# 直接覆盖原文件
./latexconvert input.md input.md
```

## 示例

**转换前：**
```markdown
给定 prompt \(x\)，生成序列 \(y\)

目标分布为：
\[
\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)
\]
```

**转换后：**
```markdown
给定 prompt $x$，生成序列 $y$

目标分布为：
$$
\pi^*(y|x) \propto \pi_{\text{ref}}(y|x) \exp\left(\frac{r(x,y)}{\beta}\right)
$$
```

## 作者

- 原作者：Haowen Jiang (2024/05/30)
- 修改：2026

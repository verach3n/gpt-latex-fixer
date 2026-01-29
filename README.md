# LaTeX Formula Converter

A lightweight C utility to convert LaTeX formula delimiters in Markdown files, making ChatGPT/AI-generated mathematical formulas display correctly in standard Markdown renderers.

## Problem

ChatGPT and other AI models often output LaTeX formulas using `\( \)` for inline math and `\[ \]` for block math. However, many Markdown renderers (GitHub, VSCode, Obsidian, etc.) expect `$ $` and `$$ $$` syntax instead.

## Solution

This tool converts:

| From | To | Type |
|------|-----|------|
| `\(` ... `\)` | `$` ... `$` | Inline math |
| `\[` ... `\]` | `$$` ... `$$` | Block math |
| `\*` | `*` | Remove unnecessary escape |

## Building

```bash
# Linux/macOS
gcc -o latexconvert latexconvert.c

# Windows (MinGW)
gcc -o latex.exe latexconvert.c
```

## Usage

```bash
# Basic usage (outputs to output.md)
./latexconvert input.md

# Specify output file
./latexconvert input.md converted.md
```

## Example

**Input:**
```markdown
The quadratic formula is \( x = \frac{-b \pm \sqrt{b^2-4ac}}{2a} \).

The Euler's identity:
\[
e^{i\pi} + 1 = 0
\]
```

**Output:**
```markdown
The quadratic formula is $ x = \frac{-b \pm \sqrt{b^2-4ac}}{2a} $.

The Euler's identity:
$$
e^{i\pi} + 1 = 0
$$
```

## Pre-built Binaries

- `latexconvert` - Linux binary
- `latex.exe` - Windows binary

## Author

- Haowen Jiang
- Original: May 30, 2024
- Modified: 2026

## License

MIT

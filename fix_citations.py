#!/usr/bin/env python3
"""
修复GPT深度思考模式生成的markdown文件中丢失的引用信息
Author: Based on gpt.pdf reference extraction
Date: 2026

功能：
1. 从PDF文件提取参考文献列表
2. 将markdown中的 citeturn... 格式替换为可读的脚注引用
3. 在文档末尾添加完整的参考文献部分
"""

import re
import sys
import fitz  # PyMuPDF


def extract_references_from_pdf(pdf_path):
    """从PDF文件提取参考文献列表
    
    PDF格式：参考文献页面包含 标题+URL 对，后面可能有编号列表
    
    返回两个结果：
    - references_list: 按顺序出现的参考文献列表 [(title, url), ...]
    - references_by_num: 按顺序编号的字典 {1: (title, url), 2: (title, url), ...}
    """
    doc = fitz.open(pdf_path)
    
    # 找到包含URL的页面（参考文献页面）
    full_text = ""
    total_pages = len(doc)
    for i in range(total_pages):
        page_text = doc[i].get_text()
        # 参考文献页面包含URL
        if 'http' in page_text:
            full_text += page_text + "\n"
    
    references_list = []  # 按顺序的参考文献列表
    
    lines = full_text.split('\n')
    i = 0
    current_title_parts = []
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 跳过空行
        if not line:
            i += 1
            continue
        
        # 跳过纯数字行（编号）
        if line.isdigit():
            i += 1
            continue
        
        # 如果是 URL 行
        if line.startswith('http'):
            url = line
            title = ' '.join(current_title_parts) if current_title_parts else url
            
            # 添加到列表（避免重复）
            if not any(ref[1] == url for ref in references_list):
                references_list.append((title, url))
            
            current_title_parts = []
            i += 1
        else:
            # 标题行（可能是多行标题的一部分）
            current_title_parts.append(line)
            i += 1
    
    # 创建按顺序编号的字典
    references_by_num = {i+1: ref for i, ref in enumerate(references_list)}
    
    return references_list, references_by_num


def parse_citation_pattern(citation_str):
    """解析 citeturn14search0turn25view0 格式的引用"""
    # 提取所有 turnXXsearchY 或 turnXXviewY 模式
    patterns = re.findall(r'turn(\d+)(search|view)(\d+)', citation_str)
    return patterns


def read_markdown(md_path):
    """读取markdown文件"""
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_markdown(md_path, content):
    """写入markdown文件"""
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)


def fix_citations(md_content, references_by_num):
    """修复markdown中的引用格式，生成可点击的链接"""
    
    # 先移除GPT内部使用的特殊Unicode字符 (Private Use Area)
    # \ue202 和 \ue201 是GPT用于标记引用的内部字符
    md_content = md_content.replace('\ue202', '').replace('\ue201', '')
    
    # 匹配 cite 后跟多个 turnXX[search|view]Y 的模式
    citation_pattern = r'cite((?:turn\d+(?:search|view)\d+)+)'
    
    # 用于跟踪已使用的引用
    used_refs = set()
    ref_counter = [0]  # 使用列表以便在闭包中修改
    citation_map = {}  # 映射原始引用字符串到新的链接格式
    
    def replace_citation(match):
        full_match = match.group(0)
        
        if full_match in citation_map:
            # 已经处理过的引用
            return citation_map[full_match]
        
        # 解析引用中的所有turn-search/view模式
        patterns = parse_citation_pattern(full_match)
        
        if not patterns:
            return full_match
        
        # 生成可点击的链接
        links = []
        for turn_num, ref_type, idx in patterns:
            ref_counter[0] += 1
            ref_num = ref_counter[0]
            used_refs.add(ref_num)
            
            # 如果有对应的参考文献，直接链接到URL
            if ref_num in references_by_num:
                title, url = references_by_num[ref_num]
                # 使用上标格式的可点击链接 <sup>[1]</sup>
                links.append(f'<sup>[[{ref_num}]]({url})</sup>')
            else:
                # 没有对应参考文献时，链接到文档末尾的参考文献部分
                links.append(f'<sup>[[{ref_num}]](#ref-{ref_num})</sup>')
        
        # 创建新的引用格式：多个链接用逗号分隔
        new_citation = ''.join(links)
        citation_map[full_match] = new_citation
        
        return new_citation
    
    # 替换所有引用
    fixed_content = re.sub(citation_pattern, replace_citation, md_content)
    
    return fixed_content, used_refs, ref_counter[0]


def create_references_section(references_list, references_by_num):
    """创建参考文献部分，包含可点击的链接
    
    每个参考文献条目包含：
    - 锚点ID（用于文档内跳转）
    - 标题（可点击链接到原始URL）
    """
    section = "\n\n---\n\n## 参考文献\n\n"
    
    # 按编号排序输出
    if references_by_num:
        sorted_nums = sorted(references_by_num.keys())
        for num in sorted_nums:
            title, url = references_by_num[num]
            # 添加锚点ID，标题作为可点击链接
            section += f'<a id="ref-{num}"></a>\n'
            section += f"**[{num}]** [{title}]({url})\n\n"
    else:
        # 如果没有编号，按顺序输出
        for i, (title, url) in enumerate(references_list, 1):
            section += f'<a id="ref-{i}"></a>\n'
            section += f"**[{i}]** [{title}]({url})\n\n"
    
    return section


def main():
    if len(sys.argv) < 2:
        print("用法: python fix_citations.py <markdown文件> [pdf文件] [输出文件]")
        print("  如果不指定pdf文件，将使用同目录下的gpt.pdf")
        print("  如果不指定输出文件，将输出到 fixed_<原文件名>")
        return 1
    
    md_path = sys.argv[1]
    
    # 确定PDF路径
    if len(sys.argv) >= 3:
        pdf_path = sys.argv[2]
    else:
        import os
        pdf_path = os.path.join(os.path.dirname(md_path), 'gpt.pdf')
    
    # 确定输出路径
    if len(sys.argv) >= 4:
        output_path = sys.argv[3]
    else:
        import os
        dir_name = os.path.dirname(md_path)
        base_name = os.path.basename(md_path)
        output_path = os.path.join(dir_name, f"fixed_{base_name}")
    
    print(f"读取markdown文件: {md_path}")
    md_content = read_markdown(md_path)
    
    print(f"从PDF提取参考文献: {pdf_path}")
    references_list, references_by_num = extract_references_from_pdf(pdf_path)
    print(f"  提取到 {len(references_list)} 个参考文献条目")
    print(f"  其中 {len(references_by_num)} 个有编号映射")
    
    print("修复引用格式...")
    fixed_content, used_refs, total_refs = fix_citations(md_content, references_by_num)
    print(f"  共处理 {total_refs} 个引用标记")
    
    # 添加参考文献部分
    print("添加参考文献列表...")
    fixed_content += create_references_section(references_list, references_by_num)
    
    print(f"写入输出文件: {output_path}")
    write_markdown(output_path, fixed_content)
    
    print("完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

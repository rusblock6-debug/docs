import re
import os
from datetime import datetime
import pypandoc

def filter_tz(input_file, output_dir, tag):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    filtered_lines = []
    in_section = False
    current_section_has_tag = False

    for line in lines:
        if line.startswith('##'):
            tags_in_line = re.findall(r'\[(.*?)\]', line)
            if tags_in_line:
                current_section_has_tag = any(tag in [x.strip() for x in t.split(',')] for t in tags_in_line)
                if current_section_has_tag:
                    line_without_tags = re.sub(r'\s*\[.*?\]', '', line)
                    filtered_lines.append(line_without_tags)
                in_section = True
            else:
                in_section = False
        else:
            if in_section and current_section_has_tag:
                filtered_lines.append(line)
            elif not in_section:
                filtered_lines.append(line)

    all_tags = [t.strip() for line in lines if line.startswith('##') for t in re.findall(r'\[(.*?)\]', line)]
    if tag not in sum([t.split(',') for t in all_tags], []):
        raise ValueError(f"Нет контента для тега '{tag}'")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- Markdown ---
    output_md = os.path.join(output_dir, f'dic_{tag}.md')
    with open(output_md, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    # --- PDF ---
    output_pdf = os.path.join(output_dir, f'dic_{tag}_{datetime.now().strftime("%Y-%m-%d")}.pdf')
    pypandoc.convert_file(
        output_md, 'pdf',
        outputfile=output_pdf,
        extra_args=[
            '--pdf-engine=xelatex',
            '--toc',
            '--toc-depth=2',
            '-V', 'mainfont=Times New Roman',
            '-V', 'geometry:margin=2cm',
            '-V', 'parskip=0pt',
            '-V', 'fontsize=12pt'
        ]
    )

    # --- HTML ---
    output_html = os.path.join(output_dir, f'dic_{tag}.html')
    pypandoc.convert_file(
        output_md, 'html',
        outputfile=output_html,
        extra_args=[
            '--toc',           # оглавление
            '--toc-depth=2',
        ]
    )

    return output_pdf, output_html  # возвращаем оба пути

def main():
    input_file = '../dic.md'
    output_dir = '../output'
    tags = ['innerl', 'customer']
    
    for tag in tags:
        try:
            pdf_path, html_path = filter_tz(input_file, output_dir, tag)
            print(f'Сгенерирован PDF: {pdf_path}')
            print(f'Сгенерирован HTML: {html_path}')
        except ValueError:
            print(f"Пропущен тег '{tag}' — нет контента.")

if __name__ == '__main__':
    main()

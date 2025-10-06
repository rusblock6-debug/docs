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

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # --- Markdown ---
    output_md = os.path.join(output_dir, f'{base_name}_{tag}.md')
    with open(output_md, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    # --- DOCX ---
    output_docx = os.path.join(output_dir, f'{base_name}_{tag}.docx')
    pypandoc.convert_file(
        output_md, 'docx',
        outputfile=output_docx,
        extra_args=['--toc', '--toc-depth=2']
    )

    # --- PDF ---
    output_pdf = os.path.join(output_dir, f'{base_name}_{tag}_{datetime.now().strftime("%Y-%m-%d")}.pdf')
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
    output_html = os.path.join(output_dir, f'{base_name}_{tag}.html')
    pypandoc.convert_file(
        output_md, 'html',
        outputfile=output_html,
        extra_args=['--toc', '--toc-depth=2']
    )

    return output_docx, output_pdf, output_html


def process_folder(input_folder, output_dir, tags=['innerl', 'customer']):
    if not os.path.exists(input_folder):
        print(f"Папка не найдена: {input_folder}")
        return

    md_files = [f for f in os.listdir(input_folder) if f.endswith('.md')]
    if not md_files:
        print(f"Нет .md файлов в папке: {input_folder}")
        return

    for filename in md_files:
        file_path = os.path.join(input_folder, filename)
        print(f'\nОбрабатываем: {file_path}')
        for tag in tags:
            try:
                docx_path, pdf_path, html_path = filter_tz(file_path, output_dir, tag)
                print(f'  DOCX: {docx_path}')
                print(f'  PDF: {pdf_path}')
                print(f'  HTML: {html_path}')
            except ValueError:
                print(f'  Пропущен тег "{tag}" — нет контента.')


if __name__ == '__main__':
    input_folder = r'D:\Project\Learn\rus_eng'  # папка с md файлами
    output_dir = r'D:\Project\Learn\output'     # куда складываем результаты
    process_folder(input_folder, output_dir)

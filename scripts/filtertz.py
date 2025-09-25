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
                # Проверяем наличие нужного тега
                current_section_has_tag = any(tag in [x.strip() for x in t.split(',')] for t in tags_in_line)
                if current_section_has_tag:
                    # Убираем теги из заголовка перед добавлением
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

    # Проверка, что для данного тега есть контент
    all_tags = [t.strip() for line in lines if line.startswith('##') for t in re.findall(r'\[(.*?)\]', line)]
    if tag not in sum([t.split(',') for t in all_tags], []):
        raise ValueError(f"Нет контента для тега '{tag}'")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_md = os.path.join(output_dir, f'dic_{tag}.md')
    with open(output_md, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)

    output_pdf = os.path.join(output_dir, f'dic_{tag}_{datetime.now().strftime("%Y-%m-%d")}.pdf')
    
    # Конвертация Markdown -> PDF через Pandoc/XeLaTeX
    pypandoc.convert_file(
        output_md, 'pdf',
        outputfile=output_pdf,
        extra_args=[
            '--pdf-engine=xelatex',
            '--toc',                      # включаем оглавление
            '--toc-depth=2',              # берём только ## (уровень 2)
            '-V', 'mainfont=Times New Roman',
            '-V', 'geometry:margin=2cm',
            '-V', 'parskip=0pt',
            '-V', 'fontsize=12pt'
        ]
    )
    return output_pdf

def check_tags(input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    untagged = [line for line in lines if line.startswith('##') and not re.search(r'\[(innerl|customer)(,.*?)?\]', line)]
    if untagged:
        print("Секции без тегов:")
        for line in untagged:
            print(line.strip())
        return False
    return True

def main():
    input_file = '../dic.md'
    output_dir = '../output'
    tags = ['innerl', 'customer']
    
    if not check_tags(input_file):
        print("Добавьте теги для всех секций!")
    
    for tag in tags:
        try:
            pdf_path = filter_tz(input_file, output_dir, tag)
            print(f'Сгенерирован файл: {pdf_path}')
        except ValueError:
            print(f"Пропущен тег '{tag}' — нет контента.")

if __name__ == '__main__':
    main()

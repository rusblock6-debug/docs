import re

# Путь к исходному файлу
input_file = r'D:\Project\Learn\rus_eng\English to Russian.md'
# Путь к выходному файлу
output_file = r'D:\Project\Learn\rus_eng\English to Russian_clean.md'

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []

for i, line in enumerate(lines):
    # ищем строки вида ## term [tag1, tag2]
    match = re.match(r'## (.+?) \[.*?\]', line)
    if match:
        term = match.group(1).strip()
        # предполагаем, что следующая строка — перевод/описание
        translation = ''
        if i + 1 < len(lines):
            translation = lines[i + 1].strip()
        if translation:
            output_lines.append(f'## {term}\n{translation}\n\n')

# Записываем результат
with open(output_file, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f'Готово! Чистый словарь сохранён в {output_file}')

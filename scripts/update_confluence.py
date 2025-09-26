import requests
from requests.auth import HTTPBasicAuth
import json
import re

# ===== Загружаем секреты =====
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

email = secrets["email"]
api_token = secrets["api_token"]

# ===== Параметры =====
confluence_url = "https://rusblock6.atlassian.net/wiki"
space_key = "MFS"
page_title = "Словарь АСУ ГТК для клиента"
file_path = "dic_inner.HTML"

# ===== Чтение Markdown =====
with open(file_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# ===== Конвертация Markdown -> HTML =====
entries = re.split(r"\n## ", md_content)
html_parts = []

for entry in entries:
    if not entry.strip():
        continue
    lines = entry.strip().split("\n", 1)
    header = lines[0].strip()
    body = lines[1].strip() if len(lines) > 1 else ""

    html_parts.append(f"<h2>{header}</h2>")
    html_parts.append(f"<p>{body}</p>")

html_content = "\n".join(html_parts)

# ===== Проверка существующей страницы =====
search_url = f"{confluence_url}/rest/api/content"
params = {"title": page_title, "spaceKey": space_key, "expand": "version"}
response = requests.get(search_url, params=params, auth=HTTPBasicAuth(email, api_token))

if response.status_code != 200:
    print(f"Ошибка при поиске страницы: {response.status_code}")
    print(response.text)
    exit()

data = response.json()
if data["size"] > 0:
    # Страница есть → обновляем
    page_id = data["results"][0]["id"]
    version_number = data["results"][0]["version"]["number"] + 1

    update_url = f"{confluence_url}/rest/api/content/{page_id}"
    payload = {
        "id": page_id,
        "type": "page",
        "title": page_title,
        "space": {"key": space_key},
        "body": {"storage": {"value": html_content, "representation": "storage"}},
        "version": {"number": version_number},
    }

    r = requests.put(
        update_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(email, api_token),
    )

    if r.status_code in [200, 201]:
        print("✅ Страница успешно обновлена!")
    else:
        print(f"❌ Ошибка при обновлении: {r.status_code}")
        print(r.text)

else:
    # Страницы нет → создаём
    create_url = f"{confluence_url}/rest/api/content/"
    payload = {
        "type": "page",
        "title": page_title,
        "space": {"key": space_key},
        "body": {"storage": {"value": html_content, "representation": "storage"}},
    }

    r = requests.post(
        create_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        auth=HTTPBasicAuth(email, api_token),
    )

    if r.status_code in [200, 201]:
        print("✅ Страница успешно создана!")
    else:
        print(f"❌ Ошибка при создании страницы: {r.status_code}")
        print(r.text)

import os
import json
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup  # pip install beautifulsoup4

# ===== Загружаем переменные из .env =====
load_dotenv()

email = os.getenv("CONFLUENCE_EMAIL")
api_token = os.getenv("CONFLUENCE_TOKEN")

if not email or not api_token:
    print("❌ Ошибка: переменные CONFLUENCE_EMAIL и CONFLUENCE_TOKEN не заданы")
    exit()

# ===== Общие параметры =====
confluence_url = "https://rusblock6.atlassian.net/wiki"
space_key = "MFS"

# ===== Папка с HTML-файлами =====
html_folder = r"D:\Project\Learn\output"

# ===== Функция преобразования HTML в красивую таблицу =====
def html_to_table(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    rows = []

    for h2 in soup.find_all("h2"):
        header_text = h2.get_text(strip=True)
        term = header_text
        tags = ""

        if "[" in header_text and "]" in header_text:
            term = header_text.split("[")[0].strip()
            tags = header_text.split("[")[1].split("]")[0]

        p = h2.find_next_sibling("p")
        body = p.get_text(strip=True) if p else ""

        row = f"<tr><td style='width:20%; padding:4px; border-bottom:1px solid #ccc; vertical-align:top;'><strong>{term}</strong></td><td style='width:80%; padding:4px; border-bottom:1px solid #ccc;'>{body}<span style='display:none'>{tags}</span></td></tr>"
        rows.append(row)

    html_table = f"""
    <div style="max-width:600px; margin:0 auto;">
    <table style="width:80%; border-collapse: collapse; table-layout: fixed;">
      <thead>
        <tr>
          <th style="text-align:left; border-bottom:2px solid #000; padding:6px; width:25%;">Термин</th>
          <th style="text-align:left; border-bottom:2px solid #000; padding:6px; width:75%;">Описание</th>
        </tr>
      </thead>
      <tbody>
        {"".join(rows)}
      </tbody>
    </table>
    </div>
    """
    return html_table

# ===== Обработка всех HTML-файлов в папке =====
for filename in os.listdir(html_folder):
    if not filename.endswith(".html"):
        continue

    html_file_path = os.path.join(html_folder, filename)
    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_to_table(html_content)
    page_title = os.path.splitext(filename)[0]  # имя файла без расширения

    # проверка существующей страницы
    search_url = f"{confluence_url}/rest/api/content"
    params = {"title": page_title, "spaceKey": space_key, "expand": "version"}
    response = requests.get(search_url, params=params, auth=HTTPBasicAuth(email, api_token))

    if response.status_code != 200:
        print(f"❌ Ошибка при поиске страницы: {response.status_code}")
        continue

    data = response.json()
    if data["size"] > 0:
        # обновление страницы
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
            print(f"✅ Страница обновлена: {page_title}")
        else:
            print(f"❌ Ошибка при обновлении ({page_title}): {r.status_code}")
            print(r.text)
    else:
        # создание страницы
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
            print(f"✅ Страница создана: {page_title}")
        else:
            print(f"❌ Ошибка при создании ({page_title}): {r.status_code}")
            print(r.text)

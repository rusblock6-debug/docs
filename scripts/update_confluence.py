import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json
import re

load_dotenv()

email = os.getenv("CONFLUENCE_EMAIL")
api_token = os.getenv("CONFLUENCE_TOKEN")

if not email or not api_token:
    print("❌ Ошибка: переменные CONFLUENCE_EMAIL и CONFLUENCE_TOKEN не заданы")
    exit()

confluence_url = "https://rusblock6.atlassian.net/wiki"
space_key = "MFS"

pages = [
    {"title": "Словарь АСУ ГТК для внутреннего пользователя", "html_file_path": r"C:\docs\output\dic_innerl.html"},
    {"title": "Словарь АСУ ГТК для клиента", "html_file_path": r"C:\docs\output\dic_customer.html"}
]

def upload_page(title, html_file_path):
    if not os.path.exists(html_file_path):
        print(f"❌ HTML не найден: {html_file_path}")
        return

    with open(html_file_path, "r", encoding="utf-8") as f:
        html_content = f.read()


    html_content = re.sub(r'style="[^"]*text-align:[^"]*"', '', html_content)
    
    html_content = re.sub(r'<p([^>]*)>', r'<p\1 align="left">', html_content)
    html_content = re.sub(r'<h([1-6])([^>]*)>', r'<h\1\2 align="left">', html_content)

       search_url = f"{confluence_url}/rest/api/content"
    params = {"title": title, "spaceKey": space_key, "expand": "version"}
    response = requests.get(search_url, params=params, auth=HTTPBasicAuth(email, api_token))

    if response.status_code != 200:
        print(f"❌ Ошибка при поиске страницы '{title}': {response.status_code}")
        print(response.text)
        return

    data = response.json()
    if data["size"] > 0:
        page_id = data["results"][0]["id"]
        version_number = data["results"][0]["version"]["number"] + 1

        update_url = f"{confluence_url}/rest/api/content/{page_id}"
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
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
            print(f"✅ Страница '{title}' успешно обновлена!")
        else:
            print(f"❌ Ошибка при обновлении '{title}': {r.status_code}")
            print(r.text)

    else:
        create_url = f"{confluence_url}/rest/api/content/"
        payload = {
            "type": "page",
            "title": title,
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
            print(f"✅ Страница '{title}' успешно создана!")
        else:
            print(f"❌ Ошибка при создании '{title}': {r.status_code}")
            print(r.text)

for page in pages:
    upload_page(page["title"], page["html_file_path"])

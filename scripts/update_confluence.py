import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
import json
import re

# Загружаем переменные окружения
load_dotenv()

confluence_url = 'https://rusblock6.atlassian.net/wiki'
space_key = 'MFS'
page_title = 'Словарь АСУ ГТК для клиента'
file_path = '../dic_customer.html'

email = os.getenv("EMAIL")
api_token = os.getenv("API_TOKEN")

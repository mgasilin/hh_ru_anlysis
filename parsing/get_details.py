import json
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import logging


def get_info_by_vacancies_urls(input_path = 'new_links.json', output_path = 'vacancies_details.json'):
    
    data=[] 

    #Считываем вакансии, полученные селениумом без описаний
    #Если файл есть и он пустой, то json.load() упадет с ошибкой, так как не найдет ( или {, поэтому проверяем не только наличие, но и размер файла
    if os.path.exists(input_path) and os.stat(input_path).st_size>0:
        with open(input_path, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
            raw_vacancies = input_data["vacancies"]
            logger.debug("Файл для чтения найден, данные загружены")
    else:
        logger.error("Файл для чтения не найден")

    #Проверяем есть у нас уже файл с записями, чтобы продолжить с места последней записи, при закрытии программы или ошибки
    #Если файл есть и он пустой, то json.load() упадет с ошибкой, так как не найдет ( или {, поэтому проверяем не только наличие, но и размер файла
    if os.path.exists(output_path) and os.stat(output_path).st_size>0:
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            if loaded_data:
                data = loaded_data
            logger.debug("Файл для записи найден, загружены начальные данные")
    else:
        logger.debug("Файл для записи не найден")

    session = requests.Session()

    saved_ids = set([x["id"] for x in data])

    try:
        for item in raw_vacancies:
            if item["id"] in saved_ids:
                continue
            
            details={
                "id": item["id"],
                'query': item["query"],
                "title": item["title"],
                "company": "",
                "salary": "Не указана",
                "description": "",
                "skills": [],
                "link": item["link"]
            }

            try: 
                response = session.get(item["link"], headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")

                    description = soup.find("div", {"data-qa": "vacancy-description"})
                    if description:
                        details["description"] = description.get_text(separator=" ", strip=True)

                    skills = soup.find_all(attrs={"data-qa": "skills-element"})
                    if skills:
                        details["skills"] = [x.get_text(separator=" ", strip=True) for x in skills]
                    
                    salary = soup.find(attrs={"data-qa": "vacancy-salary"})
                    if salary:
                        details["salary"] = salary.get_text(separator=" ",strip=True)

                    company = soup.find(attrs={"data-qa": "vacancy-company-name"}) 
                    if company:
                        details["company"] = company.get_text(separator=" ",strip=True)   

                    data.append(details)

                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)

                    time.sleep(random.uniform(2, 4))

                else:
                    logger.debug(f"Доступ запрещен или страница не найдена, стутус {response.status_code}")
                    time.sleep(60)

            except:
                logger.error(f"Запрос не прошёл")
        
        logger.debug("Загрузка завершена")
        return

    except:
        logger.error("Загрузка прервана")
        return





# Инициализация логгера
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

dh = logging.FileHandler('debug.log', encoding='utf-8')
dh.setLevel(logging.DEBUG)

eh = logging.FileHandler('error.log', encoding='utf-8')
eh.setLevel(logging.ERROR)

# Указываем время работы, название модуля, уровень логов и сообщение при отрабатывании
formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
dh.setFormatter(formatter)
eh.setFormatter(formatter)

logger.addHandler(eh)
logger.addHandler(dh)

#Чтобы hh не забанил и не выдал 403 на каждой вакансии введем браузерные хедеры
#User-agent брал из своего браузера когда делал запрос по одной вакансии вручную
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36 Edg/146.0.0.0',
    'Accept-Language':'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
}
get_info_by_vacancies_urls()
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
import json
import os
import logging


def parser_selenium(output_path = "new_links.json", queries = ["python+разработчик", "java+разработчик", 
    "go+разработчик", "data+scientist","javascript-разработчик","программист+c++",
    "c#+разработчик", "dotnet+developer",
    "php+разработчик", "php+developer",
    "javascript+разработчик", "frontend+developer",
    "react+разработчик", "angular+разработчик", "vue+разработчик",
    "node.js+разработчик", "backend+developer",
    "ruby+разработчик", "rust+разработчик",
    "ios+разработчик", "android+разработчик", "kotlin+developer",
    "swift+developer", "flutter+developer", "ml+engineer",
    "machine+learning+engineer", "nlp+разработчик",
    "computer+vision+engineer", "cv+разработчик",
    "data+engineer", "инженер+данных",
    "ai+developer", "deep+learning+engineer",
    "mlops+engineer", "разработчик+нейросетей"]):

    data = {
        "last_query_index":0,
        "last_page":0,
        "vacancies":[]
    }

    #Проверяем есть у нас уже файл с записями, чтобы продолжить с места последней записи, при закрытии программы или ошибки
    #Если файл есть и он пустой, то json.load() упадет с ошибкой, так как не найдет ( или {, поэтому проверяем не только наличие, но и размер файла
    if os.path.exists(output_path) and os.stat(output_path).st_size>0:
        with open(output_path, 'r', encoding='utf-8') as f:
            loaded_data=json.load(f)
            if loaded_data:
                data = loaded_data
                logger.debug("Файл для записи найден, загружены начальные данные")
            else:
                logger.error("Файл для записи пустой или в другом формате")
    else:
        logger.debug("Файл для записи не найден")

    #Индексация такая: id - сквозной для всех вакансий, page - для каждого запроса, чтобы сохранять последнюю страницу и начинать с last_page+1 в следующий раз
    id = len(data["vacancies"]) + 1
    page = data["last_page"]
    
    for query_index in range(data["last_query_index"], len(queries)):

        current_query = queries[query_index]
        data["last_query_index"] = query_index
        data["last_page"] = page
            
        #Так как не знаем сколько страниц на каждом запросе, то просто парсим, пока не упремся в отсутствие вакансий на странице (там будет и отсутствие селектора) 
        while True:                
            #Формируем адрес запроса, если первая страница, то параметр page не нужен
            url=f"https://hh.ru/vacancies?text={current_query}&page={page}" if page>0 else f"https://hh.ru/vacancies?text={current_query}"
            driver.get(url)
                
            #После задержки скроллим в самый низ страницы, чтобы прогрузился весь контент на странице
            time.sleep(random.uniform(3, 5))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(random.uniform(0.9, 1.1))
            vacancies=driver.find_elements(By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"]')
            if not vacancies:
                page = 0
                break 

            for v in vacancies:
                try:
                    title = v.find_element(By.CSS_SELECTOR, '[data-qa="serp-item__title"]')
                    link = title.get_attribute('href')
                    data["vacancies"].append({
                            'id':id,
                            'query':current_query,
                            'title':title.text,
                            'link':link,
                            'page':page
                        })
                    id += 1
                except:
                    continue

            page += 1 
                
            #Сохраняем прогресс в файл, сразу в читаемом формате, чтобы видеть результат нормально
            with open(output_path, 'w', encoding = 'utf-8') as f:
                json.dump(data, f, indent = 4, ensure_ascii = False)
                logger.debug(f"Данные по запросу {current_query} со страницы {page} сохранены")

            time.sleep(random.uniform(2,4))

    driver.quit()

# Инициализация логгера
logger = logging.getLogger(__name__)
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

#Нужно указать свою версию Chrome, у меня 146, базовая 147 вроде
driver = uc.Chrome(version_main = 146) 
parser_selenium(output_path = "new_links.json")

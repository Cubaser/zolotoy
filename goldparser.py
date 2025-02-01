import logging
import os
import re
import requests
from datetime import datetime as dt

import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    filename='goldparser.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

HEADERS = {
        "x-qa-client-type": os.getenv('X_QA_CLIENT_TYPE'),
        "x-qa-region": os.getenv('X_QA_REGION'),
}

URLS = [os.getenv('BRACELET_URL'), os.getenv('CHAIN_URL')]
TYPE_GOLD = ['BRACELET', 'CHAIN']


def gold_parse(choose_url):

    os.makedirs('result', exist_ok=True)
    data_out = []
    items_on_page = 0
    items_in_itersble = 0
    items_all_size = 0
    page_num = 1

    while True:
        url = f"https://www.585zolotoy.ru/api/v3/products/?category={URLS[choose_url]}=1&page={page_num}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        items = data.get('results')

        logging.info(f'Страница: {page_num}')

        for item in items:
            item_link = re.search(
                r'https?://[^\s]+', item.get('share_text')
            )[0]
            item_article = re.search(r'/(\d+)/$', item.get('share_text'))
            item_url = f'https://www.585zolotoy.ru/api/v3/products{item_article[0]}'
            response_item = requests.get(item_url, headers=HEADERS)
            item = response_item.json()
            properties = item.get('properties_by_size')
            items_in_itersble += 1
            try:
                for propertie in properties:
                    items_all_size += 1
                    values = propertie.get('properties')
                    price = propertie.get('price')
                    size = propertie.get('size')
                    value = values[2].get('values')
                    prob = value[0][1].get('value')[0]
                    weight = \
                    re.search(
                        r'(\d+(?:\.\d+)?)', value[0][2].get('value')[0]
                    )[0]

                    add_data = {
                        'Ссылка': item_link,
                        'Размер': size,
                        'Вес': weight,
                        'Проба': prob,
                        }

                    if price is not None:
                        add_data['Цена'] = price
                        add_data['Цена за грамм'] = round(
                            float(price) / float(weight), 2
                        )
                    data_out.append(add_data)

            except Exception as error:
                logging.error('*' * 30)
                logging.error(f'Возникло исключение :{error}')
                logging.error(f'properties: {properties}')
                logging.error(f'item: {item}')
                logging.error('*' * 30)

        items_on_page += len(items)
        logging.info(f'Всего айдена на страницах = {items_on_page}')
        end_message = f'Всего обработано = {items_in_itersble} (включая все размеры {items_all_size})'
        logging.info(end_message)
        if len(items) < 20:
            break
        page_num += 1

    df = pd.DataFrame(data_out)

    save_time = dt.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f'result/{TYPE_GOLD[choose_url]}_{save_time}.xlsx'
    df.to_excel(file_name, index=False)
    logging.info(f'Результат вычислений сохранен в {file_name}')

    return file_name, end_message


if __name__ == '__main__':
    print(gold_parse(0)) # Спарсить браслеты
    print(gold_parse(1)) # Спарсить цепи

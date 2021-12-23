import time

import requests
import fake_useragent
import bs4
from openpyxl import Workbook

count = 1
DOMAIN = 'https://novotroitsk.hh.ru'
input_text = 'номер региона на hh, если закончили оставьте строку пустой'
HEADERS = {'user-agent': fake_useragent.UserAgent().random}
REGIONS_NUM = []
input_ = None

while not input_ == '':
    input_ = input(input_text)
    if not input_ == '':
        REGIONS_NUM.append(input_)

URL = f'{DOMAIN}/search/vacancy?'
REQ_TEXT = input('Текст запроса')


def generate_requests(page=''):
    if REGIONS_NUM:
        req = requests.get(f"{URL}{'&'.join([f'area={str(x)}' for x in REGIONS_NUM])}&text={REQ_TEXT}{page}",
                           headers=HEADERS).text
        return req
    else:
        return requests.get(f'{URL}text={REQ_TEXT}{page}', headers=HEADERS).text


data_pages_list = []


def parse_tags(dict_, link, count):
    req = requests.get(link, headers=HEADERS).text
    soup = bs4.BeautifulSoup(req, 'lxml')
    dict_['tags'] = [tag.text for tag in soup.find_all('div', class_='bloko-tag-list')]
    print(f'    Parse vacancy {count}')
    return dict_


def add_card_data(page=''):
    global count
    vacancy_count = 1
    print(f'Parse page {count}')
    for card in bs4.BeautifulSoup(generate_requests(page), 'lxml').find_all('div', class_='vacancy-serp-item'):
        price_text = card.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
        link = card.find('a', class_='bloko-link').get('href')
        res_dict = {
            'title': card.find('a', class_='bloko-link').text,
            'link': link,
            'Зарплата': 'Зарплата не указана' if price_text is None else price_text.text
        }
        data_pages_list.append(parse_tags(res_dict, link, vacancy_count))
        vacancy_count += 1

    time.sleep(3)
    count += 1


def parse_pages(count_parse):
    for index in range(1, count_parse):
        if index == 1:
            add_card_data()
        else:
            add_card_data(f'&page={index - 1}')


get_pages = bs4.BeautifulSoup(generate_requests(), 'lxml').find_all('a', class_='bloko-button')[-2].find('span').text

if get_pages == 'Откликнуться':
    print('Найдена только одна страница')
    parse_pages(2)
else:
    print(f'Страниц найдено {get_pages}')
    parse_pages(int(get_pages))


book = Workbook()
sheet = book.active
sheet['A1'] = 'Заголовок'
sheet['B1'] = 'Ссылка'
sheet['C1'] = 'Зарплата'
sheet['D1'] = 'Тэги'
row = 2

for card in data_pages_list:
    sheet[row][0].value = card['title']
    sheet[row][1].value = card['link']
    sheet[row][2].value = card['Зарплата']
    sheet[row][3].value = ' '.join(card['tags'])
    row += 1

book.save('res.xlsx')
book.close()

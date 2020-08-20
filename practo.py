#!/usr/bin/env python3
import time
import os
import requests
from datetime import datetime
import csv
from lxml import html
from bs4 import BeautifulSoup
from selenium import webdriver

os.system('mkdir csv_practo > /dev/null 2>&1')
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

print("Starting...")
done = []
url_format = 'https://www.practo.com/tests?city={}'
category_url_format = 'https://www.practo.com/health-checkup-packages/{}?city={}'  # category, city
all_cities = ['delhi', 'mumbai', 'hyderabad', 'bangalore', 'kolkata']
all_categories = ['diabetes-checkup', 'cancer-screening-health-checkup', 'skin-care-checkups', 'kidney-urine-checkups', 
                  'stomach-digestion-checkups', 'sexual-wellness-checkups', 'bone-joints-checkups', 'fever-checkup']


def process_tests_list(tests_list, filename):
    global done
    for url in tests_list:
        '''while 1:
            try:
                res = requests.get(url)
                res.raise_for_status()
            except Exception:
                print('.', end='', flush=True)
                pass
            except KeyboardInterrupt:
                print('URL:', url)
                break  # return  # pending
            else:
                break'''
        driver.get(url)
        tree = html.fromstring(driver.page_source)  # res.text
        name = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[1]/h1/text()'
        alt_name = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[1]/span/span[2]/text()'
        price = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/text()'
        what_is_this_test = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[1]/text()'
        what_is_this_test_2 = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[2]/text()'
        why_performed = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[3]/text()'
        frequency = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[4]/text()'
        precautions = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[5]/text()'
        precautions_2 = '/html/body/div[2]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[4]/div/div/div/div/p[6]/text()'
        test_preparation_xp = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[5]/div/div/p'
        understanding_results_xp = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[6]/div/div/div/div'
        #
        understanding_results = tree.xpath(understanding_results_xp)  # find children
        num = len(understanding_results)
        understanding_results = []
        for x in range(num):
            understanding_results.append(understanding_results_xp + '/p[{}]/text()'.format(x+1))
        #
        test_preparation = tree.xpath(test_preparation_xp)  # find children
        num = len(test_preparation)
        test_preparation = []
        for x in range(num):
            test_preparation.append(test_preparation_xp + '/text()[{}]'.format(x+1))
        #
        row_elements = [[name], [alt_name], [price], [what_is_this_test, what_is_this_test_2],
        [why_performed], [frequency], [precautions, precautions_2], test_preparation, understanding_results]
        row = []
        for elem in row_elements:
            if len(elem) > 1:
                text = [' '.join(tree.xpath(part)) for part in elem]
            else:
                text = tree.xpath(elem[0])
            text = ' '.join(text)
            row.append(text)
        row.append(url)
        if not all(row):
            print('Empty data in url {}'.format(url))
            # continue
        with open(filename, 'a+') as file:
            if url not in done:  # URL not in file
                csvwriter = csv.writer(file)
                csvwriter.writerow(row)
                done.append(url)
        # break  # temp


# def main():
#    global done
if 1:
    for city in all_cities:
        folder_name = 'csv_practo'
        print(f'Processing for city {city}')
        for category in all_categories:
            print(f'    Processing for category {category}', end='')
            filename = f'{folder_name}/{city}_{category}.csv'
            with open(filename, 'a+') as file:
                file.seek(0, 0)
                if file.read():  # if not empty, load urls from file
                    file.seek(0, 0)
                    csv_reader = csv.DictReader(file, delimiter=',')
                    done += [line['Link'] for line in csv_reader]
                else:  # if empty, write first column
                    file.seek(0, 0)
                    csvwriter = csv.writer(file)
                    csvwriter.writerow(['Test name', 'Alternate name', 'Price', 'What is this test?', 'Why this test is performed?', 'Frequency', 'Precautions', 'Test Preparation', 'Understanding your test results', 'Link'])
            category_url = category_url_format.format(category, city)
            url = category_url.format(city)
            print('.', end='', flush=True)
            # print('Loading {}... '.format(url))
            while 1:
                try:
                    res = requests.get(url)
                    res.raise_for_status()
                except Exception:
                    print('.', end='', flush=True)
                    pass
                except KeyboardInterrupt:
                    print('URL:', url)
                    break  # return  # pending
                else:
                    break
            print('.', end='', flush=True)
            soup = BeautifulSoup(res.text, 'lxml')
            tests_list = []
            cl = 'u-pad--std--half u-border--std'
            url_prefix = 'https://www.practo.com'
            for e in soup.findAll(class_=cl):
                tests_list.append(url_prefix+e['href'])
            print('Scraping data')
            # Tests
            try:
                process_tests_list(tests_list, filename)
            except:
                pass
            # break
        # break  # temp


driver.quit()

'''while 1:
    main()
    break  # temp
    print('Done. Waiting for 5 minutes.')
    time.sleep(300)'''


#!/usr/bin/env python3
import time
import os
import requests
from datetime import datetime
import csv
from lxml import html
from bs4 import BeautifulSoup
import pandas as pd
import multiprocessing
from selenium import webdriver

os.system('mkdir csv_practo > /dev/null 2>&1')
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

print("Starting...")
done = []
url_format = 'https://www.practo.com/tests?city={}'
category_url_format = 'https://www.practo.com/health-checkup-packages/{}?city={}'  # category, city
all_cities = ['bangalore', 'delhi', 'mumbai', 'chennai', 'hyderabad', 'kolkata', 'pune', 'ahmedabad']  # 
all_categories = ['diabetes-checkup', 'cancer-screening-health-checkup', 'skin-care-checkups', 'kidney-urine-checkups',
                  'stomach-digestion-checkups', 'sexual-wellness-checkups', 'bone-joints-checkups', 'fever-checkup']
test_columns = ['Test name', 'Alternate name', 'Price', 'What is this test?', 'Why this test is performed?',
                'Frequency', 'Precautions', 'Test Preparation', 'Understanding your test results', 'Link']
package_columns = ['Package name', 'Ideal for', 'Includes', 'What preparation is needed for this Checkup?',
                   'Who should book this checkup?', 'Highly recommended for people with', 'Includes tests', 'Link']


def process_tests_list(tests_list, filename):
    global done
    for url in tests_list:
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
        # driver.get(url)
        tree = html.fromstring(res.text)  # driver.page_source
        name = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[1]/h1/text()'
        alt_name = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[1]/span/span[2]/text()'
        price = '/html/body/div[1]/div/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/div/div[2]/div[2]/div[1]/div[1]/text()'
        name = tree.xpath(name)[0]
        try:
            alt_name = tree.xpath(alt_name)[0]
        except:
            alt_name = name
        price = ''.join(tree.xpath(price))
        row = [name, alt_name, price]
        #
        soup = BeautifulSoup(res.text, 'lxml')
        text = soup.text.replace('\n', ' ')
        what_is_this_test = text[text.find('What is this test?')+len('What is this test?'):text.find('Why this test is performed?')]
        why_performed = text[text.find('Why this test is performed?')+len('Why this test is performed?'):text.find('Frequency:')]
        frequency = text[text.find('Frequency:')+len('Frequency:'):text.find('Precautions:')]
        if not frequency:
            frequency = text[text.find('Frequency:')+len('Frequency:'):text.find('Test Preparation')]
        precautions = text[text.find('Precautions:')+len('Precautions:'):text.find('Test Preparation')]
        test_preparation = text[text.find('Test Preparation')+len('Test Preparation'):text.find('Understanding your test results')]
        understanding_results = text[text.find('Understanding your test results')+len('Understanding your test results'):text.find('Your Cart')]
        #
        row += [what_is_this_test, why_performed, frequency, precautions, test_preparation, understanding_results, url]
        # print([item[:20] for item in row])
        if not all(row):
            pass
            # print(f'----> Empty data in url {url}\n')
            # continue
        with open(filename, 'a+') as file:
            if url not in done:  # URL not in file
                csvwriter = csv.writer(file)
                csvwriter.writerow(row)
                done.append(url)


def process_packages_list(packages_list, filename):
    global done
    global driver
    for url in packages_list:
        driver.get(url)
        tree = html.fromstring(driver.page_source)
        name = '/html/body/div[1]/div/div/div[2]/div/div[1]/div[4]/div/div[2]/div/h1/text()'
        name = tree.xpath(name)[0]
        #
        soup = BeautifulSoup(driver.page_source, 'lxml')
        text = soup.text.replace('\n', ' ')
        for_age = text[text.find('Ideal for individuals aged ')+len('Ideal for individuals aged '):text.find('Includes')]
        for_age = for_age.split('\xa0')[-1]
        includes = text[text.find('Includes')+len('Includes '):text.find('Why book with us?')]
        preparation_needed = text[text.find('What preparation is needed for this Checkup?')+len('What preparation is needed for this Checkup?'):text.find('Who should book this checkup?')]
        who_should_book = text[text.find('Who should book this checkup?')+len('Who should book this checkup?'):text.find('Highly recommended for people with')]
        highly_recommended = text[text.find('Highly recommended for people with')+len('Highly recommended for people with'):text.find('Tests')-len('Includes xx Test')]
        number_of_tests = f'Includes {includes[:3]}'
        includes_tests = text[text.find(number_of_tests)+len(number_of_tests):text.find('How it works?')]
        row = [name, for_age, includes, preparation_needed, who_should_book, highly_recommended, includes_tests, url]
        # print(f'{highly_recommended[:10]}..{highly_recommended[-10:]}')
        #
        # print([item[:10] for item in row])
        if not all(row):
            pass
            # print(f'----> Empty data in url {url}\n')
        with open(filename, 'a+') as file:
            if url not in done:  # URL not in file
                csvwriter = csv.writer(file)
                csvwriter.writerow(row)
                done.append(url)


def process_category(category):
    global global_city
    global done
    print(f'    Processing for category {category}', end='')
    filename = f'{folder_name}/{city}/{category}.csv'
    for stype in ['test', 'package']:
        s_filename = filename.replace(f'{category}', f'{stype}_{category}')
        with open(s_filename, 'a+') as file:
            file.seek(0, 0)
            if file.read():  # if not empty, load urls from file
                file.seek(0, 0)
                csv_reader = csv.DictReader(file, delimiter=',')
                done += [line['Link'] for line in csv_reader]
            else:  # if empty, write first column
                # file.seek(0, 0)
                csvwriter = csv.writer(file)
                csvwriter.writerow(test_columns if stype == 'test' else package_columns)
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
    print('Scraping data')
    # Tests
    stype = 'test'
    cl = 'u-pad--std--half u-border--std'
    url_prefix = 'https://www.practo.com'
    # tests_list = []
    # for e in soup.findAll(class_=cl):
    #     tests_list.append(url_prefix+e['href'])
    tests_list = [url_prefix+e['href'] for e in soup.findAll(class_=cl)]
    try:
        process_tests_list(tests_list, filename.replace(f'{category}', f'{stype}_{category}'))
    except KeyboardInterrupt:
        exit()
    except Exception:
        print(f'Failed for filename {filename}')
        pass
    # Packages
    stype = 'package'
    packages_list = []
    cl = 'c-package o-f-color--primary u-marginr--less'
    url_prefix = 'https://www.practo.com'
    for e in soup.findAll(class_=cl):
        packages_list.append(url_prefix+e.a['href'])
    try:
        process_packages_list(packages_list, filename.replace(f'{category}', f'{stype}_{category}'))
    except KeyboardInterrupt:
        exit()
    except Exception:
        print(f'Failed for filename {filename}')
        pass
    # break


# def main():
#    global done
if 1:
    for city in all_cities:
        global_city = city
        folder_name = 'csv_practo'
        print(f'Processing for city {city}')
        os.system(f'mkdir {folder_name}/{city} > /dev/null 2>&1')
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(process_category, all_categories)
        # for category in all_categories:
    # break  # temp


driver.quit()

'''
apt install chromium

from bs4 import BeautifulSoup
from selenium import webdriver
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)

url = 'https://www.practo.com/health-checkup-packages/advanced-diabetic-patients-health-checkup/p?tag_id=28&city=delhi'
driver.get(url)
page_source = driver.page_source
soup = BeautifulSoup(driver.page_source, 'lxml')
text = soup.text.replace('\n', ' ')


while 1:
    main()
    break  # temp
    print('Done. Waiting for 5 minutes.')
    time.sleep(300)
'''

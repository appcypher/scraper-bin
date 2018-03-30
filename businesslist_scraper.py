#!/usr/bin/env python3
import time, requests, csv
from bs4 import BeautifulSoup
from os import listdir, path, rmdir, mkdir, remove
from re import sub

def remove_captcha_files(companies_dir):
    for filename in listdir(companies_dir): 
        is_captcha = False
        with open(companies_dir + '/' + filename, 'r') as f: 
            if 'CaptchaScode' in f.read(): 
                is_captcha = True
        if is_captcha:
            remove(companies_dir + '/' + filename)

# get categories from the business list txt file
def get_categories(cat_path): 
    with open(cat_path, 'r') as f:
        categories = list(map(lambda x: x[:-1], f.readlines()))
        return categories

# create a dir for each business category
def make_category_directories(categories):
    if not path.isdir('./home/'): 
        mkdir('./home/')
    if not path.isdir('./home/categories'): 
        mkdir('./home/categories')
    for cat in categories: 
        cat = sub('\\s', '', cat)
        if not path.isdir('./home/categories/{}'.format(cat)):
            mkdir('./home/categories/{}'.format(cat))

# make company dir under each category
def make_company_directories(categories): 
    for cat in categories:   
        if not path.isdir('./home/categories/{}/companies'.format(cat)):
            print("category company: " + cat ) # DEBUG
            mkdir('./home/categories/{}/companies'.format(cat))

# get pages under each category
def download_category_pages(categories, cat_dir):
    make_category_directories(categories)
    make_company_directories(categories)
    for cat in categories:
        for i in range(1, 11):
            print(cat) # DEBUG

            category_file = '{}/{}/{}.html'.format(cat_dir, cat,i)

            if path.exists(category_file): continue
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'}
            url = 'https://www.businesslist.com.ng/category/{}/{}/state:lagos'.format(cat,i)
            res = requests.get(url, headers=headers)

            print('{} | {}'.format(res.status_code,url)) # DEBUG
            if res.status_code == 404: continue

            with open(category_file, 'w') as htmlFile:
                htmlFile.write(str(res.content))
            time.sleep(10)

# cleanup phone number format
def parse_phone_number(num_str):      
    num_str = sub("\s+|[\(\)-]", "", num_str)
    num_str = sub("\+?234(?=\d{10})", "0", num_str)

    list_num = []

    temp_num = ""
    for (i, ch) in enumerate(num_str): 
        temp_num += ch
        if (i+1) % 11 == 0: 
            list_num.append(temp_num)
            temp_num = ""

    return ",".join(list_num)

# download each company page under a category
def download_company_pages(cat_dir): 
    for filename in listdir(cat_dir):
        file = '{}/{}'.format(cat_dir, filename)
        if path.isfile(file):
            with open(file, 'r') as f:    
                html = BeautifulSoup(f, 'html.parser')
                print('=========== {} =============='.format(filename)) # DEBUG
                for link in html.select('h4 > a'):
                    ln = link['href']
                    name = link.text
                    url = 'https://www.businesslist.com.ng{}'.format(ln)

                    company_name = sub('/|\s|\\\\|\\?', '_', name)
                    company_file = '{}/companies/{}.html'.format(cat_dir, company_name)

                    if path.exists(company_file): continue

                    res = requests.get(url)
                    
                    print('{} | {}'.format(res.status_code,url)) # DEBUG

                    if 'CaptchaScode' in res.text: continue
                    if res.status_code == 404: continue

                    print(company_file) # DEBUG
                    with open(company_file, 'w') as htmlFile:
                        htmlFile.write(str(res.content))
                    time.sleep(10)

# pulling all needed data from each company under a category
def parse_data(company_dir): 
    row_list = []
    for filename in listdir(company_dir):
        file = '{}/{}'.format(company_dir, filename)
        with open(file, 'r') as f:
            # print("----------------------------") # DEBUG
            html = BeautifulSoup(f, 'html.parser')

            company_name  = ""
            address       = ""
            description   = ""
            hours         = ""
            phones        = ""
            mobile_phones = ""
            manager       = ""
            website       = ""
            started       = ""
            employees     = ""

            for div in html.select('#company_item > div.company_details > div'):
                div2 = div.select('div')
                span = div.select('span')
                if not div2 == []:
                    div_title = div2[0].text
                    div_title_len = len(div_title)
                    if not (div_title == "" or div_title == "E-mail"):
                        body = div.text.replace(div_title, '', 1).replace('\n', '') # was printing title with body
                        # print('{}: {}'.format(div_title, body)) # DEBUG
                        if div_title == "Company name": company_name = body
                        elif div_title == "Address": address = body
                        elif div_title == "Phone": phones = parse_phone_number(body); #print('{}: {}'.format(div_title, phones)) # DEBUG
                        elif div_title == "Mobile phone": mobile_phones = parse_phone_number(body); # print('{}: {}'.format(div_title, mobile_phones)) # DEBUG
                        elif div_title == "Website": website = body

                elif not span == []:
                    span_title = span[0].text
                    span_title_len = len(span_title)
                    body = div.text.replace(span_title, '', 1) # was printing title with body
                    # print('{}: {}'.format(span_title, body)) # DEBUG
                    if span_title == "Establishment year": started = body
                    elif span_title == "Employees": employees = body
                    elif span_title == "Company manager": manager = body
            
            description = html.select(".text.description")
            description = '' if description == [] else description[0].text.replace('\\r\\n', '').replace('\n', ' ')
            # print('Description: ' + description) # DEBUG
            
            hours = html.select(".openinghours.description li")
            hours = '' if hours == [] else hours[0].text[7:] # skip 'Monday:' string 
            # print('Hours: ' + str(hours)) # DEBUG

            row = [company_name, description, address, hours, phones, mobile_phones, manager, website, started, employees]
            row_list.append(row)

    return row_list

# write data to csv file
def write_to_csv(row_list, path, category):
    columns = ['COMPANY_NAME', 'DESCRIPTION', 'ADDRESS', 'HOURS', 'PHONES', 'MOBILE_PHONES', 'MANAGER', 'WEBSITE', 'STARTED', 'EMPLOYEES']    
    with open('{}/{}.csv'.format(path, category), 'w', newline='', encoding='utf-8') as data_file:
        data_writer = csv.writer(data_file)
        data_writer.writerow(columns)
        for row in row_list:
            data_writer.writerow(row)

def main():
    categories = get_categories('./current1.txt')
    cat_dir = './home/categories'

    download_category_pages(categories, cat_dir)


    # download all company pages in each category
    for cat in categories:
        download_company_pages('{}/{}'.format(cat_dir, cat))

    # row_board = []

    # get all company details in each category
    # for cat in categories: 
    #     row_list = parse_data('{}/{}/companies'.format(cat_dir, cat))
    #     row_board.append(row_list)

    # write each category to it's csv file 
    # for row_list, cat in zip(row_board, categories): 
    #     write_to_csv(row_list, '{}/{}/companies'.format(cat_dir, cat), cat)

main()

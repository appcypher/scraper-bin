import time, csv, sys, platform
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

industry = 'resturant'
try:
    industry = sys.argv[1]
except IndexError:
    pass
file_name = 'gmaps_' + industry + '.csv'
coord_lat = '6.4165804'
coord_long = '3.5714664'
chrome_path = '/usr/bin/chromedriver'
if platform.system() == 'Windows':
    chrome_path = './chromedriver'
url = 'https://www.google.com/maps/search/{}/@{},{},11z'.format(
    industry, coord_lat, coord_long)
browser = webdriver.Chrome(chrome_path)
business_list = []

def open_page():
    browser.get(url)
    time.sleep(7)

def scrape():
    open_page()

    # uncheck the "Update results when the map moves"
    map_update_uncheck = browser.find_element_by_xpath('//*[@id="section-query-on-pan-checkbox-id"]')
    map_update_uncheck.click()

    business_divs = browser.find_elements_by_class_name('section-result')

    while True:
        for i in range(len(business_divs)): 
            biz = business_divs[i]

            biz.click()
            time.sleep(7)

            business = []
            name = ''
            address = ''
            contact = ''
            site = ''
            hours = ''

            try:
                name = browser.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[2]/div/div/div[1]/div[3]/div[1]/h1').text
                print('name: ' + name)
                business.append(name)
            except NoSuchElementException:
                name = ''
                print('name: ' + name)
                business.append(name)
            ##########################
            try:
                address = browser.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[2]/div/div/div[4]/div/div[1]/span[3]/span[1]/span').text
                print('address: ' + address)
                business.append(address)
            except NoSuchElementException:
                print('address: ' + address)
                business.append(address)
            ##########################
            try:
                contact = browser.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[2]/div/div/div[5]/div/div[1]/span[3]/button').text
                contact = ''.join(contact.split(' ')) # removing the spaces
                print('line: ' + contact)
                business.append(contact)
            except NoSuchElementException:
                print('contact: ' + contact)
                business_list.append(contact)
            ##########################
            try:
                site = browser.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[2]/div/div/div[5]/div/div[1]/span[3]/span[2]/span/a[3]').text
                print('site: ' + site)
                business.append(site)
            except NoSuchElementException:
                print('site: ' + site)
                business.append(site)
            ##########################
            try:
                hours = browser.find_element_by_xpath(
                    '//*[@id="pane"]/div/div[2]/div/div/div[6]/div[1]/span[2]/span[2]').text
                # print('hour: ' + hour)
                business.append(hours)
            except NoSuchElementException:
                print('hours: ' + hours)
                business.append(hours)
            
            # add the business detail to list 
            business_list.append(business)

            print('==========================')
                
            back = browser.find_element_by_xpath('//*[@id="pane"]/div/div[2]/div/div/button/jsl/jsl[7]/span')
            back.click()
            time.sleep(7)
            business_divs = browser.find_elements_by_class_name('section-result')
        
        try:
            next_page = browser.find_element_by_xpath('//*[@id="section-pagination-button-next"]/span')
            next_page.click()
            time.sleep(7)

            business_divs = browser.find_elements_by_class_name('section-result')
        except WebDriverException:
            break

    columns = ['NAME', 'ADDRESS', 'CONTACT', 'SITE', 'HOURS']

    with open(file_name, 'w', newline='', encoding='utf-8') as data_file:
        data_writer = csv.writer(data_file)
        data_writer.writerow(columns)
        for biz in business_list:
            data_writer.writerow(biz)
    print('DONE!')


if __name__ == '__main__':
    scrape()

import requests
import pandas as pd 
from bs4 import BeautifulSoup
import json

from concurrent.futures import ThreadPoolExecutor
import time
from tqdm.notebook import tqdm
from tqdm import tqdm as tqdm2
from tqdm.contrib.concurrent import thread_map

Product_Links = []
TotalData = []
categories_links = []
category_name = []
# get Category Names & Categories Link
def category():
    link = 'https://gfxplugin.com/en/'
    r = requests.get(link).text
    soup = BeautifulSoup(r , 'lxml')
    ul = soup.find('ul' , class_='sub-menu')
    lis = ul.find_all('li' , recursive=False)
    for li in lis:
        cat_name = li.a.text.strip()
        cat_link = li.a['href']
        
        categories_links.append(cat_link)
        category_name.append(cat_name)


    return

# get the last page of each category
def lastpage(url):
    css = '.PagedList-skipToLast .page-link'
    r = requests.get(url).text 
    soup = BeautifulSoup(r ,'lxml')
    c = (soup.select_one(css)['href'].split('/')[-1]).strip()
    d = int(c)
    return (d)

# get data from product link
def get_data(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r , 'lxml')
    script = soup.find('script' , {'type':'application/ld+json'}).text 
    jsondata = json.loads(script)
    # Title
    # title = soup.find('div' , class_='tab-body-box').div.h2.strong.text.strip()
    title = jsondata['name']
    title = title.replace("Download" , '')
    title = title.replace('–', '-')
    title = title.strip()
    # Description
    # description = soup.find('div' , class_='tab-body-box').find('div')
    description = soup.select_one('h2+ ul')
    if description is None:
        description = soup.select_one('#nav-0 p')
    # Image Link
    img = jsondata['image']
    data = {
        'Title': title,
        'Description': description,
        'Image Link': img,
        'Product Link': url
    }
    TotalData.append(data)
    return

# getting product links
def getProds(x):
    url = link_index + f"/{x}"
    r = requests.get(url).text
    soup = BeautifulSoup(r, 'lxml')
    products = soup.select('.slider-pro-items-name')
    for i in products:
        prodlink = (i['href'])
        Product_Links.append(prodlink)

    return


print('How do you want to scrape?')
print('\n')
print('1: Category Wise')
print('2: Link Wise')
print('\n')
num = int(input('Enter Number: '))
print('\n')
if num==1:
    category()
    for i in range(len(category_name)):
        print(f'{i+1}: {category_name[i]}')

    print('\nWhich category do you want to scrape?')
    print('\n')
    n = int(input(f'Enter a Number from 1 to {len(category_name)}: '))
    print('\n')
    # Getting the category link
    link_index = categories_links[n-1]
    last_page = lastpage(link_index)

    Pages = []
    p = int(input('How many products do you want to scrape? '))
    L = (p//24)+1
    # Fetching product links
    print('\n')
    print('Fetching the Product Link')
    for i in range(1 , L+1):
        Pages.append(i)
    
    thread_map(getProds , Pages , max_workers=10)


    new_products = Product_Links[0:p]

    # getting Total Data
    print('\n')
    print('Fetching Products Data')
    thread_map(get_data , new_products , max_workers=10)


    df = pd.DataFrame(TotalData)
    file_name = f"{category_name[n-1]}.csv"
    df.to_csv(file_name , index=False )
    print('\nData Stored to CSV')
    time.sleep(3)

elif num==2:
    LINK = input('Enter the Product Link: ')
    r = requests.get(LINK).text
    soup = BeautifulSoup(r , 'lxml')
    script = soup.find('script' , {'type':'application/ld+json'}).text 
    jsondata = json.loads(script)
    filename = f"{jsondata['name'].replace('Download','').strip()}.csv"
    get_data(LINK)
    df = pd.DataFrame(TotalData)
    df.to_csv(filename , index=False)
    print('\nData Stored to CSV')
    time.sleep(3)
else:
    print('Incorrect Entry....')




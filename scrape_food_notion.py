import requests, json
from bs4 import BeautifulSoup

# Notion Setup
token = 'secret_W9BBlOEIm8CZwgWR4FrUQzZ4jd883iX0C9aJQsIM6WR'
databaseId = 'aa19dde9a14641fdb5bc6c603f340963'
headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
}

#Notion create row in DataBase
def createRow(databaseId, headers, details):
    createUrl = "https://api.notion.com/v1/pages"

    newRowData = {
        "parent": {"database_id": databaseId},
        "properties": {
            "Shop Name": {
                "rich_text": [{
                    "text":{
                        "content": details["name"]
                    }
                }]
            },
            "Must Try!": {
                "rich_text": [{
                    "text":{
                        "content": details["mustTry"]
                    }
                }]
            },
            "Hawker Center": {
                "select": {
                   "name": details["hawker"]
                }
            },
        }
    }

    # Convert python dict to json
    data = json.dumps(newRowData)
    res = requests.request("POST", createUrl, headers=headers, data=data)
    print(res.status_code)
    
    
# Code for scraping each individual website
def scrape_website(url, food_center):
    source_code = requests.get(url).text
    soup_html = BeautifulSoup(source_code, 'lxml')

    # Getting the main body of html to scrape
    page = soup_html.find('div', class_="col-md-6 article__post responsive-iframe-video")
    if (not page):
        return None
    # Finding each article in the page
    titles = page.find_all('h2')
   
    for title in titles:
        # Edge case
        if (title.img):
            continue
        
        # Getting all the paragraphs for each article to scrape
        list_of_para = []
        sibling = title.next_sibling
        while True:
            if (not sibling or sibling.name == 'h2'):
                break
            if (sibling.name == 'p'):
                list_of_para.append(sibling)
            
            sibling = sibling.next_sibling

        # Scraping the paragraphs for each article to find the recommended food
        food_name = ""
        for para in list_of_para:
            temps = para.find_all('em')
            for temp in temps:
                if (temp and ("(S$" in temp.text or "($" in temp.text)):
                    food_name += temp.text.lstrip()

            temps1 = para.find_all('span')
            for temp1 in temps1:
                if (temp1 and ("(S$" in temp1.text or "($" in temp1.text)):
                    food_name += temp1.text.lstrip()
    
    
        # Scraping for the shop name in each article
        shop_link = title.a
        if not shop_link:
            if ("." not in title.text):
                continue
            shop_name = title.text.split(".")[1].lstrip()
            
        else:
            if ("https://sethlui.com" not in shop_link["href"]): 
                continue
            shop_name = shop_link.text

        # Condensing all the info needed to pass as inputs to create a new row in notion
        details = {
            "name": shop_name,
            "mustTry": food_name,
            "hawker": food_center.replace(',', ''),
        }

        # Calling the function to create row 
        createRow(databaseId, headers, details)

# Function to get all the website links to scrape
def get_hawker_links(url, url_list, name_list):
    source_code = requests.get(url).text
    soup_html = BeautifulSoup(source_code, 'lxml')
    page = soup_html.find('div', class_="col-md-6 article__post responsive-iframe-video")
    titles = page.find_all('h2')
    for title in titles:
        url = title.a["href"]
        center_name = title.a.text
        if "https://sethlui.com/" in url:
            url_list.append(url)
            name_list.append(center_name)



def start_scrape():
    list_of_url = []
    list_of_food_center = []
    get_hawker_links("https://sethlui.com/ultimate-compilation-of-hawker-centres-in-singapore-part-1/", list_of_url, list_of_food_center)
    get_hawker_links("https://sethlui.com/ultimate-compilation-of-hawker-centres-singapore-part-2/", list_of_url, list_of_food_center)
    for i in range(len(list_of_url)):
        scrape_website(list_of_url[i], list_of_food_center[i])

start_scrape()
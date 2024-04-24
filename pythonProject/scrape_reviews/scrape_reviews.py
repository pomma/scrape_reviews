import requests
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

curr_file= 'C:\\Users\\pomma\\scrape_reviews\\reviews.xml'
root = ET.Element('root')
tree = ET.ElementTree(root)
with open(curr_file, 'wb') as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
tree.write(curr_file)

html_escape_table = {
    ">": "&gt;",
    "<": "&lt;",
}


def scrape_reviews(url, review_id):
    parser = ET.XMLParser(encoding='UTF-8')
    tree = ET.parse(curr_file, parser=parser)
    root = tree.getroot()

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        fiction_name = soup.find('h1', class_='font-white').text.strip()

        fiction_stats = soup.find('div', class_='fiction-stats')

        print("Fiction Name:", fiction_name)
        print("Stats:", fiction_stats)
        ##gotta parse through the stats to make them make sense
        print()

        last_page = soup.find(lambda tag: tag.name == 'a' and tag.get_text(strip=True) == "Last »")
        if (last_page):
            last_page_number = int(last_page['data-page']) + 1
            j = 0
            for i in range(1, last_page_number):
                response = requests.get(url + "?sorting=top&reviews=" + str(i))
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')

                    reviews = soup.find_all(class_='review')
                    for review in reviews:
                        reviewer_name = review.find('a', class_='small').text.strip()
                        review_content = review.find('div', class_='review-inner').text.strip()
                        new_element = ET.SubElement(root, "a" + str(review_id) + '_' + str(j),
                                                    attrib={'reviewer_name': reviewer_name})
                        new_element.text = escape(review_content, html_escape_table)
                        j += 1
                        print(new_element)
                        print()

    else:
        print("Failed to retrieve the page. Status code:", response.status_code)
    tree.write(curr_file)


def get_best_rated(number):
    url = "https://www.royalroad.com/fictions/best-rated"

    response = requests.get(url)
    if response.status_code == 200:
        last_page_number = number
        top_fictions = list()
        for i in range(1, last_page_number):
            response = requests.get(url + "?page=" + str(i))
            html_content = response.text
            fiction_titles = re.findall(r'<a href="/fiction/[^"]+" class="font-red-sunglo bold">([^<]+)</a>',
                                        html_content)
            fiction_links = re.findall(r'<a href="(/fiction/[^"]+)" class="font-red-sunglo bold">', html_content)
            print(fiction_titles)
            top_fictions += (zip(fiction_titles, ["https://www.royalroad.com" + link for link in fiction_links]))

        return top_fictions
    else:
        print("Failed to retrieve the page. Status code:", response.status_code)


def call_scrape_reviews(num):
    fiction_urls = get_best_rated(num)

    if fiction_urls:
        i = 0
        for name, url in fiction_urls:
            scrape_reviews(url, i)
            i += 1
            print("-" * 50)
    else:
        print("Failed to retrieve fiction URLs.")

import os
from bs4 import BeautifulSoup
import json
import pandas as pd
import requests
import re

def title_to_key(title):
    title = title.replace("°", "deg")
    key = re.sub('[^0-9a-zA-Z]+', '_', title)
    key = key.lower()
    return key

def extract_thecvf_paper_info(html_file = "cvpr2023.html"):

    # Download webpage using wget
    if not os.path.exists(html_file):
        os.system('wget -O {} https://openaccess.thecvf.com/CVPR2023?day=all'.format(html_file))
    # Open downloaded webpage
    with open(html_file, 'r') as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'html.parser')

    papers_info = {}

    for paper in soup.find_all('dt', {'class': 'ptitle'}):
        paper_info = {}
        # Initialize default values
        paper_info['home_page'] = ""
        paper_info['pdf'] = ""
        paper_info['supp'] = ""
        paper_info['arxiv'] = ""
        paper_info['bibtex'] = ""
        paper_info['code'] = ""
        paper_info['authors'] = ""

        paper_title = paper.get_text(strip=True)

        paper_page = paper.find('a').get('href')
        paper_info['home_page'] = f'https://openaccess.thecvf.com/{paper_page}'

        paper_links = paper.find_next_sibling('dd').find_next_sibling('dd')

        # Extracting pdf, supp, arxiv links
        paper_links = paper.find_next_sibling('dd').find_next_sibling('dd').find_all('a')
        #import ipdb; ipdb.set_trace()
        for link in paper_links:
            if 'pdf' in link.text:
                paper_info['pdf'] = 'https://openaccess.thecvf.com' + link['href']
            elif 'supp' in link.text:
                paper_info['supp'] = 'https://openaccess.thecvf.com' + link['href']
            elif 'arXiv' in link.text:
                paper_info['arxiv'] = link['href']

        # Extracting bibtex
        bibtex = soup.find('div', {'class': 'bibref'})
        paper_info['bibtex'] = bibtex.text.strip()
        paper_info['title'] = paper_title

        paper_key = title_to_key(paper_title)
        papers_info[paper_key] = paper_info

    return papers_info

# add code url
def enrich_paper_info(papers_info):
    url = 'https://cvpr2023.thecvf.com/Conferences/2023/AcceptedPapers'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    papers = soup.find_all('tr')  # Finding all table row tags

    for paper in papers:
        title_link = paper.find('a')  # Finding the first 'a' tag inside the table row

        if not title_link:
            continue  # Skip this row if there's no <a> tag or if the href doesn't start with 'https://github.com'

        title = link = authors = ''  # Initialize the variables

        title = title_link.text  # Paper title
        link = title_link['href']  # GitHub link

        authors_div = paper.find('div', {'class': 'indented'})
        if authors_div:
            authors = authors_div.text.strip().split('·')[0].strip()  # First author

        # Append the paper information to the list
        paper_key = title_to_key(title)
        try:
            papers_info[paper_key]['title'] = title
            papers_info[paper_key]['authors'] = authors
            papers_info[paper_key]['code'] = link
        except:
            continue

    return papers_info


def main():
    thecvf_papers_info = extract_thecvf_paper_info()
    """
    with open('papers_thecvf_info.json', 'w') as f:
        json.dump(thecvf_papers_info, f)
    """
    paper_list = enrich_paper_info(thecvf_papers_info)
        # Save the paper list to a JSON file
    with open('papers_info.json', 'w') as f:
        json.dump(paper_list, f)
    print('Saved paper information to papers_info.json.')


if __name__ == "__main__":
    # Call the function
    main()
    

import requests
import json
import os

github_api = 'https://api.github.com/repos'
github_token = ''  # Replace with your GitHub token

def enrich_papers_info():
    # Load the paper list from the JSON file
    with open('CVPR2023/papers_info_refined.json', 'r') as f:
        paper_list = json.load(f)

    paper_with_code_list = []
    for _, paper in paper_list.items():
        link = paper['code']  # GitHub link
        if link == '':
            continue

        stars = 0  # Initialize star count

        if 'github.com' in link:
            parts = link.split('/')
            if len(parts) > 4:  # Ensure the link points to a specific repository
                username = parts[3]
                repo_name = parts[4]
                # Construct the API URL and send a GET request
                repo_api = f'{github_api}/{username}/{repo_name}'
                try:
                    repo_response = requests.get(repo_api, headers={'Authorization': f'token {github_token}'})
                    repo_info = json.loads(repo_response.text)

                    # Check the number of stars
                    stars = repo_info.get('stargazers_count', 0)
                except Exception as e:
                    print(f'Error while fetching star count for {link}. Error: {e}')

        # Enrich the paper information with stars and PDF link
        paper['stars'] = stars
        paper_with_code_list.append(paper)

    # Save the enriched paper list back to the JSON file
    with open('papers_with_code_and_stars.json', 'w') as f:
        json.dump(paper_with_code_list, f)

    print('papers_with_code_and_stars.json saved~')

def write_papers_to_readme():
    # Load the enriched paper list from the JSON file
    with open('papers_with_code_and_stars.json', 'r') as f:
        paper_list = json.load(f)

    # Sort the list by stars
    sorted_paper_list = sorted(paper_list, key=lambda x: x['stars'], reverse=True)

    with open('CVPR2023.md', 'w') as f:
        # Write the table headers
        f.write("# Top CVPR2023 Papers with Code \n")
        f.write("|Title  | Paper | Code | Github Stars |\n")
        f.write("| :---: | :---: | :---: | :---: |\n")

        for paper in sorted_paper_list:
            # Write the row to the file
            parts = paper['code'].split('/')
            if len(parts) > 4:  # Ensure the link points to a specific repository
                username = parts[3]
                repo_name = parts[4]
            show_stars = "![GitHub Repo stars](https://badgen.net/github/stars/{}/{})".format(username,repo_name)
            f.write(f"| {paper['title']} | [Link]]({paper['home_page']}) | [Github]({paper['code']}) | {show_stars}|\n")

    print('Converted enriched paper information to CVPR2023.md.')

override = True
if override or not os.path.exists('papers_with_code_and_stars.json') :
    enrich_papers_info()

write_papers_to_readme()

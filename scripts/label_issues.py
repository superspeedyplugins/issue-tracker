import os
import json
import requests

def label_issue(issue_number, title, body, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Combine title and body for keyword search
    content = f"{title} {body}".lower()

    # Define keywords and corresponding labels
    keywords_to_labels = {
        'ssf|super speedy filters|super-speedy-filters': 'SSF Label',
        'sss|super speedy search|super-speedy-search': 'SSS Label',
        # Add more mappings as needed
    }

    # Determine the right label based on keywords
    labels_to_add = []
    for keywords, label in keywords_to_labels.items():
        if any(keyword in content for keyword in keywords.split('|')):
            labels_to_add.append(label)

    if labels_to_add:
        # Add labels to the issue
        url = f'https://api.github.com/repos/Glynnage/REPO_NAME/issues/{issue_number}/labels'
        data = {'labels': labels_to_add}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            print("Labels added to issue successfully")
        else:
            print(f"Failed to add labels to issue: {response.content}")
    else:
        print("No matching keywords found for labeling.")

# Environment variables
issue_number = os.getenv('ISSUE_NUMBER')
issue_title = os.getenv('ISSUE_TITLE')
issue_body = os.getenv('ISSUE_BODY')
token = os.getenv('GITHUB_TOKEN')

# Label the issue
label_issue(issue_number, issue_title, issue_body, token)

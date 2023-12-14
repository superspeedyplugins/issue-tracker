import os
import json
import requests

def label_issue(issue_number, title, body, token, plugins_str):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Load plugins data
    ssp_plugins = json.loads(plugins_str)

    # Combine title and body for keyword search
    content = f"{title} {body}".lower()

    # Determine the right label based on synonyms in ssp_plugins
    labels_to_add = []
    for label, details in ssp_plugins.items():
        if any(synonym.lower() in content for synonym in details['synonyms']):
            labels_to_add.append(label)

    if labels_to_add:
        # Add labels to the issue
        url = f'https://api.github.com/repos/superspeedyplugins/issue-tracker/issues/{issue_number}/labels'
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
ssp_plugins_str = os.getenv('SSP_PLUGINS')

# Label the issue
label_issue(issue_number, issue_title, issue_body, token, ssp_plugins_str)

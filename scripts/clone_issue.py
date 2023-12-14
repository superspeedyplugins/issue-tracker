import os
import json
import requests


def clone_issue(issue_number, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    source_repo = "superspeedyplugins/issue-tracker"

    # Get the issue from the source repository
    issue_url = f'https://api.github.com/repos/{source_repo}/issues/{issue_number}'
    response = requests.get(issue_url, headers=headers)
    issue_data = response.json()

    # Fetch comments from the source issue
    comments_url = issue_data['comments_url']
    comments_response = requests.get(comments_url, headers=headers)
    comments_data = comments_response.json()

    # Construct the body with comments
    body_with_comments = issue_data['body'] + '\n\n'
    for comment in comments_data:
        body_with_comments += f"{comment['user']['login']} said: {comment['body']}\n\n"

    # Add sourced from text
    body_with_comments += f"Sourced from public issue {issue_url}"

    ssp_plugins_str = os.getenv('SSP_PLUGINS')
    ssp_plugins = json.loads(ssp_plugins_str)

    issue_labels = issue_data.get('labels', [])
    destination_repo_slug = get_matching_repo_slug(issue_labels, ssp_plugins)
    if destination_repo_slug:
        destination_repo = f'superspeedyplugins/{destination_repo_slug}'

        # Prepare data for the new issue
        new_issue_data = {
            'title': issue_data['title'],
            'body': body_with_comments,
            'labels': issue_data['labels']
        }

        # Create a new issue in the destination repository
        create_issue_url = f'https://api.github.com/repos/{destination_repo}/issues'
        create_response = requests.post(create_issue_url, headers=headers, data=json.dumps(new_issue_data))

        if create_response.status_code == 201:
            print("Issue cloned successfully")
            new_issue_data = create_response.json()
            new_issue_url = new_issue_data['html_url']

            # Construct the comment
            comment_text = f"This issue has been cloned to our private repo: {new_issue_url}"

            # Post the comment to the original issue
            comment_url = f'https://api.github.com/repos/{source_repo}/issues/{issue_number}/comments'
            comment_data = {'body': comment_text}
            comment_response = requests.post(comment_url, headers=headers, data=json.dumps(comment_data))
        else:
            print("Failed to clone issue")
    else:
        print("No matching repo found")        

# Function to find the first matching label and return the corresponding repository slug
def get_matching_repo_slug(issue_labels, plugins):
    for label in issue_labels:
        label_name = label['name']
        if label_name in plugins:
            return plugins[label_name]['slug']
    return None
    
# Environment variables
issue_number = 3  # This should be passed from the workflow
token = "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"  # Your GitHub token

# Clone the issue
clone_issue(issue_number, token)

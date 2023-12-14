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

    destination_repo_name = get_first_project_repo(issue_number, headers)
    destination_repo = f'superspeedyplugins/{destination_repo_name}'

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
    
def get_first_project_repo(issue_number, headers):
    # Get the issue timeline
    source_repo = "superspeedyplugins/issue-tracker"

    timeline_url = f'https://api.github.com/repos/{source_repo}/issues/{issue_number}/timeline'
    timeline_response = requests.get(timeline_url, headers=headers)
    timeline_data = timeline_response.json()

    # Find the first project card event
    for event in timeline_data:
        if event['event'] == 'added_to_project':
            # Get the project card URL from the event
            project_card_url = event['project_card']['url']

            # Get project card details
            card_response = requests.get(project_card_url, headers=headers)
            card_data = card_response.json()

            # Extract the project URL
            project_url = card_data['project_url']

            # Get project details
            project_response = requests.get(project_url, headers=headers)
            project_data = project_response.json()

            # Extract the repository name from the project data
            repo_name = project_data['owner_url'].split('/')[-1]
            return repo_name

    return None

# Environment variables
issue_number = os.getenv('ISSUE_NUMBER')  # This should be passed from the workflow
token = os.getenv('GITHUB_TOKEN')  # Your GitHub token

# Clone the issue
clone_issue(issue_number, token)

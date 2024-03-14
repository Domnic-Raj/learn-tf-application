import subprocess
import os
from git import Repo
import datetime
import json
import pathlib
import requests
from git import GitCommandError
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


F5_NON_PROD = 'https://mod-ptc-nonprod.mdgapp.net'
F5_PROD_PTC = 'https://mod-ptc-prod.mdgapp.net'
F5_PROD_CTC = 'https://mod-ctc-prod.mdgapp.net'
BACKUP_LOCATION = pathlib.Path('f5_backup')

def fetch_data(url):
    try:
        response = requests.get(url, auth=('MoD_Guest', 'ReadOnly'))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data from {url}: {e}")
        return None

def backup_data(data, destination):
    backup_dir = BACKUP_LOCATION / destination
    backup_dir.mkdir(parents=True, exist_ok=True)

    if data:
        for item in data.get('items', []):
            if item['partition'] != 'Common':
                file_path = backup_dir / f"{item['name']}.json"
                print(f"Processing {item['name']}: {file_path}")
                with open(file_path, "w") as file:
                    json.dump(item, file, indent=2)

def run():
    datagroups_data = fetch_data(F5_NON_PROD + '/mgmt/tm/ltm/data-group/internal')
    backup_data(datagroups_data, 'datagroups/non-prod')

    irules_data = fetch_data(F5_NON_PROD + '/mgmt/tm/ltm/rule')
    backup_data(irules_data, 'irules/non-prod')

    virtualservers_data = fetch_data(F5_NON_PROD + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    backup_data(virtualservers_data, 'virtualservers/non-prod')

    datagroups_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/data-group/internal')
    backup_data(datagroups_data, 'datagroups/prod-ptc')

    irules_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/rule')
    backup_data(irules_data, 'irules/prod-ptc')

    virtualservers_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    backup_data(virtualservers_data, 'virtualservers/prod-ptc')

    # datagroups_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/data-group/internal')
    # backup_data(datagroups_data, 'datagroups/prod-ctc')

    irules_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/rule')
    backup_data(irules_data, 'irules/prod-ctc')

    virtualservers_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    backup_data(virtualservers_data, 'virtualservers/prod-ctc')

def git_clone(repository_url, target_directory):
    try:
        # Temporarily disable SSL verification
        os.environ['GIT_SSL_NO_VERIFY'] = 'true'

        # Clone the repository
        repo = Repo.clone_from(repository_url, target_directory)

        # Re-enable SSL verification
        del os.environ['GIT_SSL_NO_VERIFY']
        print(f"Repository cloned successfully to {target_directory}")
        return repo
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return None

def git_pull(repo):
    try:
        repo.remotes.origin.pull()
        print("Changes pulled from remote repository.")
        return True
    except Exception as e:
        print(f"Error pulling changes from remote repository: {e}")
        return False

def add_and_commit_changes(repo, commit_message):
    try:
        repo.git.add(all=True)
        repo.index.commit(commit_message)
        print("Changes staged and committed locally.")
        return True
    except Exception as e:
        print(f"Error staging and committing changes locally: {e}")
        return False

def push_changes(repo):
    try:
        # Temporarily disable SSL verification
        os.environ['GIT_SSL_NO_VERIFY'] = 'true'

        # Push changes to the remote repository
        repo.remotes.origin.push()

        # Re-enable SSL verification
        del os.environ['GIT_SSL_NO_VERIFY']
        print("Changes pushed to remote repository.")
        return True
    except Exception as e:
        print(f"Error pushing changes to remote repository: {e}")
        return False

def check_for_changes(repo):
    try:
        if repo.is_dirty(untracked_files=True) or repo.untracked_files:
            print("Local changes detected.")
            return True
        else:
            print("No local changes detected.")
            return False
    except Exception as e:
        print(f"Error checking for local changes: {e}")
        return False

def get_last_commit_date(repo):
    try:
        last_commit = repo.head.commit
        last_commit_date = last_commit.committed_datetime
        last_commit_id = last_commit.hexsha
        print(f"Last commit date: {last_commit_date}")
        return last_commit_date,last_commit_id
    except Exception as e:
        print(f"Error retrieving last commit date: {e}")
        return None, None

def send_email(attachment_path,build_number, smtp_server, sender_email, recipient_email, subject, content, body_as_html=False, attachment=None):
    try:
        # Set up the email message
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ', '.join(recipient_email)
        message['Subject'] = subject
        repo_path = 'f5_backup/'

        # Attach the email body
        html_content = MIMEText(content, "html")
        message.attach(html_content)

        # Attach the build log file as an attachment
        with open(attachment_path, "rb") as file:
            attach_part = MIMEApplication(file.read(), Name=f"build_log_{build_number}.txt")
        attach_part['Content-Disposition'] = f'attachment; filename="build_log_{build_number}.txt"'
        message.attach(attach_part)

        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server) as server:
            server.send_message(message)  # Send the email

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_latest_build_number(jenkins_url, job_name, project_name):
    try:
        # Construct the URL for the Jenkins job
        url = f"{jenkins_url}/job/{project_name}/job/{job_name}/job/master/api/json"

        # Send a GET request to the Jenkins API
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            job_info = response.json()

            # Extract the latest build number
            latest_build_number = job_info['builds'][0]['number']

            return latest_build_number
        else:
            print(f"Failed to retrieve latest build number: {response.text}")
            return None
    except Exception as e:
        print(f"Error getting latest build number: {e}")
        return None

def download_build_log(jenkins_url, job_name, build_number,project_name):
    # Construct the URL for the build log
    build_log_url = f"{jenkins_url}/job/{project_name}/job/{job_name}/job/master/{build_number}/consoleText"

    try:
        # Make a GET request to download the build log
        response = requests.get(build_log_url)
        if response.status_code == 200:
            # Write the response content (build log) to a file
            with open(f"build_{build_number}_log.txt", "w") as file:
                file.write(response.text)
            print(f"Build log for build {build_number} downloaded successfully.")
            return f"build_{build_number}_log.txt"
        else:
            print(f"Failed to download build log for build {build_number}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading build log: {e}")
        return None

def main():
    # Replace these variables with the actual repository URL and target directory
    repository_url = 'https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_backup.git'
    target_directory = 'f5_backup'

    # Clone the Git repository
    repo = git_clone(repository_url, target_directory)
    if repo is None:
        return
    # Open the Git repository
    # repo = Repo(target_directory)
    run()
    last_commit_date, last_commit_id= get_last_commit_date(repo)
    if last_commit_date is None:
        print("No last commit date available due to empty repository.")
    # Check for local changes
    print("last commit id")
    print(last_commit_id)
    if check_for_changes(repo):
        # Add and commit changes locally
        tracked_files = repo.untracked_files
        if add_and_commit_changes(repo, 'Automated commit - Changes detected'):
            # Push changes to the remote repository
            if push_changes(repo):
              print("Process completed successfully.")
              # Example usage
              smtp_server = 'os-smtpp702.prod.mdgapp.net'
              sender_email = 'sonali.jain@ihsmarkit.com'
              recipient_email = ['MD-MercuryTeam@ihsmarkit.com']
              subject = 'F5 CONFIGURATION CHANGES'
              jenkins_url = 'https://jenkins.dev.tools.mdgapp.net/'
              project_name = 'Mercury-Devops'
              job_name = 'f5_automation'
              latest_build_number = get_latest_build_number(jenkins_url, job_name, project_name)
              build_url = f"https://jenkins.dev.tools.mdgapp.net/job/Mercury-Devops/job/f5_automation/job/master/{latest_build_number}/"
              print("latest: ",latest_build_number)
              attachment_path = download_build_log(jenkins_url, job_name, latest_build_number,project_name)
              print(attachment_path)
              content = """
  <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jenkins Build Notification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333;
        }}

        .container {{
            max-width: 600px;
            margin: 20px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            color: #009900;
        }}

        p {{
            margin-bottom: 15px;
        }}
    </style>
</head>

<body>
    <div class="container">
        <h1>F5 Configuration Build Notification</h1>
        <p>Your Jenkins build has been successfully executed.</p>
        <p><b>Build Details:</b></p>
        <ul>
            <li><b>Build Number:</b> {}</li>
            <li><b>Build Status:</b> Success</li>
            <li><b>Build URL:</b> <a href="{}">View Build</a></li>
            <li><b>Configuration URL:</b> <a href="https://stash.mgmt.local/projects/MERC/repos/f5_backup/commits/{}">View
                    Config</a></li>
        </ul>
        <p><b>Updated in f5 Configuration</b></p>
            <pre style="color:green;">{}</pre>
    </div>
</body>

</html>
       """.format(latest_build_number, build_url, last_commit_id, '\n'.join('<span style="color:blue;">{}</span>'.format(file) for file in tracked_files))
              send_email(attachment_path,latest_build_number, smtp_server, sender_email, recipient_email, subject, content, body_as_html=True)
              print("content:  /n",content)
              print("latest: ",latest_build_number)
            else:
                print("Failed to push changes to remote repository.")
        else:
            print("Failed to stage and commit changes locally.")
    else:
        print("No local changes detected in file.")

if __name__ == "__main__":
    main()


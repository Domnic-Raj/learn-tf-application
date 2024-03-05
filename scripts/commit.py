import subprocess
import os
from git import Repo
import datetime
import json
import pathlib
import requests
from git import GitCommandError


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

    # irules_data = fetch_data(F5_NON_PROD + '/mgmt/tm/ltm/rule')
    # backup_data(irules_data, 'irules/non-prod')

    # virtualservers_data = fetch_data(F5_NON_PROD + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    # backup_data(virtualservers_data, 'virtualservers/non-prod')
    
    # datagroups_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/data-group/internal')
    # backup_data(datagroups_data, 'datagroups/prod-ptc')

    # irules_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/rule')
    # backup_data(irules_data, 'irules/prod-ptc')

    # virtualservers_data = fetch_data(F5_PROD_PTC + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    # backup_data(virtualservers_data, 'virtualservers/prod-ptc')

    # datagroups_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/data-group/internal')
    # backup_data(datagroups_data, 'datagroups/prod-ctc')

    # irules_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/rule')
    # backup_data(irules_data, 'irules/prod-ctc')

    # virtualservers_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/virtual/?expandSubcollections=true&%24select=name,enabled,partition,pool,profilesReference/items/name,rules')
    # backup_data(virtualservers_data, 'virtualservers/prod-ctc')
     
def get_last_commit_date(repo):
    if not repo.heads:
        print("Repository is empty. No commits found.")
        return None
    last_commit = repo.head.commit
    return last_commit.committed_datetime

def check_for_changes(repo):
    try:
        # Fetch changes from the remote repository
        repo.remotes.origin.fetch()
        if not repo.remotes.origin.refs:
            print("Remote repository is empty. Skipping pull operation.")
            return True
        # Pull changes from the remote repository
        repo.remotes.origin.pull()

        # Check if there are any changes in the local repository
        if repo.is_dirty(untracked_files=True) or repo.untracked_files:
            return True
        else:
            return False
    except GitCommandError as e:
        print(f"Error pulling changes from origin: {e}")
        return False
    except Exception as e:
        print(f"Error checking for changes: {e}")
        return False
def update_repository(repo):
    repo.remotes.origin.pull()
    repo.remotes.origin.update()
    print("Repository updated.")

def save_metadata(repo, last_commit_date):
    with open("metadata.txt", "w") as file:
        file.write(f"Last commit date: {last_commit_date}\n")
        file.write("Update timestamp: {}\n".format(datetime.datetime.now()))

def set_remote_origin(url):
    try:
        subprocess.run(['git', 'remote', 'set-url', 'origin', url], check=True)
        print("Remote origin URL set successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting remote origin URL: {e}")
def push_changes(repo):
    repo.remotes.origin.push()
    print("Changes pushed to remote repository.")

def add_and_commit_changes(repo):
    repo.git.add(all=True)
    repo.git.commit('-m', 'Automated commit - Changes detected')

def git_clone(repository_url, target_directory):
    try:
        os.environ['GIT_SSL_NO_VERIFY'] = 'true'
        repo = Repo.clone_from(repository_url, target_directory)
        print(f"Repository cloned successfully to {target_directory}")
    except Exception as e:
        print(f"Error cloning repository: {e}")

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(smtp_server, sender_email, recipient_email, subject, content, body_as_html=False, attachment=None):
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
        # Connect to the SMTP server
        with smtplib.SMTP(smtp_server) as server:
            server.send_message(message)  # Send the email

        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_tracked_files_from_repo(repo_path):
    try:
        # Change directory to the cloned repository
        os.chdir(repo_path)

        # Run the git ls-files command to list tracked files
        git_ls_files_output = subprocess.check_output(['git', 'ls-files'], universal_newlines=True)
        
        # Split the output into lines
        tracked_files = git_ls_files_output.strip().split('\n')
        
        return tracked_files
    
    except subprocess.CalledProcessError:
        print("Error: Git command failed")
        return None


def main():
    repository_url = 'https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_backup.git'

    # Replace 'path/to/your/target/directory' with the path where you want to clone the repository
    target_directory = 'f5_backup'

    git_clone(repository_url, target_directory)
    # Replace 'path/to/your/repo' with the actual path to your Git repository
    repo_path = 'f5_backup/'

    # Open the Git repository
    repo = Repo(repo_path)

    # Get the date of the last commit
    last_commit_date = get_last_commit_date(repo)
    if last_commit_date is not None:
        print(f"Last commit date: {last_commit_date}")
    else:
        print("No last commit date available due to empty repository.")

# Use subprocess to execute the Node.js script
    try:
        run()
    except subprocess.CalledProcessError as e:
        print(f"Error executing Node.js script: {e}")

    # Check for changes
    if check_for_changes(repo):
        print("Changes detected. Updating repository...")
        # status = git_status(repo_path)

        # Add and commit changes
        add_and_commit_changes(repo)

        # Save metadata
        save_metadata(repo, last_commit_date)
        set_remote_origin(repository_url)
        # new_repo_path = "../f5_backup"
        tracked_files = get_tracked_files_from_repo(repo_path)
        push_changes(repo)
        # Example usage
        smtp_server = 'os-smtpp702.prod.mdgapp.net'
        sender_email = 'sonali.jain@ihsmarkit.com'
        recipient_email = ['sonali.jain@ihsmarkit.com','sachin.kumar4@ihsmarkit.com']
        subject = 'BUILD TEST MAIL'
        content = """
<html>
  <body>
  <p>This is a test email for f5 config update.\n https://stash.mgmt.local/projects/MERC/repos/f5_backup/browse.</p>
  <p>Changes in files.</p>
    <pre style="color:green;">{}</pre>
  </body>
</html>
""".format('\n'.join('<span style="color:blue;">{}</span>'.format(file) for file in tracked_files))
        print("Tracked files:")
        print(tracked_files)
        send_email(smtp_server, sender_email, recipient_email, subject, content, body_as_html=True)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()

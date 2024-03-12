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

    datagroups_data = fetch_data(F5_PROD_CTC + '/mgmt/tm/ltm/data-group/internal')
    backup_data(datagroups_data, 'datagroups/prod-ctc')

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
        print(f"Last commit date: {last_commit_date}")
        return last_commit_date
    except Exception as e:
        print(f"Error retrieving last commit date: {e}")
        return None

def get_tracked_files_from_repo(repo_path):
    try:
        # Change directory to the cloned repository
        os.chdir(repo_path)

        # Run the git ls-files command to list tracked files
        git_ls_files_output = subprocess.check_output(['git', 'diff', '--cached', '--name-only'], universal_newlines=True)
        
        # Split the output into lines
        tracked_files = git_ls_files_output.strip().split('\n')
        
        return tracked_files
    
    except subprocess.CalledProcessError:
        print("Error: Git command failed")
        return None
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
    last_commit_date = get_last_commit_date(repo)
    if last_commit_date is None:
        print("No last commit date available due to empty repository.")
    # Check for local changes
    if check_for_changes(repo):
        # Add and commit changes locally
        if add_and_commit_changes(repo, 'Automated commit - Changes detected'):
            # Check for changes in the remote repository and pull if necessary
            #if git_pull(repo):
                # Push changes to the remote repository
            tracked_files = get_tracked_files_from_repo(target_directory)
            print("Tracked files:")
            print(tracked_files)
            if push_changes(repo):
              print("Process completed successfully.")
              # Example usage
              smtp_server = 'os-smtpp702.prod.mdgapp.net'
              sender_email = 'sonali.jain@ihsmarkit.com'
              recipient_email = ['sonali.jain@ihsmarkit.com']
              subject = 'F5 CONFIGURATION CHANGES'
              content = """
                                    <html>
                                      <body>
                                      <p>This is a test email for f5 config update.\n https://stash.mgmt.local/projects/MERC/repos/f5_backup/browse.</p>
                                      <p>Changes in files.</p>
                                        <pre style="color:green;">{}</pre>
                                      </body>
                                    </html>
                                    """.format('\n'.join('<span style="color:blue;">{}</span>'.format(file) for file in tracked_files))
              send_email(smtp_server, sender_email, recipient_email, subject, content, body_as_html=True)
            else:
                print("Failed to push changes to remote repository.")
        else:
            print("Failed to stage and commit changes locally.")
    else:
        print("No local changes detected in file.")

if __name__ == "__main__":
    main()


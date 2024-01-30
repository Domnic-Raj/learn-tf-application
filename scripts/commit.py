import subprocess
import os
from git import Repo
import datetime

def get_last_commit_date(repo):
    last_commit = repo.head.commit
    return last_commit.committed_datetime

def check_for_changes(repo):
    repo.remotes.origin.pull()
    return repo.is_dirty(untracked_files=True)

def update_repository(repo):
    repo.remotes.origin.pull()
    repo.remotes.origin.update()
    print("Repository updated.")

def save_metadata(repo, last_commit_date):
    with open("metadata.txt", "w") as file:
        file.write(f"Last commit date: {last_commit_date}\n")
        file.write("Update timestamp: {}\n".format(datetime.datetime.now()))

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

def main():
    repository_url = 'https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_config.git'

    # Replace 'path/to/your/target/directory' with the path where you want to clone the repository
    target_directory = 'f5_config'

    git_clone(repository_url, target_directory)
    # Replace 'path/to/your/repo' with the actual path to your Git repository
    repo_path = 'f5_config/'

    # Open the Git repository
    repo = Repo(repo_path)

    # Get the date of the last commit
    last_commit_date = get_last_commit_date(repo)
    print(f"Last commit date: {last_commit_date}")
        # Replace 'path/to/your/node/script.js' with the actual path to your Node.js script
    node_script_path = 'sample-project-test/backup/index.js'

# Use subprocess to execute the Node.js script
    try:
        subprocess.run(['node', node_script_path], check=True)
        print("Node.js script executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing Node.js script: {e}")

    # Check for changes
    if check_for_changes(repo):
        print("Changes detected. Updating repository...")

        # Add and commit changes
        add_and_commit_changes(repo)

        # Save metadata
        save_metadata(repo, last_commit_date)

        # Push changes to remote repository
        push_changes(repo)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
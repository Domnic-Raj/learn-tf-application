import unittest
from unittest.mock import patch, MagicMock
from scripts.commit import add_and_commit_changes, GitCommandError

class TestAddAndCommitChanges(unittest.TestCase):
    @patch('scripts.commit.Repo')
    def test_add_and_commit_changes_success(self, mock_repo):
        # Mock repository
        mock_repo_instance = MagicMock()
        mock_repo_instance.git.add.return_value = None
        mock_repo_instance.git.commit.return_value = None
        mock_repo.return_value = mock_repo_instance

        # Call the function
        add_and_commit_changes(mock_repo_instance, "Test Commit")

        # Assertions
        mock_repo_instance.git.add.assert_called_once_with(all=True)
        mock_repo_instance.git.commit.assert_called_once_with('-m', 'Automated commit - Changes detected')

    # @patch('commit.Repo')
    # def test_add_and_commit_changes_git_command_error(self, mock_repo):
    #     # Mock a GitCommandError
    #     mock_repo_instance = MagicMock()
    #     mock_repo_instance.git.add.side_effect = GitCommandError('git add', 1, 'exit code(1)')
    #     mock_repo.return_value = mock_repo_instance

    #     # Call the function
    #     add_and_commit_changes(mock_repo_instance)

    #     # Assertions
    #     # You may want to assert logging or other handling of the error

if __name__ == '__main__':
    unittest.main()

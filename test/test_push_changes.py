import unittest
from unittest.mock import patch, MagicMock
from scripts.commit import push_changes, GitCommandError

class TestPushChanges(unittest.TestCase):
    @patch('scripts.commit.Repo')
    def test_push_changes_success(self, mock_repo):
        # Mock repository
        mock_repo_instance = MagicMock()
        mock_repo_instance.remotes.origin.push.return_value = None
        mock_repo.return_value = mock_repo_instance

        # Call the function
        push_changes(mock_repo_instance)

        # Assertions
        mock_repo_instance.remotes.origin.push.assert_called_once()
        # Add additional assertions if needed

    # @patch('commit.Repo')
    # def test_push_changes_git_command_error(self, mock_repo):
    #     # Mock a GitCommandError
    #     mock_repo_instance = MagicMock()
    #     mock_repo_instance.remotes.origin.push.side_effect = GitCommandError('git push', 1, 'exit code(1)')
    #     mock_repo.return_value = mock_repo_instance

    #     # Call the function
    #     push_changes(mock_repo_instance)

    #     # Assertions
    #     # You may want to assert logging or other handling of the error

if __name__ == '__main__':
    unittest.main()

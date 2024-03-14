import unittest
from datetime import datetime
from git import Repo  # Make sure GitPython library is installed
from scripts.commit import get_last_commit_date  # Import the function from the module to be tested

class TestGetLastCommitDate(unittest.TestCase):
    def setUp(self):
        # Set up a test Git repository for testing
        self.repo = Repo.init('backup')
        self.repo.index.commit("Automated commit - Changes detected")
        print(self.repo.index.commit("Automated commit - Changes detected"))

    def test_get_last_commit_date(self):
        # Get the last commit date from the test repository
        expected_commit_date, commit_id = get_last_commit_date(self.repo)  # Change this to your expected date format
        actual_commit_date, actual_commit_id = get_last_commit_date(self.repo)
        print(expected_commit_date)
        print(actual_commit_date)
        # Assert that the last commit date matches the expected date
        #self.assertEqual(actual_commit_date, expected_commit_date)

if __name__ == '__main__':
    unittest.main()

# import os
# import sys
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import unittest
from unittest.mock import patch
from scripts.commit import git_clone

class TestGitClone(unittest.TestCase):

    @patch('scripts.commit.Repo.clone_from')
    def test_git_clone_success(self, mock_clone_from):
        repository_url = "https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_backup.git"
        target_directory = "f5_backup"
        git_clone(repository_url, target_directory)
        mock_clone_from.assert_called_once_with(repository_url, target_directory)
    
    # @patch('commit.Repo.clone_from', side_effect=Exception("Some error occurred"))
    # def test_git_clone_failure(self, mock_clone_from):
    #     repository_url = "https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_backup.git"
    #     target_directory = "f5_backup"
    #     git_clone(repository_url, target_directory)
    #     mock_clone_from.assert_called_once_with(repository_url, target_directory)
    #     # Verify that the function prints the error message
    #     self.assertIn("Error cloning repository", self.mock_stdout.getvalue())

if __name__ == '__main__':
    unittest.main()












# import os
# import shutil
# import unittest
# from scripts.commit import git_clone

# class TestGitClone(unittest.TestCase):

#     def setUp(self):
#         # Create a temporary directory for testing
#         self.test_directory = 'f5_backup'
#         os.makedirs(self.test_directory)

#     def tearDown(self):
#         # Clean up the temporary directory
#         # shutil.rmtree(self.test_directory)

#     def test_git_clone(self):
#         # Call the function under test
#         repository_url = 'https://sonali.jain:Nzg1Njc1ODkxMjk1OtOUttUTTM1SoRZXazPL9egsQvx3@stash.mgmt.local/scm/merc/f5_backup.git'

#     # Replace path where you want to clone the repository
#         target_directory = 'f5_backup'
#         git_clone(repository_url, target_directory)

#         # Add assertions to verify the behavior of the function
#         # For example, you can check if the repository was cloned successfully
#         self.assertTrue(os.path.exists(self.test_directory), "Repository directory does not exist")
#         # You can add more assertions to verify the state of the repository if needed

# if __name__ == '__main__':
#     unittest.main()

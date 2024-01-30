## **F5 Configuration Backup and Monitoring Automation**
We've leveraged JavaScript to streamline F5 backup configuration downloads across both our non-production and production environments. The scripts reside in our f5_scripts repository.

To maintain the integrity of our configurations, we've developed a Python script. This script not only checks the timestamp of the last configuration commit but also compares the latest backup with fresh files. Any detected changes trigger an automatic push to our Bitbucket repository, hosted in the f5_backup repository.

Our Jenkins pipeline, as defined in the Jenkinsfile, orchestrates the backup script execution across Jenkins agents. Detailed logs and information regarding the automated backup job can be accessed here.

Repository Links:
f5_scripts Repository
f5_backup Repository
Please feel free to explore these repositories for deeper insights and potential contributions.

Should you have any questions or require further assistance, don't hesitate to reach out.

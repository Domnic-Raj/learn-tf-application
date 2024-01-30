# F5 Configuration Backup and Monitoring Automation

We've leveraged JavaScript to streamline F5 backup configuration downloads across both our non-production and production environments. The scripts reside in our [`f5_scripts`](https://stash.mgmt.local/projects/MERC/repos/f5_scripts/browse) repository.

To maintain the integrity of our configurations, we've developed a Python script. This script not only checks the timestamp of the last configuration commit but also compares the latest backup with fresh files. Any detected changes trigger an automatic push to our Bitbucket repository, hosted in the [`f5_backup`](https://stash.mgmt.local/projects/MERC/repos/f5_backup/browse?at=refs%2Fheads%2Fmaster) repository.

Our Jenkins pipeline, as defined in the `Jenkinsfile`, orchestrates the backup script execution across Jenkins agents. Detailed logs and information regarding the automated backup job can be accessed [here](https://jenkins.dev.tools.mdgapp.net/job/Mercury-Devops/job/f5_automation/job/master/20/).

We have established a recurring Jenkins build schedule to ensure the continuous synchronization of our configurations. This schedule, implemented through Jenkins cron triggers, executes the build process once daily, thus maintaining the up-to-date status of our configurations.

## Repository Links:
- [f5_scripts Repository](https://stash.mgmt.local/projects/MERC/repos/f5_scripts/browse)
- [f5_backup Repository](https://stash.mgmt.local/projects/MERC/repos/f5_backup/browse?at=refs%2Fheads%2Fmaster)

Please feel free to explore these repositories for deeper insights.

Should you have any questions or require further assistance, don't hesitate to reach out [Mercury Team](MD-MercuryTeam@ihsmarkit.com)



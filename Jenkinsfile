pipeline {
    agent {
        label 'linux_bbt'
    }
    stages {
        stage('Clone') {
            steps {
                checkout scm
            }
        }
       stage('script') {
            steps {
                sh '/var/lib/jenkins/workspace/ury-Devops_f5_automation_feature@tmp/f5_backup.sh'
            }
        }
      stage('build') { 
            steps {
                sh "echo 'building ...'"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}

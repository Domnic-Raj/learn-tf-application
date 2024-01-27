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
                sh '/var/lib/jenkins/workspace/Mercury-Devops/f5_aut/_build_scripts/f5_backup.sh'
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

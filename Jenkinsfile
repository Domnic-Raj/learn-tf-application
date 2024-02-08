pipeline {
  	triggers {
        cron('0 20 */1 * *')
    }
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
                sh 'chmod +x ./scripts/commit.py'
                sh 'python3 ./scripts/commit.py'
            }
        }
      stage('build') { 
            steps {
                sh "echo 'Configuration updated ...'"
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}

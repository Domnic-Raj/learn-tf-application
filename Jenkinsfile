pipeline {
  	triggers {
        cron('0 0 */3 * *')
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
                sh "npm install axios"
                sh 'python3 ./scripts/commit.py'
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

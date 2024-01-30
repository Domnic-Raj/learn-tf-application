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
      stage('git clone'){
        steps{
          sh "git clone https://stash.mgmt.local/scm/merc/sonali-test.git"
        }
      }
       stage('script') {
            steps {
                sh 'chmod +x ./scripts/commit.py'
                sh "python3 ./scripts/commit.py"
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

String BRANCH_NAME = 'master'
pipeline {
  	triggers {
        sh 'echo "$env.BRANCH_NAME"'
        cron((BRANCH_NAME == 'master' || BRANCH_NAME == 'main')?'25 14 */1 * *' : '')
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
        stage('Test Trigger')
        {
            steps{
                sh 'python3 -m unittest discover -s test'
            }
        }
       stage('Script Execution') {
        when {
                branch 'master'
            }
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
            echo 'This will always run'
        }
        success {
            echo 'This will run only if successful'
        }
        failure {
          	 emailext (
				mimeType: 'text/html',
				subject: "ERROR CI: Project name -> ${env.JOB_NAME}",
				to: "sonali.jain@spglobal.com,sachin.kumar4@spglobal.com",
				body: "<b>Example</b><br/><br/>Project: ${env.JOB_NAME}<br/>Build Number: ${env.BUILD_NUMBER}<br/>URL de build: ${env.BUILD_URL}"
						)
        }
        unstable {
            echo 'This will run only if the run was marked as unstable'
        }
        changed {
            echo 'This will run only if the state of the Pipeline has changed'
            echo 'For example, if the Pipeline was previously failing but is now successful'
        }
    }
}

pipeline {

agent any

tools {
    dependencyCheck 'OWASP'
}

stages {

    stage('Clean Workspace') {
        steps {
            cleanWs()
        }
    }

    // stage('Checkout') {
    //     steps {
    //         git branch: 'main',
    //             url: 'https://github.com/khushbhat/blood_system.git'
    //     }
    // }

    stage('Verify Environment') {
        steps {
            sh '''
            docker --version
            docker compose version
            python3 --version
            '''
        }
    }

    // stage('OWASP Dependency Check') {
    //     steps {
    //         dependencyCheck(
    //             odcInstallation: 'OWASP',
    //             additionalArguments: '--scan . --format ALL'
    //         )
    //     }
    // }

    stage('Publish OWASP Report') {
        steps {
            dependencyCheckPublisher(
                pattern: '**/dependency-check-report.xml'
            )
        }
    }

    stage('SonarQube Analysis') {
        steps {
            withSonarQubeEnv('sonarqube') {
                sh '''
                sonar-scanner
                '''
            }
        }
    }

    stage('Stop Existing Containers') {
        steps {
            sh '''
            docker compose down || true
            '''
        }
    }

    stage('Build Containers') {
        steps {
            sh '''
            docker compose build
            '''
        }
    }

    stage('Deploy Containers') {
        steps {
            sh '''
            docker compose up -d
            '''
        }
    }

    stage('Wait For Startup') {
        steps {
            sh '''
            sleep 30
            '''
        }
    }

    stage('Health Check') {
        steps {
            sh '''
            curl -f http://localhost:5004/ping
            '''
        }
    }

    stage('Container Verification') {
        steps {
            sh '''
            docker ps
            docker compose ps
            '''
        }
    }
}

post {

    success {
        echo 'Blood System deployed successfully'
    }

    failure {
        echo 'Deployment failed'
    }
}

}

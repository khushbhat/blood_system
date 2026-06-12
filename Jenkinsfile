pipeline {

agent any

stages {

    // stage('Checkout') {
    //     steps {
    //         git branch: 'main',
    //             url: 'https://github.com/khushbhat/blood_system.git'
    //     }
    // }
    stage("adding a startup hello"){
        steps {
            echo "Hello, Jenkins! Starting the Blood System deployment pipeline."
        }
    }
    stage('Start Docker Desktop') {
        steps {
            sh '''
            if ! docker info > /dev/null 2>&1; then
                echo "Docker Desktop is not running. Starting Docker Desktop..."
                open -a Docker

                echo "Waiting for Docker Desktop to start..."
                while ! docker info > /dev/null 2>&1; do
                    sleep 5
                done
            else
                echo "Docker Desktop is already running."
            fi
            '''
        }
    }

    stage('Verify Environment') {
        steps {
            sh '''
            docker --version
            docker compose version
            python3 --version
            '''
        }
    }

    stage('Trivy Filesystem Scan') {
        steps {
            sh '''
            docker run --rm \
            -v "$PWD:/project" \
            aquasec/trivy fs /project
            '''
        }
    }

    stage('SonarQube Analysis') {
        steps {
        script {
            def scannerHome = tool 'sonarqube'
                    withSonarQubeEnv('sonarqube') {
                        sh "${scannerHome}/bin/sonar-scanner"
                    }
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

    stage('Debug Workspace') {
        steps {
            sh '''
            pwd
            ls -la
            '''
        }
    }

    stage('Trivy Image Scan') {
        steps {
            sh '''
            docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image blood_system-web:latest
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

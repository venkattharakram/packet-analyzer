pipeline {
    agent any
    environment {
        DOCKER_REGISTRY = 'yourdockerhubusername'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                }
            }
        }
        stage('Build Docker Images') {
            steps {
                script {
                    def modules = ['parser-service', 'persistor-service', 'analyzer-service', 'ui-service']
                    for (module in modules) {
                        dir(module) {
                            sh "docker build -t ${DOCKER_REGISTRY}/${module}:latest ."
                        }
                    }
                }
            }
        }
        stage('Push Docker Images') {
            steps {
                script {
                    def modules = ['parser-service', 'persistor-service', 'analyzer-service', 'ui-service']
                    for (module in modules) {
                        sh "docker push ${DOCKER_REGISTRY}/${module}:latest"
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                sh 'docker-compose down'
                sh 'docker-compose pull'
                sh 'docker-compose up -d'
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}

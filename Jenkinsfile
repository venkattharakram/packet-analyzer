pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = "639799575784"          // 🔑 replace if different
        AWS_REGION     = "ca-central-1"
        ECR_URL        = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/packet-analyzer"
        BRANCH_NAME    = "Docker-features-v3-Ram3"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${BRANCH_NAME}", url: 'https://github.com/vivekgshan/packet-analyzer.git'
            }
        }

        stage('AWS ECR Login') {
            steps {
                sh '''
                  aws ecr get-login-password --region ${AWS_REGION} \
                    | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
                '''
            }
        }

        stage('Build Images') {
            steps {
                sh '''
                  echo "🐳 Building images using docker-compose..."
                  docker-compose -f docker-compose.yml build
                '''
            }
        }

        stage('Tag & Push Images') {
            steps {
                sh '''
                  echo "🏷️ Tagging & pushing images to ECR..."

                  docker tag packet-analyzer-capture-service:latest   ${ECR_URL}/capture-service:latest
                  docker push ${ECR_URL}/capture-service:latest

                  docker tag packet-analyzer-parser-service:latest    ${ECR_URL}/parser-service:latest
                  docker push ${ECR_URL}/parser-service:latest

                  docker tag packet-analyzer-persistor-service:latest ${ECR_URL}/persistor-service:latest
                  docker push ${ECR_URL}/persistor-service:latest

                  docker tag packet-analyzer-analyzer-service:latest  ${ECR_URL}/analyzer-service:latest
                  docker push ${ECR_URL}/analyzer-service:latest

                  docker tag packet-analyzer-ui-service:latest        ${ECR_URL}/ui-service:latest
                  docker push ${ECR_URL}/ui-service:latest
                '''
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                  echo "🚀 Deploying updated stack..."
                  docker-compose -p packet-analyzer -f docker-compose.yml down -v --remove-orphans || true
                  docker-compose -p packet-analyzer -f docker-compose.yml up -d
                '''
            }
        }
    }

    post {
        always {
            sh '''
              echo "🧹 Cleaning up unused Docker resources..."
              docker system prune -f
            '''
        }
    }
}

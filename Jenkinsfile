pipeline {
    agent any
    
    environment {
        DOCKER_HUB_REPO = 'your-username/delivery-prediction'
        DOCKER_HUB_CREDENTIALS = 'docker-hub-credentials'
        KUBECONFIG_CREDENTIALS = 'kubeconfig-credentials'
        SONAR_PROJECT_KEY = 'delivery-prediction'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/your-username/your-repo.git'
            }
        }
        
        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install -r requirements.txt
                    pip install pytest pytest-cov flake8 black
                '''
            }
        }
        
        stage('Code Quality Analysis') {
            parallel {
                stage('Linting') {
                    steps {
                        sh '''
                            source venv/bin/activate
                            flake8 app/ --count --select=E9,F63,F7,F82 --show-source --statistics
                            flake8 app/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        '''
                    }
                }
                
                stage('Code Formatting') {
                    steps {
                        sh '''
                            source venv/bin/activate
                            black --check app/
                        '''
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                sh '''
                    source venv/bin/activate
                    python -m pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    publishCoverage adapters: [cobertura('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    source venv/bin/activate
                    pip install safety bandit
                    safety check
                    bandit -r app/
                '''
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    def image = docker.build("${DOCKER_HUB_REPO}:${BUILD_NUMBER}")
                    def latestImage = docker.build("${DOCKER_HUB_REPO}:latest")
                }
            }
        }
        
        stage('Docker Security Scan') {
            steps {
                sh '''
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        -v $(pwd):/app aquasec/trivy:latest image ${DOCKER_HUB_REPO}:${BUILD_NUMBER}
                '''
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', DOCKER_HUB_CREDENTIALS) {
                        docker.image("${DOCKER_HUB_REPO}:${BUILD_NUMBER}").push()
                        docker.image("${DOCKER_HUB_REPO}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                script {
                    sh '''
                        kubectl apply -f k8s/staging/ --kubeconfig=$KUBECONFIG_CREDENTIALS
                        kubectl set image deployment/delivery-app delivery-app=${DOCKER_HUB_REPO}:${BUILD_NUMBER} -n staging
                        kubectl rollout status deployment/delivery-app -n staging
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            when {
                branch 'develop'
            }
            steps {
                sh '''
                    source venv/bin/activate
                    python -m pytest tests/integration/ --base-url=http://staging.your-domain.com
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                input message: 'Deploy to Production?', ok: 'Deploy'
                script {
                    sh '''
                        kubectl apply -f k8s/production/ --kubeconfig=$KUBECONFIG_CREDENTIALS
                        kubectl set image deployment/delivery-app delivery-app=${DOCKER_HUB_REPO}:${BUILD_NUMBER} -n production
                        kubectl rollout status deployment/delivery-app -n production
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
            sh 'docker system prune -af'
        }
        
        failure {
            emailext (
                subject: "Pipeline Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}",
                to: "team@yourcompany.com"
            )
        }
        
        success {
            emailext (
                subject: "Pipeline Success: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build successful. Deployed version ${env.BUILD_NUMBER}",
                to: "team@yourcompany.com"
            )
        }
    }
}
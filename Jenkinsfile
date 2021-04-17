pipeline{
    agent any
    environment{
        dockerImage = ''
        registry = 'kevinshah/dockertest'
        registryCredential = 'docker'
    }
    stages{
        stage('Checkout'){
            steps{
                checkout([$class: 'GitSCM', branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/KevinShahgit/DevOps_IA1']]])
            }
        }
        stage('Docker Image'){
            steps{
                script{
                    dockerImage = docker.build registry
                }
            }
        }
        stage("Upload to DockerHub"){
            steps{
                script{
                    docker.withRegistry('', registryCredential){
                        dockerImage.push()
                    }   
                }
            }
        }
        stage('Docker Run') {
        steps{
            script {
                dockerImage.run("-p 8096:5000 --rm --name dockerTestContainer")
            }
        }
    }
    }
}
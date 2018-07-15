pipeline {
    agent {
        label 'master'
    }
    stages {
        stage('Build') {
            failFast true
            parallel {
                stage('macOS') {
                    agent {
                        label 'macOS'
                    }
                    environment {
                        CONAN_ARCHS = 'x86_64'
                    }
                    steps {
                        sh '''
                            conan remove "*" -f
                            python3 $PWD/build.py
                        '''
                    }
                }
                stage('Windows') {
                    agent {
                        label 'Windows&&vs14'
                    }
                    environment {
                        CONAN_ARCHS = 'x86'
                    }
                    steps {
                        sh '''
                            conan remove "*" -f
                            python $PWD/build.py
                        '''
                    }
                }
            }
        }
    }
}

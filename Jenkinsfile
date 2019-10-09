pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_STABLE_BRANCH_PATTERN = 'master'
        CONAN_BUILD_TYPES = 'Release'
        CONAN_ARCHS = 'x86_64'
    }
    stages {
        stage('Build') {
            failFast true
            parallel {
                stage('macOS') {
                    agent {
                        label 'macOS-10.14'
                    }
                    steps {
                        sh '''
                            conan remove "Qt/*@arobasmusic/*" -f
                            python3 $PWD/build.py
                        '''
                    }
                }
                stage('Windows') {
                    agent {
                        label 'Windows&&vs16'
                    }
                    steps {
                        sh '''
                            conan remove "Qt/*@arobasmusic/*" -f
                            python $PWD/build.py
                        '''
                    }
                }
            }
        }
    }
}

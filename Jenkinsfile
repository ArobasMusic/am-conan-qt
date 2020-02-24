pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_BUILD_TYPES = 'Release'
        CONAN_ARCHS = 'x86_64'
        CONAN_STABLE_BRANCH_PATTERN = 'release/*'
    }
    stages {
        stage('Build') {
            failFast true
            parallel {
                stage('macOS') {
                    agent {
                        label 'macOS&&clang-11.0'
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
                        label 'Windows&&vs14'
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

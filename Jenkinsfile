pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_BUILD_TYPES = 'Release'
        CONAN_ARCHS = 'x86_64'
    }
    stages {
        stage('Build') {
            failFast true
            parallel {
                stage('macOS') {
                    agent {
                        label 'macOS-10.13&&clang-9.1'
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

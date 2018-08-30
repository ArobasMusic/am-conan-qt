pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_BUILD_TYPES = 'Release'
        CONAN_UPLOAD = 'https://api.bintray.com/conan/arobasmusic/public-conan@True@arobasmusic_public'
    }
    stages {
        stage('Build') {
            failFast true
            parallel {
                stage('macOS') {
                    agent {
                        label 'macOS-10.13&&clang-9.1'
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

pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_USERNAME = 'amusic'
        CONAN_CHANNEL = 'stable'
        CONAN_REMOTES = 'http://conan.arobas-music.com'
        CONAN_UPLOAD = 'http://conan.arobas-music.com'
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
                        CONAN_APPLE_CLANG_VERSIONS = '7.0'
                        CONAN_ARCHS = 'x86_64'
                    }
                    steps {
                        sh 'python3 $PWD/build.py'
                    }
                }
                stage('Windows') {
                    agent {
                        label 'Windows&&vs14'
                    }
                    environment {
                        CONAN_ARCHS = 'x86'
                        CONAN_VISUAL_VERSIONS='14'
                        CONAN_VISUAL_RUNTIMES='MD,MDd'
                    }
                    steps {
                        sh 'python $PWD/build.py'
                    }
                }
            }
        }
    }
}

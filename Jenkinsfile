pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_CHANNEL = "testing"
        CONAN_STABLE_BRANCH_PATTERN = 'release/*'
        CONAN_BUILD_TYPES = 'Release'
        CONAN_ARCHS = 'x86_64'
        CONAN_REMOTES = "http://artifactory.arobas-music.com/artifactory/api/conan/conan@True@arobasmusic"
        CONAN_UPLOAD = "http://artifactory.arobas-music.com/artifactory/api/conan/conan@True@arobasmusic"
        CONAN_PASSWORD_AROBASMUSIC = credentials('arobas-music-artifactory-password')
        CONAN_LOGIN_USERNAME_AROBASMUSIC = "amusic"
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
                        CONAN_APPLE_CLANG_VERSIONS = "12.0"
                        CONAN_USER_HOME = "${env.WORKSPACE}"
                    }
                    steps {
                        sh '''
                            python3 -m venv .venv
                            source .venv/bin/activate
                            pip install conan==1.42.0 conan_package_tools
                            conan remove -f "*"
                            python "$PWD/build.py"
                        '''
                    }
                    post {
                        always {
                            sh '''
                                source .venv/bin/activate
                                conan remove -f "*"
                                rm -fr "$CONAN_USER_HOME/.conan"
                            '''
                        }
                    }
                }
                stage('Windows') {
                    agent {
                        label 'Windows'
                    }
                    environment {
                        CONAN_BASH_PATH = 'C:\\Program Files\\Git\\usr\\bin\\bash.exe'
                        CONAN_USER_HOME = "${env.WORKSPACE}"
                        CONAN_VISUAL_RUNTIMES = 'MD,MDd'
                        CONAN_VISUAL_VERSIONS = '16'
                    }
                    steps {
                        sh '''
                            python -m venv .venv
                            source .venv/Scripts/activate
                            pip install conan==1.42.0 conan_package_tools
                            conan remove -f "*"
                            python "$PWD/build.py"
                        '''
                    }
                    post {
                        always {
                            sh '''
                                source .venv/Scripts/activate
                                conan remove -f "*"
                                rm -fr "$CONAN_USER_HOME/.conan"
                            '''
                        }
                    }
                }
            }
        }
    }
}

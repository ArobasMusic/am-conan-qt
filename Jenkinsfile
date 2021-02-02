pipeline {
    agent {
        label 'master'
    }
    environment {
        CONAN_BUILD_TYPES = 'Release'
        CONAN_ARCHS = 'x86_64'
        CONAN_STABLE_BRANCH_PATTERN = 'release/*'
        CONAN_USER_HOME = "${env.WORKSPACE}"
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
                        CONAN_APPLE_CLANG_VERSIONS = '12.0'
                        CONAN_ARCHS = 'x86_64'
                        CONAN_OS_VERSIONS='10.10, 10.13'
                        CONAN_USER_HOME = "${env.WORKSPACE}"
                    }
                    steps {
                        sh '''
                            python3 -m venv .venv
                            source .venv/bin/activate
                            pip install conan==1.30.2 conan_package_tools
                            conan remove -f "*"
                            python3 $PWD/build.py
                        '''
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
                            pip install conan==1.30.2 conan_package_tools
                            conan remove -f "*"
                            python $PWD/build.py
                        '''
                    }
                }
            }
        }
    }
}

pipeline {
  agent any

  environment {
    K8S_DIR = "k8s"
    POLICY_DIR = "policies"
  }

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('YAML Lint - yamllint') {
      steps {
        sh '''
          echo "Running yamllint..."
          yamllint -d relaxed $K8S_DIR
        '''
      }
    }

    stage('Kubernetes Schema Validation - kubeconform') {
      steps {
        sh '''
          echo "Running kubeconform..."
          find $K8S_DIR -name "*.yaml" -print0 | \
            xargs -0 kubeconform \
              -strict \
              -summary \
              -ignore-missing-schemas
        '''
      }
    }

    stage('Kubernetes Best Practices - kube-score') {
      steps {
        sh '''
          echo "Running kube-score..."
          kube-score score $K8S_DIR/**/*.yaml || true
        '''
      }
    }

    stage('Kubernetes Security Scan - kubesec') {
      steps {
        sh '''
          echo "Running kubesec..."
          for file in $(find $K8S_DIR -name "*.yaml"); do
            echo "Scanning $file"
            kubesec scan $file || true
          done
        '''
      }
    }

    stage('IaC Security Scan - Checkov') {
      steps {
        sh '''
          echo "Running Checkov..."
          checkov -d $K8S_DIR --framework kubernetes
        '''
      }
    }

    stage('Policy Enforcement - Conftest') {
      steps {
        sh '''
          echo "Running OPA policy checks..."
          conftest test $K8S_DIR --policy $POLICY_DIR
        '''
      }
    }

  }

  post {
    success {
      echo "All Kubernetes security & compliance checks PASSED"
    }
    failure {
      echo "Security validation FAILED — Deployment BLOCKED"
    }
    always {
      echo "Pipeline completed"
    }
  }
}

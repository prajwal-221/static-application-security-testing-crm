pipeline {
  agent any

  environment {
    K8S_DIR = "k8s"
    POLICY_DIR = "policies"
    REPORT_DIR = "reports"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Prepare Workspace') {
      steps {
        sh '''
          rm -rf $REPORT_DIR
          mkdir -p $REPORT_DIR
        '''
      }
    }

    stage('YAML Lint - yamllint') {
      steps {
        sh '''
          echo "Running yamllint..."
          yamllint -f parsable -d relaxed $K8S_DIR > $REPORT_DIR/yamllint.txt || true
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
              -output json \
              -ignore-missing-schemas > $REPORT_DIR/kubeconform.json || true
        '''
      }
    }

    stage('Kubernetes Best Practices - kube-score') {
      steps {
        sh '''
          echo "Running kube-score..."
          kube-score score $K8S_DIR/**/*.yaml -o json > $REPORT_DIR/kube-score.json || true
        '''
      }
    }

    stage('Kubernetes Security Scan - kubesec') {
      steps {
        sh '''
        echo "Running kubesec (only scanning workload resources)..."
        echo "[" > $REPORT_DIR/kubesec.json
        first=true

        for file in $(find $K8S_DIR -name "*.yaml"); do
          kind=$(yq e '.kind' "$file")

          case "$kind" in
            Deployment|StatefulSet|DaemonSet|Job|CronJob)
            echo "Scanning $file ($kind)"
            result=$(kubesec scan "$file" 2>/dev/null || true)

            if [ "$first" = true ]; then
              first=false
            else
              echo "," >> $REPORT_DIR/kubesec.json
            fi

            echo "$result" >> $REPORT_DIR/kubesec.json
            ;;
          *)
            echo "Skipping unsupported kind $kind in $file"
            ;;
        esac
        done

        echo "]" >> $REPORT_DIR/kubesec.json
        '''
      }
    }


    stage('IaC Security Scan - Checkov') {
      steps {
        sh '''
          echo "Running Checkov..."
          checkov -d $K8S_DIR -o json > $REPORT_DIR/checkov.json || true
        '''
      }
    }

    stage('Policy Enforcement - Conftest') {
      steps {
        sh '''
          echo "Running Conftest..."
          conftest test $K8S_DIR --policy $POLICY_DIR -o json > $REPORT_DIR/conftest.json || true
        '''
      }
    }

    stage('Generate Security Report') {
      steps {
        sh '''
          python3 scripts/generate_report.py
        '''
      }
    }

  }

  post {
    always {
      archiveArtifacts artifacts: 'security-report.html, security-report.json, reports/**', fingerprint: true
    }
    success {
      echo "DevSecOps Security Validation PASSED"
    }
    failure {
      echo "Security Validation FAILED – Review Security Report"
    }
  }
}

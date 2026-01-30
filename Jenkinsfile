pipeline {
  agent any

  environment {
    K8S_DIR    = "k8s"
    POLICY_DIR = "policies"
    REPORT_DIR = "reports"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  stages {

    stage('Force Clean Workspace') {
      steps {
        deleteDir()
      }
    }

    stage('Checkout') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: '*/staging']],
          userRemoteConfigs: [[
            url: 'https://github.com/prajwal-221/static-application-security-testing-crm.git',
            credentialsId: '2d538862-d385-4df0-be3e-ea0c372f27b7'
          ]],
          extensions: [
            [$class: 'CleanBeforeCheckout'],
            [$class: 'PruneStaleBranch']
          ]
        ])
        sh 'git log -1 --oneline'
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
          yamllint -f parsable -d relaxed $K8S_DIR > $REPORT_DIR/yamllint.txt || true
          COUNT=$(wc -l < $REPORT_DIR/yamllint.txt || echo 0)

          if [ "$COUNT" -eq 0 ]; then
            echo "YAML Lint Result: PASS" > $REPORT_DIR/yamllint.status
          else
            echo "YAML Lint Result: WARN — $COUNT warnings detected" > $REPORT_DIR/yamllint.status
          fi
        '''
        sh 'cat $REPORT_DIR/yamllint.status'
      }
    }

    stage('Kubernetes Schema Validation - kubeconform') {
      steps {
        sh '''
          find $K8S_DIR -name "*.yaml" -print0 | \
          xargs -0 kubeconform -strict -summary -verbose -output json -ignore-missing-schemas \
          > $REPORT_DIR/kubeconform.json || true

          INVALID=$(jq '.summary.invalid' $REPORT_DIR/kubeconform.json 2>/dev/null || echo 0)

          if [ "$INVALID" -eq 0 ]; then
            echo "Kubeconform Result: PASS — All schemas valid" > $REPORT_DIR/kubeconform.status
          else
            echo "Kubeconform Result: FAIL — $INVALID invalid resources" > $REPORT_DIR/kubeconform.status
          fi
        '''
        sh 'cat $REPORT_DIR/kubeconform.status'
      }
    }

    stage('Kubernetes Best Practices - kube-score') {
      steps {
        sh '''
          kube-score score $K8S_DIR/**/*.yaml -o json > $REPORT_DIR/kube-score.json || true

          CRITICAL=$(jq '[.[] | .checks[] | select(.grade <= 3)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)
          WARNING=$(jq '[.[] | .checks[] | select(.grade > 3 and .grade <= 6)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)

          if [ "$CRITICAL" -eq 0 ] && [ "$WARNING" -eq 0 ]; then
            echo "Kube-score Result: PASS — No findings" > $REPORT_DIR/kube-score.status
          elif [ "$CRITICAL" -eq 0 ]; then
            echo "Kube-score Result: WARN — $WARNING warnings" > $REPORT_DIR/kube-score.status
          else
            echo "Kube-score Result: FAIL — $CRITICAL critical findings" > $REPORT_DIR/kube-score.status
          fi
        '''
        sh 'cat $REPORT_DIR/kube-score.status'
      }
    }

    stage('Kubernetes Security Scan - kubesec') {
      steps {
        sh '''
          echo "[" > $REPORT_DIR/kubesec.json
          first=true

          for file in $(find $K8S_DIR -name "*.yaml"); do
            kind=$(yq e '.kind' "$file")

            case "$kind" in
              Deployment|StatefulSet|DaemonSet|Job|CronJob)
                result=$(kubesec scan "$file" 2>/dev/null || true)

                if [ "$first" = true ]; then
                  first=false
                else
                  echo "," >> $REPORT_DIR/kubesec.json
                fi

                echo "$result" >> $REPORT_DIR/kubesec.json
                ;;
            esac
          done

          echo "]" >> $REPORT_DIR/kubesec.json

          FINDINGS=$(jq '[.[] | .scoring.advise[]] | length' $REPORT_DIR/kubesec.json 2>/dev/null || echo 0)

          if [ "$FINDINGS" -eq 0 ]; then
            echo "Kubesec Result: PASS — No security findings" > $REPORT_DIR/kubesec.status
          else
            echo "Kubesec Result: WARN — $FINDINGS recommendations" > $REPORT_DIR/kubesec.status
          fi
        '''
        sh 'cat $REPORT_DIR/kubesec.status'
      }
    }

    stage('IaC Security Scan - Checkov') {
      steps {
        sh '''
          checkov -d $K8S_DIR -o json > $REPORT_DIR/checkov.json || true

          FAILED=$(jq '.results.failed_checks | length' $REPORT_DIR/checkov.json 2>/dev/null || echo 0)

          if [ "$FAILED" -eq 0 ]; then
            echo "Checkov Result: PASS — No failed checks" > $REPORT_DIR/checkov.status
          else
            echo "Checkov Result: FAIL — $FAILED failed checks" > $REPORT_DIR/checkov.status
          fi
        '''
        sh 'cat $REPORT_DIR/checkov.status'
      }
    }

    stage('Policy Enforcement - Conftest') {
      steps {
        sh '''
          if [ -d "$POLICY_DIR" ] && [ "$(ls -A $POLICY_DIR 2>/dev/null)" ]; then
            conftest test $K8S_DIR --policy $POLICY_DIR -o json > $REPORT_DIR/conftest.json || true
          else
            echo "[]" > $REPORT_DIR/conftest.json
          fi

          COUNT=$(jq 'length' $REPORT_DIR/conftest.json 2>/dev/null || echo 0)

          if [ "$COUNT" -eq 0 ]; then
            echo "Conftest Result: PASS — No policy violations" > $REPORT_DIR/conftest.status
          else
            echo "Conftest Result: FAIL — $COUNT violations" > $REPORT_DIR/conftest.status
          fi
        '''
        sh 'cat $REPORT_DIR/conftest.status'
      }
    }

    stage('Generate Security Report') {
      steps {
        sh 'python3 scripts/generate_report.py'
      }
    }

  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/**, security-report.html, security-report.json', fingerprint: true
    }

    success {
      echo "DevSecOps Security Validation PASSED"
    }

    failure {
      echo "Security Validation FAILED — Review Security Report"
    }
  }
}

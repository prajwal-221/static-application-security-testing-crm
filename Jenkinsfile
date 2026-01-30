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
          set -e
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
          wc -l < $REPORT_DIR/yamllint.txt > $REPORT_DIR/yamllint.count || echo 0 > $REPORT_DIR/yamllint.count
        '''

        sh '''
          COUNT=$(cat $REPORT_DIR/yamllint.count)
          if [ "$COUNT" -eq 0 ]; then
            echo "YAML Lint Result: PASS"
          else
            echo "YAML Lint Result: WARN — $COUNT warnings detected"
          fi
        '''
      }
    }

    stage('Kubernetes Schema Validation - kubeconform') {
      steps {
        sh '''
          find $K8S_DIR -name "*.yaml" -print0 > $REPORT_DIR/kubeconform-files.txt

          cat $REPORT_DIR/kubeconform-files.txt | \
            xargs -0 kubeconform \
              -strict -summary -verbose -output json \
              -ignore-missing-schemas > $REPORT_DIR/kubeconform.json || true

          jq '.summary.invalid' $REPORT_DIR/kubeconform.json > $REPORT_DIR/kubeconform.invalid || echo 0 > $REPORT_DIR/kubeconform.invalid
        '''

        sh '''
          INVALID=$(cat $REPORT_DIR/kubeconform.invalid)
          if [ "$INVALID" -eq 0 ]; then
            echo "Kubeconform Result: PASS — All schemas valid"
          else
            echo "Kubeconform Result: FAIL — $INVALID invalid resources"
          fi
        '''
      }
    }

    stage('Kubernetes Best Practices - kube-score') {
      steps {
        sh '''
          kube-score score $K8S_DIR/**/*.yaml -o json > $REPORT_DIR/kube-score.json || true

          jq '[.[] | .checks[] | select(.grade <= 3)] | length' $REPORT_DIR/kube-score.json > $REPORT_DIR/kubescore.critical || echo 0 > $REPORT_DIR/kubescore.critical
          jq '[.[] | .checks[] | select(.grade > 3 and .grade <= 6)] | length' $REPORT_DIR/kube-score.json > $REPORT_DIR/kubescore.warning || echo 0 > $REPORT_DIR/kubescore.warning
        '''

        sh '''
          CRITICAL=$(cat $REPORT_DIR/kubescore.critical)
          WARNING=$(cat $REPORT_DIR/kubescore.warning)

          if [ "$CRITICAL" -eq 0 ]; then
            echo "Kube-score Critical: PASS"
          else
            echo "Kube-score Critical: FAIL — $CRITICAL findings"
          fi

          if [ "$WARNING" -eq 0 ]; then
            echo "Kube-score Warnings: PASS"
          else
            echo "Kube-score Warnings: WARN — $WARNING warnings"
          fi
        '''
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

          jq '[.[] | .scoring.advise[]] | length' $REPORT_DIR/kubesec.json > $REPORT_DIR/kubesec.count || echo 0 > $REPORT_DIR/kubesec.count
        '''

        sh '''
          FINDINGS=$(cat $REPORT_DIR/kubesec.count)
          if [ "$FINDINGS" -eq 0 ]; then
            echo "Kubesec Result: PASS — No security findings"
          else
            echo "Kubesec Result: WARN — $FINDINGS security recommendations"
          fi
        '''
      }
    }

    stage('IaC Security Scan - Checkov') {
      steps {
        sh '''
          checkov -d $K8S_DIR -o json > $REPORT_DIR/checkov.json || true
          jq '.results.failed_checks | length' $REPORT_DIR/checkov.json > $REPORT_DIR/checkov.count || echo 0 > $REPORT_DIR/checkov.count
        '''

        sh '''
          FAILED=$(cat $REPORT_DIR/checkov.count)
          if [ "$FAILED" -eq 0 ]; then
            echo "Checkov Result: PASS — No failed checks"
          else
            echo "Checkov Result: FAIL — $FAILED failed checks"
          fi
        '''
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

          jq 'length' $REPORT_DIR/conftest.json > $REPORT_DIR/conftest.count || echo 0 > $REPORT_DIR/conftest.count
        '''

        sh '''
          COUNT=$(cat $REPORT_DIR/conftest.count)
          if [ "$COUNT" -eq 0 ]; then
            echo "Conftest Result: PASS — No policy violations"
          else
            echo "Conftest Result: FAIL — $COUNT policy violations"
          fi
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

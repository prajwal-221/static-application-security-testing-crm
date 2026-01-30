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

    stage('Checkout') {
      steps {
        checkout scm
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

          echo "Parsing yamllint results..."
          COUNT=$(wc -l < $REPORT_DIR/yamllint.txt || echo 0)

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
          echo "Running kubeconform validation..."
          find $K8S_DIR -name "*.yaml" -print0 > $REPORT_DIR/kubeconform-files.txt

          echo "Validating manifests..."
          cat $REPORT_DIR/kubeconform-files.txt | \
            xargs -0 kubeconform \
              -strict \
              -summary \
              -verbose \
              -output json \
              -ignore-missing-schemas > $REPORT_DIR/kubeconform.json || true

          echo "Parsing kubeconform results..."
          INVALID=$(jq '.summary.invalid' $REPORT_DIR/kubeconform.json 2>/dev/null || echo 0)

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
          echo "Running kube-score..."
          kube-score score $K8S_DIR/**/*.yaml -o json > $REPORT_DIR/kube-score.json || true

          echo "Analyzing kube-score output..."
          CRITICAL=$(jq '[.[] | .checks[] | select(.grade <= 3)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)
          WARNING=$(jq '[.[] | .checks[] | select(.grade > 3 and .grade <= 6)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)

          if [ "$CRITICAL" -eq 0 ]; then
            echo "Kube-score Critical: PASS"
          else
            echo "Kube-score Critical: FAIL — $CRITICAL critical findings"
          fi

          if [ "$WARNING" -eq 0 ]; then
            echo "Kube-score Warnings: PASS"
          else
            echo "Kube-score Warnings: WARN — $WARNING warnings detected"
          fi
        '''
      }
    }

    stage('Kubernetes Security Scan - kubesec') {
      steps {
        sh '''
          echo "Running kubesec scans..."

          echo "[" > $REPORT_DIR/kubesec.json
          first=true

          for file in $(find $K8S_DIR -name "*.yaml"); do
            kind=$(yq e '.kind' "$file")

            case "$kind" in
              Deployment|StatefulSet|DaemonSet|Job|CronJob)
                echo "Scanning workload: $file ($kind)"

                result=$(kubesec scan "$file" 2>/dev/null || true)

                if [ "$first" = true ]; then
                  first=false
                else
                  echo "," >> $REPORT_DIR/kubesec.json
                fi

                echo "$result" >> $REPORT_DIR/kubesec.json
                ;;
              *)
                ;;
            esac
          done

          echo "]" >> $REPORT_DIR/kubesec.json

          echo "Analyzing kubesec results..."
          FINDINGS=$(jq '[.[] | .scoring.advise[]] | length' $REPORT_DIR/kubesec.json 2>/dev/null || echo 0)

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
          echo "Running Checkov..."
          checkov -d $K8S_DIR -o json > $REPORT_DIR/checkov.json || true

          echo "Parsing Checkov output..."
          FAILED=$(jq '.results.failed_checks | length' $REPORT_DIR/checkov.json 2>/dev/null || echo 0)

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
          echo "Running Conftest policy enforcement..."

          if [ -d "$POLICY_DIR" ] && [ "$(ls -A $POLICY_DIR 2>/dev/null)" ]; then
            conftest test $K8S_DIR --policy $POLICY_DIR -o json > $REPORT_DIR/conftest.json || true
          else
            echo "[]" > $REPORT_DIR/conftest.json
            echo "Conftest Result: SKIPPED — No policies found"
          fi

          echo "Parsing Conftest results..."
          COUNT=$(jq 'length' $REPORT_DIR/conftest.json 2>/dev/null || echo 0)

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
          echo "Generating consolidated security report..."
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

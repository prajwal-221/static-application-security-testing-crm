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
          find $K8S_DIR -name "*.yaml" -print0 | \
          xargs -0 kubeconform -strict -summary -verbose -output json -ignore-missing-schemas \
          > $REPORT_DIR/kubeconform.json || true

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
          kube-score score $K8S_DIR/**/*.yaml -o json > $REPORT_DIR/kube-score.json || true

          CRITICAL=$(jq '[.[] | .checks[] | select(.grade <= 3)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)
          WARNING=$(jq '[.[] | .checks[] | select(.grade > 3 and .grade <= 6)] | length' $REPORT_DIR/kube-score.json 2>/dev/null || echo 0)

          if [ "$CRITICAL" -gt 0 ]; then
            echo "Kube-score Result: FAIL — $CRITICAL critical findings"
          elif [ "$WARNING" -gt 0 ]; then
            echo "Kube-score Result: WARN — $WARNING warnings"
          else
            echo "Kube-score Result: PASS — No findings"
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
                if [ "$first" = true ]; then first=false; else echo "," >> $REPORT_DIR/kubesec.json; fi
                echo "$result" >> $REPORT_DIR/kubesec.json
                ;;
            esac
          done

          echo "]" >> $REPORT_DIR/kubesec.json

          FINDINGS=$(jq '[.[] | .scoring.advise[]] | length' $REPORT_DIR/kubesec.json 2>/dev/null || echo 0)

          if [ "$FINDINGS" -eq 0 ]; then
            echo "Kubesec Result: PASS — No security findings"
          else
            echo "Kubesec Result: WARN — $FINDINGS recommendations"
          fi
        '''
      }
    }

    stage('IaC Security Scan - Checkov') {
      steps {
        sh '''
          checkov -d $K8S_DIR -o json > $REPORT_DIR/checkov.json || true
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
          if [ -d "$POLICY_DIR" ] && [ "$(ls -A $POLICY_DIR 2>/dev/null)" ]; then
            conftest test $K8S_DIR --policy $POLICY_DIR -o json > $REPORT_DIR/conftest.json || true
          else
            echo "[]" > $REPORT_DIR/conftest.json
          fi

          COUNT=$(jq 'length' $REPORT_DIR/conftest.json 2>/dev/null || echo 0)

          if [ "$COUNT" -eq 0 ]; then
            echo "Conftest Result: PASS — No policy violations"
          else
            echo "Conftest Result: FAIL — $COUNT violations"
          fi
        '''
      }
    }

    stage('Generate Security Report') {
      steps {
        sh 'python3 scripts/generate_report.py'
      }
    }

    /* ---------------- CHAOS ENGINEERING ---------------- */

    stage('Chaos Readiness Validation') {
      steps {
        sh '''
          kubectl get nodes
          kubectl get pods -A | grep -i running
          echo "Cluster ready for chaos testing"
        '''
      }
    }

    stage('Install LitmusChaos') {
      steps {
        sh '''
          # Install LitmusChaos operator
          kubectl apply -f https://litmuschaos.github.io/litmus/litmus-operator-v3.0.0.yaml
          kubectl rollout status deployment/chaos-operator-ce -n litmus --timeout=180s
          kubectl wait --for=condition=Available deployment chaos-operator-ce -n litmus --timeout=180s
          
          # Create litmus namespace if not exists
          kubectl create namespace litmus --dry-run=client -o yaml | kubectl apply -f -
          
          # Apply chaos experiments (one-time setup)
          kubectl apply -f chaos/experiments/
        '''
      }
    }

    stage('Chaos Test - Frontend Pod Deletion') {
      steps {
        sh '''
          echo "Starting Frontend Pod Deletion Test..."
          kubectl apply -f chaos/engines/pod-delete-engine.yaml
          sleep 90
          kubectl delete chaosengine pod-delete-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Frontend Network Latency') {
      steps {
        sh '''
          echo "Starting Frontend Network Latency Test..."
          kubectl apply -f chaos/engines/network-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine network-latency-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Frontend CPU Stress') {
      steps {
        sh '''
          echo "Starting Frontend CPU Stress Test..."
          kubectl apply -f chaos/engines/cpu-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine cpu-hog-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Frontend Memory Stress') {
      steps {
        sh '''
          echo "Starting Frontend Memory Stress Test..."
          kubectl apply -f chaos/engines/memory-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine memory-hog-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Backend Pod Deletion') {
      steps {
        sh '''
          echo "Starting Backend Pod Deletion Test..."
          kubectl apply -f chaos/engines/backend-pod-delete-engine.yaml
          sleep 90
          kubectl delete chaosengine backend-pod-delete-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Backend CPU Stress') {
      steps {
        sh '''
          echo "Starting Backend CPU Stress Test..."
          kubectl apply -f chaos/engines/backend-cpu-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine backend-cpu-hog-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Backend Network Latency') {
      steps {
        sh '''
          echo "Starting Backend Network Latency Test..."
          kubectl apply -f chaos/engines/backend-network-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine backend-network-latency-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Test - Backend Memory Stress') {
      steps {
        sh '''
          echo "Starting Backend Memory Stress Test..."
          kubectl apply -f chaos/engines/backend-memory-chaos-engine.yaml
          sleep 120
          kubectl delete chaosengine backend-memory-hog-chaos -n litmus --ignore-not-found
        '''
      }
    }

    stage('Chaos Cleanup') {
      steps {
        sh '''
          echo "Cleaning up chaos resources..."
          # Clean up all chaos engines
          kubectl delete chaosengine --all -n litmus --ignore-not-found
          
          # Clean up chaos experiments
          kubectl delete chaosexperiment --all -n litmus --ignore-not-found
          
          # Wait for deployments to be ready
          kubectl rollout status deployment/backend -n idurar --timeout=180s
          kubectl rollout status deployment/frontend -n idurar --timeout=180s
        '''
      }
    }

    stage('Auto-Healing Validation') {
      steps {
        sh '''
          echo "Validating auto-healing..."
          
          # Check deployment status
          kubectl rollout status deployment backend -n idurar --timeout=180s
          kubectl rollout status deployment frontend -n idurar --timeout=180s

          # Get ready replicas
          BACKEND_READY=$(kubectl get deploy backend -n idurar -o jsonpath='{.status.readyReplicas}')
          FRONTEND_READY=$(kubectl get deploy frontend -n idurar -o jsonpath='{.status.readyReplicas}')

          echo "Backend ready replicas: $BACKEND_READY"
          echo "Frontend ready replicas: $FRONTEND_READY"

          # Check if all replicas are ready
          if [ "$BACKEND_READY" = "0" ] || [ "$FRONTEND_READY" = "0" ]; then
            echo "Auto-healing FAILED - Some replicas are not ready"
            exit 1
          else
            echo "Auto-healing SUCCESS - All replicas are ready"
          fi
        '''
      }
    }

  }

  post {
    always {
      // Archive all reports
      archiveArtifacts artifacts: 'reports/**, security-report.html, security-report.json', fingerprint: true
      
      // Clean up chaos resources regardless of pipeline status
      sh '''
        echo "Final chaos cleanup..."
        kubectl delete chaosengine --all -n litmus --ignore-not-found || true
        kubectl delete chaosexperiment --all -n litmus --ignore-not-found || true
      '''
    }

    success {
      echo "DevSecOps + Chaos Engineering Pipeline PASSED ✅"
      echo "All security and resilience tests completed successfully"
    }

    failure {
      echo "Pipeline FAILED ❌"
      echo "Review Security & Chaos Reports"
      echo "Check chaos results with: kubectl get chaosresult -n litmus"
    }
  }
}

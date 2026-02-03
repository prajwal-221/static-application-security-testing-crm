# Chaos Stabilization Plan

## Goal
Ensure all Litmus chaos experiments (frontend/backend pod delete, CPU, memory, network) run reliably on the Minikube cluster and report successful ChaosResults.

## Current Issues
1. Chaos helper pods fail with `CONTAINER_RUNTIME_ERROR` while inspecting containerd-managed pods.
2. Chaos results report `pods "<name>" not found` because helpers reference stale pod IDs when workloads restart mid-experiment.
3. `SEQUENCE` env vars were added under experiment env instead of runner env, so tests may still run in parallel.
4. Experiments are missing container runtime hints (`CONTAINER_RUNTIME`, `SOCKET_PATH`) and explicit target container names.
5. RBAC/ServiceAccount definitions exist but aren’t bundled with the chaos installation workflow.

## Action Plan
1. **Audit configurations**
   - Verify frontend/backend deployments (labels, container names).
   - Capture current chaos experiment and engine specs for reference.
   - Inspect recent chaos pod logs to confirm failure patterns.

2. **Fix experiments**
   - Update all `chaos/experiments/*.yaml` to use the recommended Litmus go-runner configuration with:
     - Proper permissions block (pods, events, jobs, litmus CRDs).
     - `image: litmuschaos/go-runner:3.0.0` and command/args.
     - Default env placeholders (duration, intervals) removed from definition (tuned via engines instead).

3. **Fix engines**
   - Move `SEQUENCE` under `components.runner.env`.
   - Add explicit env overrides per experiment: `TARGET_CONTAINER`, `CONTAINER_RUNTIME=containerd`, `SOCKET_PATH=/run/containerd/containerd.sock`, `PODS_AFFECTED_PERC`.
   - Provide `probe`/delay tuning as needed so workloads recover between tests.

4. **RBAC alignment**
   - Ensure `litmus-rbac.yaml` + binding applied before chaos stages (Jenkins/E2E instructions).

5. **Validation**
   - Reapply experiments and engines.
   - Run each chaos stage sequentially, monitoring helper pods/logs.
   - Capture `kubectl get chaosresults -n litmus` output to confirm `Verdict: Pass`.

Progress will be tracked by updating this file as each step completes.

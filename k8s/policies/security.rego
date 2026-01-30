package main

deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := "Containers must not run as root"
}

deny[msg] {
  container := input.spec.template.spec.containers[_]
  not container.resources.requests
  msg := sprintf("Missing resource requests for container %s", [container.name])
}

deny[msg] {
  container := input.spec.template.spec.containers[_]
  not container.resources.limits
  msg := sprintf("Missing resource limits for container %s", [container.name])
}

deny[msg] {
  container := input.spec.template.spec.containers[_]
  not container.readinessProbe
  msg := sprintf("Missing readinessProbe for container %s", [container.name])
}

deny[msg] {
  container := input.spec.template.spec.containers[_]
  not container.livenessProbe
  msg := sprintf("Missing livenessProbe for container %s", [container.name])
}

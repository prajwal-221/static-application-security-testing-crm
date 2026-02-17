#!/bin/sh
set -e

echo "Starting Docker daemon..."
dockerd --host=unix:///var/run/docker.sock --storage-driver=overlay2 &

echo "Waiting for Docker..."
until docker info > /dev/null 2>&1; do
  sleep 1
done

echo "Docker ready."

echo "Starting Jenkins agent..."
exec java -jar /usr/share/jenkins/agent.jar \
  -jnlpUrl ${JENKINS_URL}/computer/${JENKINS_AGENT_NAME}/jenkins-agent.jnlp \
  -secret ${JENKINS_SECRET} \
  -workDir /home/jenkins

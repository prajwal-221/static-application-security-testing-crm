FROM jenkins/jenkins:lts-jdk17

USER root

# ===============================
# Base system dependencies
# ===============================
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    unzip \
    jq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    wget \
    pipx \
    && rm -rf /var/lib/apt/lists/*


# ===============================
# kubectl (stable pinned)
# ===============================
RUN curl -fsSL -o /usr/local/bin/kubectl \
    https://dl.k8s.io/release/v1.30.0/bin/linux/amd64/kubectl && \
    chmod +x /usr/local/bin/kubectl


# ===============================
# Helm
# ===============================
RUN curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash


# ===============================
# Trivy (stable pinned)
# ===============================
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
    | sh -s -- -b /usr/local/bin v0.49.1


# ===============================
# kube-score (pinned)
# ===============================
RUN curl -L https://github.com/zegl/kube-score/releases/download/v1.18.0/kube-score_1.18.0_linux_amd64.tar.gz \
    -o /tmp/kube-score.tar.gz && \
    tar -xzf /tmp/kube-score.tar.gz -C /tmp && \
    mv /tmp/kube-score /usr/local/bin/ && \
    rm -rf /tmp/kube-score*


# ===============================
# kubesec (pinned)
# ===============================
RUN curl -L https://github.com/controlplaneio/kubesec/releases/download/v2.14.0/kubesec_linux_amd64.tar.gz \
    -o /tmp/kubesec.tar.gz && \
    tar -xzf /tmp/kubesec.tar.gz -C /tmp && \
    mv /tmp/kubesec /usr/local/bin/ && \
    rm -rf /tmp/kubesec*


# ===============================
# kubeconform (pinned, better than kubeval)
# ===============================
RUN curl -L https://github.com/yannh/kubeconform/releases/download/v0.6.6/kubeconform-linux-amd64.tar.gz \
    -o /tmp/kubeconform.tar.gz && \
    tar -xzf /tmp/kubeconform.tar.gz -C /tmp && \
    mv /tmp/kubeconform /usr/local/bin/ && \
    rm -rf /tmp/kubeconform*


# ===============================
# conftest (OPA policy, pinned)
# ===============================
RUN curl -L https://github.com/open-policy-agent/conftest/releases/download/v0.52.0/conftest_0.52.0_Linux_x86_64.tar.gz \
    -o /tmp/conftest.tar.gz && \
    tar -xzf /tmp/conftest.tar.gz -C /tmp && \
    mv /tmp/conftest /usr/local/bin/ && \
    rm -rf /tmp/conftest*


# ===============================
# yamllint + checkov (pipx global → PATH safe)
# ===============================
RUN pipx install --global yamllint && \
    pipx install --global checkov


# ===============================
# gitleaks (pinned)
# ===============================
RUN curl -L https://github.com/gitleaks/gitleaks/releases/download/v8.18.2/gitleaks_8.18.2_linux_x64.tar.gz \
    -o /tmp/gitleaks.tar.gz && \
    tar -xzf /tmp/gitleaks.tar.gz -C /tmp && \
    mv /tmp/gitleaks /usr/local/bin/ && \
    chmod +x /usr/local/bin/gitleaks && \
    rm -rf /tmp/gitleaks*


# ===============================
# yq (pinned)
# ===============================
RUN curl -L https://github.com/mikefarah/yq/releases/download/v4.44.1/yq_linux_amd64 \
    -o /usr/local/bin/yq && \
    chmod +x /usr/local/bin/yq

# ===============================
# Docker CLI (required for docker run / compose)
# ===============================
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose v2
RUN mkdir -p /usr/libexec/docker/cli-plugins && \
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
    -o /usr/libexec/docker/cli-plugins/docker-compose && \
    chmod +x /usr/libexec/docker/cli-plugins/docker-compose    

# ===============================
# Docker socket permissions 
# ===============================
RUN groupadd docker || true
RUN usermod -aG docker jenkins



# ===============================
# Permissions cleanup
# ===============================
RUN chown -R jenkins:jenkins /usr/local/bin


USER jenkins

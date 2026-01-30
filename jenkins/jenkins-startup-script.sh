docker build -t jenkins-devsecops:lts -f Dockerfile .

docker run -d \
  --name jenkins \
  --restart unless-stopped \
  --network host \
  -v /var/lib/jenkins:/var/jenkins_home \
  -v ~/.kube:/var/jenkins_home/.kube \
  -v ~/.minikube:/home/ht-admin/.minikube \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins-devsecops:lts
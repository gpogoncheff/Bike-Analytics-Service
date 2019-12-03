# image: gcr.io/project-5253/worker-server:v20
kubectl create -f deployment.yaml
kubectl scale deployment worker-server --replicas=3

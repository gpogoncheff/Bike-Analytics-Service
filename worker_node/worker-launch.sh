#kubectl create deployment worker-server --image=gcr.io/project-5253/worker-server:v00
#kubectl expose deployment worker-server --port 80
#kubectl scale deployment worker-server --replicas=3

kubectl create -f deployment.yaml
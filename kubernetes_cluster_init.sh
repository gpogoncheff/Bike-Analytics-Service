gcloud config set project project-5253
gcloud config set compute/zone us-west1-b
gcloud container clusters create --preemptible project-kube
kubectl create secret generic proj-access-key --from-file=key.json=../project-5253-c7b5dcc0dab1.json

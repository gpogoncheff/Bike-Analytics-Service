#kubectl create secret generic proj-key --from-file=key.json=project-5253-c66de9fd7e5e.json
gcloud config set project project-5253
gcloud config set compute/zone us-west1-b
gcloud container clusters create --preemptible project-kube

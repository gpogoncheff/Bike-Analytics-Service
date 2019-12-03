#!/bin/sh
# image: gcr.io/project-5253/rest-server:v10
kubectl create -f deployment.yaml
kubectl create -f service.yaml

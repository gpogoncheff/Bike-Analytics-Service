#!/bin/sh
# container: gcr.io/lab8-257721/rest-server:v30
kubectl create -f deployment.yaml
kubectl create -f service.yaml

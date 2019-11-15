#!/bin/sh
# docker build -t gcr.io/lab8-257721/rest-server:v30 .
# docker push gcr.io/lab8-257721/rest-server:v30
kubectl create -f deployment.yaml
kubectl create -f service.yaml
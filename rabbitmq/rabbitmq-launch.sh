#!/bin/sh
# rabbitmq container: gcr.io/project-5253/rabbitmq:v00
kubectl create -f deployment.yaml
kubectl create -f service.yaml

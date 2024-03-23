# Django Project Deployment with Docker and Kubernetes

This repository contains a Django project intended for deployment using Docker containers orchestrated with Kubernetes.

## Prerequisites

Before deploying this Django project, ensure the following dependencies are installed:

- Docker
- Kubernetes
- kubectl

## Deployment Steps

Follow these steps to deploy the Django project using Docker and Kubernetes:

1. *Clone Repository*: Clone this repository to your local machine.
   ```bash
   git clone https://github.com/asifxohd/kubernetes.git
   
2. ## create cyclehub-secret.yaml file
   ```yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: cyclehub-secret
      type: Opaque
      data:
        SECRET_KEY: 
        EMAIL_HOST_USER: 
        EMAIL_HOST_PASSWORD:
        DB_NAME:
        DB_USER:
        DB_PASSWORD:
        DB_HOST:
        DEFAULT_FROM_EMAIL:
   ```

   apply by:
      ```bash
        kubectl apply -f <secretroot/cyclehub-secret.yaml>
      ```

3. ## create postgres-secret.yaml file
  ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: postgres-secret
    type: Opaque
    data:
      POSTGRES_DB:
      POSTGRES_PASSWORD:
      POSTGRES_USER:
      POSTGRES_HOST:
```
  apply by:
      ```bash
        kubectl apply -f <secretroot/postgres-secret.yaml>
      ```
4. ## create .env file
  ``` .env
      SECRET_KEY=
      EMAIL_HOST_USER=
      EMAIL_HOST_PASSWORD=
      RAZORPAY_API_KEY=
      RAZORPAY_API_SECRET_KEY=
      POSTGRES_NAME=
      POSTGRES_USER=
      POSTGRES_PASSWORD=
      POSTGRES_HOST=
```

5. ## Run with Docker-compose
   ```
      docker-compose up -d
   ```
  Now you can run on localhost:8000. For this, you only need to create the .env file; .yaml files are not needed.
  
6. ## Deployment with Kuberneties
   ```
      kubctl apply -f <k8/django file directory>
     kubctl apply -f <k8/postgres file directory>
     kubctl apply -f <k8/volume file directory>

  By doing this, you will successfully be able to run using NodePort service. Additionally, for Nginx, you'll need to configure 127.0.0.1 cyclehub.com in the host file. Otherwise, you can use kubectl get services to get the NodePort and access the service using localhost:targetport.

happy coding

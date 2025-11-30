# MLOps_RecruitAIr_Deployment
Helm Chart and Supplementary Assets to perform Deployment of the full stack for the RecruitAIr application

## Getting Started

For development, run:
```bash
kind create cluster -n recruitair --config kind.config.yaml
```

Then, create the namespace:
```bash
kubectl create namespace recruitair
```

And create the image pull secret and the database secret:
```bash
kubectl create secret docker-registry regcred --docker-server=ghcr.io --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email> -n recruitair

kubectl create secret generic postgres-secret --from-literal=postgres-password=<your-pword> -n recruitair
```


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

And create the image pull secret and the database admin secret:
```bash
kubectl create secret docker-registry regcred --docker-server=ghcr.io --docker-username=<your-name> --docker-password=<your-pword> --docker-email=<your-email> -n recruitair

kubectl create secret generic postgres-secret --from-literal=postgres-password=<some_password> --from-literal=postgres-username=<some_username> -n recruitair
```

These will be the user and password for the admin user of the Postgres database.

Finally, install the Helm chart:
```bash
helm install recruitair ./deployment -n recruitair --wait --debug
```
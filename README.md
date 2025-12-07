# MLOps_RecruitAIr_Deployment
Helm Chart and Supplementary Assets to perform Deployment of the full stack for the RecruitAIr application

## Getting Started

1. Install [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) to create a local Kubernetes cluster.
2. Install [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to interact with your Kubernetes cluster.
3. Install [Helm](https://helm.sh/docs/intro/install/) to manage Kubernetes applications.
4. Clone this repository and navigate to the cloned repository directory.
5. Create a Kind cluster using the provided configuration file:
```bash
kind create cluster -n recruitair --config kind.config.yaml
```
6. Apply the ingress controller:
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```
7. Create a namespace for the RecruitAIr application:
```bash
kubectl create namespace recruitair
```
8. Create the image pull secret and the database admin secret:
```bash
kubectl create secret docker-registry regcred --docker-server=ghcr.io --docker-username=<your-name> --docker-password=<your-pword> -n recruitair
kubectl create secret generic postgres-secret --from-literal=postgres-password=<some_password> --from-literal=postgres-username=<some_username> -n recruitair
```
    Replace `<your-name>` and `<your-pword>` with your GitHub Container Registry credentials. Replace `<some_password>` and `<some_username>` with your desired values for the Postgres admin login.
9. If running in kind locally, create the AWS credentials secret:
```bash
kubectl -n recruitair create secret generic aws-creds --from-literal=aws-access-key-id=<your_access_key_id> --from-literal=aws-secret-access-key=<your_secret_access_key> --from-literal=aws-region=eu-north-1
```
    Replace `<your_access_key_id>` and `<your_secret_access_key>` with your AWS credentials. If running inside AWS, you can skip this step and comment out the `awsSecret` field in `values.yaml`.
10. Finally, install the Helm chart:
```bash
helm install recruitair ./recruitair -n recruitair --wait
```
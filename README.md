# Automating Distributed Data Pipelines on Kubernetes with Apache Spark and Argo CD

![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5.1-E25A1C?logo=apachespark&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestration-326CE5?logo=kubernetes&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS-S3-569A31?logo=amazons3&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-Chart-0F1689?logo=helm&logoColor=white)
![Build Status](https://github.com/zablon-oigo/spark-s3-kubernetes/actions/workflows/ci.yml/badge.svg)
![Argo CD](https://img.shields.io/badge/Argo%20CD-GitOps-EF7B4D?logo=argo&logoColor=white)

This project demonstrates distributed data processing on Kubernetes using Apache Spark and Amazon S3.

Spark applications are deployed and managed through the Spark Operator, which integrates Spark workloads with Kubernetes and simplifies job submission, execution, and lifecycle management.

The data pipeline reads source data from an Amazon S3 bucket, processes it using PySpark, and writes the transformed output back to S3 in Parquet format.

The deployment also incorporates Docker for application packaging, Helm for Spark Operator installation, and Argo CD for GitOps-based application deployment and synchronization.

### Architecture

<img width="1141" height="359" alt="spark excalidraw" src="https://github.com/user-attachments/assets/1f245051-bee9-445e-9a4f-f88e29d832d8" />


#### 1. Install the Spark Operator

Add the Spark Operator Helm repository:

```bash
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update
```

Install the Spark Operator:

```bash
helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --create-namespace \
  --set webhook.enable=true \
  --set "spark.jobNamespaces={spark-apps}"
```

#### 2. Verify the Installation

Check the Spark Operator pods:

```bash
kubectl get pods -n spark-operator
```

Verify that the Spark Operator Custom Resource Definitions (CRDs) are installed:

```bash
kubectl get crd | grep sparkoperator
```

#### 3. Create the Spark Namespace

Create the namespace where Spark applications will run:

```bash
kubectl create namespace spark-apps
```

#### 4. Configure AWS Credentials

Spark requires AWS credentials to access private S3 objects.

Export your AWS credentials from your local AWS CLI configuration:

```bash
export AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id --profile default)
export AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key --profile default)
```

Verify that both variables are populated without displaying their values:

```bash
test -n "$AWS_ACCESS_KEY_ID" && echo "AWS access key loaded"
test -n "$AWS_SECRET_ACCESS_KEY" && echo "AWS secret key loaded"
```

Create a Kubernetes Secret:

```bash
kubectl create secret generic aws-credentials \
  --namespace spark-apps \
  --from-literal=AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  --from-literal=AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY"
```

Verify the Secret:

```bash
kubectl describe secret aws-credentials -n spark-apps
```

The credentials are injected into the Spark driver and executor containers through environment variables.


#### 5. Configure the S3 Bucket

Instead of hardcoding the bucket name in the PySpark application, use a Kubernetes ConfigMap.

```bash
kubectl create configmap s3-config \
  --namespace spark-apps \
  --from-literal=S3_BUCKET=<your-actual-bucket-name>
```

Verify:

```sh
kubectl get configmap s3-config -n spark-apps
```

Replace with your S3 bucket name.

The application retrieves the bucket name through the S3_BUCKET environment variable.

#### 6. Configure Spark RBAC

Apply the Kubernetes ServiceAccount, Role, and RoleBinding:

```bash
kubectl apply -f spark-rbac.yaml
```

The Spark driver uses this ServiceAccount to interact with Kubernetes resources such as pods, services, and ConfigMaps.

#### 7. Deploy the Spark Application

Submit the SparkApplication resource:

```bash
kubectl apply -f spark-app.yaml
```

The Spark Operator detects the SparkApplication resource and creates the driver and executor pods.

#### 8. Monitor the Spark Application

Watch the SparkApplication status:

```bash
kubectl get sparkapplications -n spark-apps -w
```

Check the running pods:

```bash
kubectl get pods -n spark-apps
```

Follow the driver logs:

```bash
kubectl logs -n spark-apps data-processing-driver -f
```

Check executor logs:

```bash
kubectl logs -n spark-apps \
  -l spark-role=executor \
  --tail=100
```

#### 9. Access the Spark UI

Once the driver pod is running and the Spark UI is available, forward port 4040:

```bash
kubectl port-forward -n spark-apps \
  pod/data-processing-driver 4040:4040
```

Open the Spark UI:

>http://localhost:4040


#### 10. Verify Processed Data in S3

List the output objects:

```bash
aws s3 ls s3://YOUR_BUCKET_NAME/landing/titanic/ --recursive
```

The output is stored in Parquet format.


### Argo CD

Get Admin Password:

```sh
kubectl  get secret  argocd-initial-admin-secret   -n argocd  -o yaml
```
Decode Admin Password:

```sh
echo <argocd_admin_pass> | base64 --decode
```

Argo CD UI:
```sh
kubectl port-forward  -n argocd svc/argocd-server 8080:443
```

Argo CD CLI login:

```sh
argocd login localhost:8080 --insecure
```
<img width="1309" height="429" alt="image3" src="https://github.com/user-attachments/assets/d28081f0-2c97-4be1-839f-f74054f1fc86" />


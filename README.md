# Pokero - Cloud Native Web Application

This project demonstrates a High Availability (HA) architecture for a web application deployed on Azure Kubernetes Service (AKS). It utilizes **Infrastructure as Code** (Terraform), **GitOps** principles, and a **Cloud Native** technology stack (Django, PostgreSQL Operator, Helm, Loki/Grafana, Falco).

## Prerequisites

To work with this project, ensure you have the following tools installed:

- **Docker & Docker Compose** (for local development)
- **Azure CLI** (`az login`)
- **kubectl** (configured via `az aks get-credentials`)
- **Helm 3** (Package manager for Kubernetes)

---

## Local Development

Run the application locally using Docker Compose with hot-reloading enabled.

### Local Secrets
**Note:** The `secrets/` directory is used **only** for local development.
Create a file named `db_password` inside the `secrets/` directory containing your local database password.

### Running the Environment

**Development Mode (Hot-reload, Debug ON):**
```bash
docker compose --profile=dev up --build -d
```

**Production Mode Simulation:**
```bash
docker compose --profile=prod up --build -d
```

### Local Management Tasks
After the container starts, you may need to run migrations or create an admin user.

```bash
# Get the container ID
CONTAINER_ID=$(docker ps -qf "name=pokero-app")

# Run database migrations
docker exec -it $CONTAINER_ID python manage.py migrate

# Create a Superuser (for Django Admin Panel)
docker exec -it $CONTAINER_ID python manage.py createsuperuser
```

---

##Cluster Bootstrap (Infrastructure Setup)

These steps are performed **once** to prepare a new Kubernetes cluster. They install system-level components like the Database Operator and Monitoring Stack.

**Important:** Kubernetes secrets (e.g., database credentials) are managed via the Infrastructure Repository and must be present in the cluster before deployment.

### 1. Install PostgreSQL Operator (Zalando)
This operator manages the HA Database cluster (Master/Replica).

```bash
helm repo add postgres-operator-charts https://opensource.zalando.com/postgres-operator/charts/postgres-operator
helm repo update

# Install operator (anti-affinity disabled for cost-optimization on small clusters)
helm upgrade --install postgres-operator postgres-operator-charts/postgres-operator \
  --namespace default \
  --set configKubernetes.enable_pod_antiaffinity=false \
  --set configKubernetes.enable_pod_disruption_budget=false
```

### 2. Install Monitoring & Security Stack
Deploys Loki (logging), Grafana (visualization), and Falco (runtime security).

```bash
# Add repositories
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# Install Loki Stack (Promtail + Loki + Grafana)
helm upgrade --install loki-stack grafana/loki-stack \
  --namespace monitoring \
  --create-namespace \
  -f infra/monitoring-values.yaml

# Install Falco
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f infra/falco-values.yaml
```

### 3. Configure Grafana Dashboards
Automatically imports custom pod dashboards.

```bash
kubectl create configmap grafana-dashboard-pods \
  --namespace monitoring \
  --from-file=infra/pod-dashboard.json \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl label configmap grafana-dashboard-pods \
  --namespace monitoring \
  grafana_dashboard=1 \
  --overwrite
```

---

## Application Deployment

Use Helm to deploy or update the main application logic.

### Deploy / Update
Ensure `helm/values.yaml` contains the correct configuration (or override with `--set`).

```bash
helm upgrade --install pokero ./helm
```

### Verification
Check if the application and database pods are running:

```bash
kubectl get deployments
kubectl get pods
```

### First Time Setup (Production)
When deploying to a fresh cluster (and fresh DB), you must create the initial admin account manually.

```bash
# 1. Get the pod name
POD_NAME=$(kubectl get pod -l app=pokero-app -o jsonpath="{.items[0].metadata.name}")

# 2. execute createsuperuser
kubectl exec -it $POD_NAME -- python manage.py createsuperuser
```
*(Note: Standard database migrations are handled automatically by a Helm Job during deployment).*

---

## Accessing Monitoring & Observability

Monitoring services are not exposed publicly by default. Use port-forwarding to access them securely.

### Access Grafana
1. **Port Forwarding:**
   ```bash
   kubectl port-forward --namespace monitoring service/loki-stack-grafana 3000:80
   ```
2. **Open Browser:** [http://localhost:3000](http://localhost:3000)
3. **Credentials:**
   - **User:** `admin`
   - **Password:** Run the following command to retrieve it:
     ```bash
     kubectl get secret --namespace monitoring loki-stack-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
     ```

### SSH Tunnel (Optional)
If accessing via a Bastion Host/VM:
```bash
ssh -L 3000:127.0.0.1:3000 user@your-vm-ip
```

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

## CI/CD Pipeline
### 1. Workflow Configuration
* **File Location**: ```.github/workflows/docker-publish.yml```
* **Trigger**: Automatically executes on every ```push``` to the ```main``` branch.
* **Exclusions**: To save resources and prevent unnecessary builds, the pipeline ignores changes to the following files:
  * Documentation (```*.md```)
  * CI/CD configuration files (```zap-rules.tsv```, ```.semgrepignore```, ```.gitignore```)
  * Git submodules (```.gitmodules```)

### 2. Pipeline Stages (Jobs)

The pipeline is designed with a "Security First" approach, running multiple automated security scans before and after the build.

| Stage        | Tool      | Description                                                                                         |
|--------------|-----------|-----------------------------------------------------------------------------------------------------|
| Secret Scan  | gitleaks  | Scans the entire commit history for hardcoded secrets, passwords, or API keys.                      |
| IaC Scan     | trivy     | Scans Dockerfiles and Kubernetes manifests for security misconfigurations.                          |
| SCA     | pip-audit | Audits Python dependencies for known vulnerabilities (CVEs).                                        |
| SAST         | semgrep   | Analyzes source code for insecure coding patterns and logic flaws.                                  |
| Build & Push | Docker    | Builds the production-ready Docker image and pushes it to the GitHub Container Registry (GHCR).     |
| DAST         | OWASP ZAP | Deploys the app via Docker Compose and performs active security probes against the running service. |

### 3. Pipeline Logic & Dependencies

The pipeline follows a specific order to ensure that insecure code is caught as early as possible *(Shift Left)*:

1. **Initial Gate**: ```gitleaks``` runs first. If secrets are found, the pipeline stops immediately.
2. **Parallel Audits**: ```iac-scan``` and ```sca-scan``` run simultaneously to check environment and library safety.
3. **Code Analysis**: ```sast-scan``` runs only after the dependencies and IaC are verified.
4. **Deployment Prep**: ```build-and-push``` triggers only if all previous security scans (Gitleaks, SCA, IaC, SAST) pass.
5. **Runtime Audit**: Finally, ```dast-scan``` spins up the application in a temporary environment to perform a "black-box" security test.

### 4. Notes
* **ZAP Reports**: After a ```dast-scan``` completes, the scan reports (JSON/HTML) are available as GitHub Artifacts for audit purposes.

---

## Cluster Bootstrap (Infrastructure Setup)

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

### Accessing Grafana Loki SIEM Dashboard
Step-by-step procedure for setting up your monitoring dashboard in Grafana to analyze both Poker App logs and Falco security alerts.

**Step 1: Access the Explore Tab**

* Log in to your Grafana dashboard.
* In the left-hand sidebar, click on the Explore icon (it looks like a compass).
* At the top of the page, ensure your data source is set to Loki.

**Step 2: Add the Django Application Query**
1. In the first query field (Query A), enter the following to see your application logs: ```{app="pokero-app"}```
2. Press ```Shift + Enter``` to run. You will see the raw text logs from your Django container.

**Step 3: Add the Falco Security Query**
1. Click the + Add query button located below your first query field.
2. In the new field (Query B), enter the security stream with the JSON parser: ```{app="falco"} | json```
3. Now, Grafana will display both streams on a single timeline. Application logs will appear as text, while Falco logs will have searchable JSON fields.

---
## Falco Security Configuration
Short description for Falco custom rules and how to update them.

### 1. Edit Falco custom rules 

To modify or add security rules in Falco, you need to update the configuration stored in Kubernetes. Depending on your deployment method, use one of the following approaches:

**Method A: Using Helm**

If you deployed Falco using the Helm chart, the best practice is to update your ./infra/faclo-rules.yaml file under the  ```customRules``` section.
1. Edit your ```faclo-rules.yaml```
2. Apply the changes:
```bash
helm upgrade --install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  -f infra/falco-values.yaml
  
  ```

  **Method B: ConfigMap Edit**
1. Identify the ConfigMap name: ```kubectl get configmap -n falco```
2. Edit the resource:
```bash
kubectl edit configmap <falco-configmap-name> -n falco
```
3. After saving, Falco usually detects the change automatically. If not, restart the Falco pods:
```bash
kubectl rollout restart daemonset falco -n falco
```

### 2. Custom Security Rules Overview 

The following rules are implemented within the ```faclo-rules.yaml``` to detect anomalies and potential threats within the containerized environment especially for container escape. 

**Foundations: Lists and Macros**

* ```shell_binaries``` (List): Defines a collection of common shell interpreters (bash, sh, zsh, etc.) used for baseline terminal activity detection.
* ```spawned_process``` (Macro): Filters for events where a new process is initiated (execve).
* ```container``` (Macro): Ensures the rule applies strictly to containerized environments, excluding host-level noise.

**Network Security**
* **Listen on Suspicious Port**: Triggers a **WARNING** if a container in the default namespace attempts to listen on an unauthorized port. Authorized ports are limited to standard web and database services (80, 443, 8080, 3000, 5432, 3306).


**Privilege Escalation & Container Escape**
* **Sensitive Mount Operation**: A **CRITICAL** alert triggered when a mount command is executed inside a container. This is a common indicator of a container escape attempt or unauthorized filesystem manipulation.
* **Suspicious SU Usage**: Detects attempts to switch users to root using the su command. This is flagged as **CRITICAL** as it suggests an attempt to bypass standard permission sets.

**Reconnaissance & Discovery (MITRE ATT&CK)**

These rules detect "Discovery" techniques where an attacker tries to gather information about the system environment:

* **Command ```df```**: Detects filesystem reconnaissance (checking disk space and mount points).
* **Command ```hostname```**: Detects network reconnaissance (specifically using ```-I``` or ```-i``` to identify internal IP addresses).
* **Command ```ps```**: Detects process listing (searching for running services or security agents).

**Interactive Threats**
* **Terminal Shell in Container**: Monitors for the creation of an interactive shell (e.g., via ```kubectl exec```).


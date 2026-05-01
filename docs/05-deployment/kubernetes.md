# Kubernetes for LLM Workloads

> **TL;DR** — Running LLM application components (API services, Qdrant, Langfuse) on Kubernetes provides scalability and operational consistency; use HPA for bursty LLM call patterns and persistent volumes for vector store data.

## Overview

Kubernetes is a natural fit for LLM application infrastructure:
- **RAG API services** — stateless, horizontally scalable.
- **Vector databases** (Qdrant) — stateful, needs persistent volumes.
- **Observability** (Langfuse) — standard multi-container deployment.
- **Batch indexing jobs** — Kubernetes Jobs for one-off re-indexing.

## Deploying a RAG API Service

```yaml
# k8s/rag-api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: rag-api
  template:
    metadata:
      labels:
        app: rag-api
    spec:
      containers:
      - name: rag-api
        image: your-registry/rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: AZURE_OPENAI_ENDPOINT
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: endpoint
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: api-key
        - name: QDRANT_URL
          value: "http://qdrant:6333"
        resources:
          requests:
            cpu: "250m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: rag-api
spec:
  selector:
    app: rag-api
  ports:
  - port: 80
    targetPort: 8000
```

## Horizontal Pod Autoscaler

LLM workloads are bursty. Use HPA with custom metrics (queue depth, request latency):

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: rag-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: rag-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

## Deploying Qdrant on Kubernetes

Use the official Helm chart:

```bash
helm repo add qdrant https://qdrant.github.io/qdrant-helm
helm repo update

helm install qdrant qdrant/qdrant \
  --set replicaCount=1 \
  --set persistence.size=20Gi \
  --set resources.requests.memory=1Gi
```

Or with a StatefulSet for more control:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: qdrant
spec:
  serviceName: qdrant
  replicas: 1
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:latest
        ports:
        - containerPort: 6333
        volumeMounts:
        - name: data
          mountPath: /qdrant/storage
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

## Secrets Management

Do not hardcode Azure OpenAI keys. Use:

1. **Kubernetes Secrets** (base64 encoded, not encrypted by default):
   ```bash
   kubectl create secret generic azure-openai-secret \
     --from-literal=api-key="$AZURE_OPENAI_API_KEY" \
     --from-literal=endpoint="$AZURE_OPENAI_ENDPOINT"
   ```

2. **Azure Key Vault + CSI Driver** (recommended for production):
   ```yaml
   volumes:
   - name: secrets
     csi:
       driver: secrets-store.csi.k8s.io
       readOnly: true
       volumeAttributes:
         secretProviderClass: azure-openai-secrets
   ```

3. **Managed Identity** — Assign a pod identity with access to Azure OpenAI; no keys needed.

## Batch Indexing Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: reindex-wiki
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: indexer
        image: your-registry/rag-indexer:latest
        command: ["python", "index_documents.py", "--source", "docs/"]
        env:
        - name: QDRANT_URL
          value: "http://qdrant:6333"
```

## References

- Source: [Che-Chia Chang's Kubernetes talks and workshops](../../content/slides/)
- [Qdrant Helm Chart](https://github.com/qdrant/qdrant-helm)
- [Azure Workload Identity](https://azure.github.io/azure-workload-identity/)
- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-asia-east1}"
SERVICE_NAME="${GCP_SERVICE_NAME:-precious-metal-dashboard}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "Missing GCP_PROJECT_ID. Example:"
  echo "  GCP_PROJECT_ID=my-project-id GCP_REGION=asia-east1 ./deploy/gcp_deploy_cloud_run.sh"
  exit 1
fi

echo "Deploying ${SERVICE_NAME} to project ${PROJECT_ID} in region ${REGION}"

gcloud config set project "${PROJECT_ID}"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

gcloud run deploy "${SERVICE_NAME}" \
  --source . \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 1

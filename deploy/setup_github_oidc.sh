#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-project-6f7a4de7-bd07-408c-a53}"
REGION="${GCP_REGION:-asia-east1}"
SERVICE_NAME="${GCP_SERVICE_NAME:-precious-metal-dashboard}"
REPOSITORY="${GITHUB_REPOSITORY:-patricxie/precious-metal-premium-strategy}"
POOL_ID="${WIF_POOL_ID:-github-actions-pool}"
PROVIDER_ID="${WIF_PROVIDER_ID:-github-actions-provider}"
DEPLOYER_SA_ID="${DEPLOYER_SA_ID:-github-actions-deployer}"

GCLOUD_BIN="${GCLOUD_BIN:-gcloud}"
PROJECT_NUMBER="$("${GCLOUD_BIN}" projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
DEPLOYER_SA_EMAIL="${DEPLOYER_SA_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
BUILD_SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
RUNTIME_SA_EMAIL="$("${GCLOUD_BIN}" run services describe "${SERVICE_NAME}" --region "${REGION}" --format='value(spec.template.spec.serviceAccountName)')"

echo "Project: ${PROJECT_ID} (${PROJECT_NUMBER})"
echo "Repository: ${REPOSITORY}"
echo "Service: ${SERVICE_NAME}"
echo "Runtime SA: ${RUNTIME_SA_EMAIL}"
echo "Build SA: ${BUILD_SA_EMAIL}"

if ! "${GCLOUD_BIN}" iam service-accounts describe "${DEPLOYER_SA_EMAIL}" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" iam service-accounts create "${DEPLOYER_SA_ID}" \
    --display-name="GitHub Actions Cloud Run Deployer"
fi

"${GCLOUD_BIN}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOYER_SA_EMAIL}" \
  --role="roles/run.sourceDeveloper" \
  --quiet

"${GCLOUD_BIN}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${DEPLOYER_SA_EMAIL}" \
  --role="roles/serviceusage.serviceUsageConsumer" \
  --quiet

"${GCLOUD_BIN}" iam service-accounts add-iam-policy-binding "${RUNTIME_SA_EMAIL}" \
  --member="serviceAccount:${DEPLOYER_SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet

"${GCLOUD_BIN}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${BUILD_SA_EMAIL}" \
  --role="roles/run.builder" \
  --quiet

if ! "${GCLOUD_BIN}" iam workload-identity-pools describe "${POOL_ID}" --location="global" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" iam workload-identity-pools create "${POOL_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool"
fi

if ! "${GCLOUD_BIN}" iam workload-identity-pools providers describe "${PROVIDER_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --display-name="GitHub Actions Provider" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.aud=assertion.aud,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository=='${REPOSITORY}' && assertion.ref=='refs/heads/main'"
fi

"${GCLOUD_BIN}" iam service-accounts add-iam-policy-binding "${DEPLOYER_SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPOSITORY}" \
  --quiet

echo
echo "GitHub Actions OIDC is configured."
echo "Provider: projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo "Service account: ${DEPLOYER_SA_EMAIL}"

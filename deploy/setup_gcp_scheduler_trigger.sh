#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-project-6f7a4de7-bd07-408c-a53}"
PROJECT_NUMBER="${GCP_PROJECT_NUMBER:-37711474242}"
WORKFLOW_REGION="${GCP_WORKFLOW_REGION:-asia-east1}"
SCHEDULER_REGION="${GCP_SCHEDULER_REGION:-asia-east1}"
WORKFLOW_NAME="${GCP_WORKFLOW_NAME:-trigger-daily-update-dispatch}"
SCHEDULER_JOB_NAME="${GCP_SCHEDULER_JOB_NAME:-trigger-daily-update-job}"
SERVICE_ACCOUNT_ID="${GCP_TRIGGER_SA_ID:-github-actions-dispatcher}"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com"
SECRET_ID="${GCP_SECRET_ID:-github-actions-dispatch-token}"
SCHEDULE="${GCP_SCHEDULE:-30 8 * * *}"
TIME_ZONE="${GCP_TIME_ZONE:-Asia/Taipei}"
WORKFLOW_SOURCE="${GCP_WORKFLOW_SOURCE:-deploy/workflows/trigger_daily_update_dispatch.yaml}"
GCLOUD_BIN="${GCLOUD_BIN:-gcloud}"
REPOSITORY_PATH="${GITHUB_REPOSITORY_PATH:-patricxie/precious-metal-premium-strategy.git}"
WORKFLOWS_SERVICE_AGENT="service-${PROJECT_NUMBER}@gcp-sa-workflows.iam.gserviceaccount.com"

if [[ ! -f "${WORKFLOW_SOURCE}" ]]; then
  echo "Workflow source not found: ${WORKFLOW_SOURCE}"
  exit 1
fi

get_github_token() {
  if [[ -n "${GITHUB_ACTIONS_DISPATCH_TOKEN:-}" ]]; then
    printf '%s' "${GITHUB_ACTIONS_DISPATCH_TOKEN}"
    return 0
  fi

  local credential_file
  credential_file="$(mktemp)"
  printf 'protocol=https\nhost=github.com\npath=%s\n\n' "${REPOSITORY_PATH}" | git credential fill >"${credential_file}" 2>/dev/null || true
  awk -F= '$1=="password"{print substr($0,10)}' "${credential_file}"
  rm -f "${credential_file}"
}

GITHUB_TOKEN="$(get_github_token)"

if [[ -z "${GITHUB_TOKEN}" ]]; then
  echo "Unable to resolve a GitHub token. Set GITHUB_ACTIONS_DISPATCH_TOKEN or configure git credentials."
  exit 1
fi

echo "Using project ${PROJECT_ID}"
echo "Workflow region: ${WORKFLOW_REGION}"
echo "Scheduler region: ${SCHEDULER_REGION}"
echo "Scheduler cron: ${SCHEDULE} (${TIME_ZONE})"

"${GCLOUD_BIN}" services enable \
  workflows.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com

if ! "${GCLOUD_BIN}" iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" iam service-accounts create "${SERVICE_ACCOUNT_ID}" \
    --display-name="GCP Scheduler GitHub Actions Dispatcher"
fi

for attempt in 1 2 3 4 5; do
  if "${GCLOUD_BIN}" iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" >/dev/null 2>&1; then
    break
  fi
  sleep 3
done

if ! "${GCLOUD_BIN}" iam service-accounts describe "${SERVICE_ACCOUNT_EMAIL}" >/dev/null 2>&1; then
  echo "Service account did not become available in time: ${SERVICE_ACCOUNT_EMAIL}"
  exit 1
fi

"${GCLOUD_BIN}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/workflows.invoker" \
  --quiet

"${GCLOUD_BIN}" projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/logging.logWriter" \
  --quiet

if ! "${GCLOUD_BIN}" secrets describe "${SECRET_ID}" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" secrets create "${SECRET_ID}" --replication-policy="automatic"
fi

printf '%s' "${GITHUB_TOKEN}" | "${GCLOUD_BIN}" secrets versions add "${SECRET_ID}" --data-file=-

"${GCLOUD_BIN}" secrets add-iam-policy-binding "${SECRET_ID}" \
  --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --quiet

"${GCLOUD_BIN}" beta services identity create \
  --service="workflows.googleapis.com" \
  --project="${PROJECT_ID}" >/dev/null 2>&1 || true

for attempt in 1 2 3 4 5; do
  if "${GCLOUD_BIN}" iam service-accounts describe "${WORKFLOWS_SERVICE_AGENT}" >/dev/null 2>&1; then
    break
  fi
  sleep 3
done

"${GCLOUD_BIN}" iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
  --member="serviceAccount:${WORKFLOWS_SERVICE_AGENT}" \
  --role="roles/iam.serviceAccountTokenCreator" \
  --quiet

"${GCLOUD_BIN}" workflows deploy "${WORKFLOW_NAME}" \
  --location="${WORKFLOW_REGION}" \
  --source="${WORKFLOW_SOURCE}" \
  --service-account="${SERVICE_ACCOUNT_EMAIL}"

SCHEDULER_URI="https://workflowexecutions.googleapis.com/v1/projects/${PROJECT_ID}/locations/${WORKFLOW_REGION}/workflows/${WORKFLOW_NAME}/executions"
SCHEDULER_BODY='{"argument":"{}"}'

if "${GCLOUD_BIN}" scheduler jobs describe "${SCHEDULER_JOB_NAME}" --location="${SCHEDULER_REGION}" >/dev/null 2>&1; then
  "${GCLOUD_BIN}" scheduler jobs update http "${SCHEDULER_JOB_NAME}" \
    --location="${SCHEDULER_REGION}" \
    --schedule="${SCHEDULE}" \
    --time-zone="${TIME_ZONE}" \
    --uri="${SCHEDULER_URI}" \
    --http-method=POST \
    --headers="Content-Type=application/json,User-Agent=Google-Cloud-Scheduler" \
    --message-body="${SCHEDULER_BODY}" \
    --oauth-service-account-email="${SERVICE_ACCOUNT_EMAIL}"
else
  "${GCLOUD_BIN}" scheduler jobs create http "${SCHEDULER_JOB_NAME}" \
    --location="${SCHEDULER_REGION}" \
    --schedule="${SCHEDULE}" \
    --time-zone="${TIME_ZONE}" \
    --uri="${SCHEDULER_URI}" \
    --http-method=POST \
    --headers="Content-Type=application/json,User-Agent=Google-Cloud-Scheduler" \
    --message-body="${SCHEDULER_BODY}" \
    --oauth-service-account-email="${SERVICE_ACCOUNT_EMAIL}"
fi

echo
echo "Cloud Scheduler trigger is configured."
echo "Workflow: ${WORKFLOW_NAME}"
echo "Scheduler job: ${SCHEDULER_JOB_NAME}"
echo "Service account: ${SERVICE_ACCOUNT_EMAIL}"

#!/usr/bin/env bash
set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is required" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required" >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "${repo_root}" ]]; then
  echo "Run this from inside a git repo" >&2
  exit 1
fi

workflows_dir="${repo_root}/.github/workflows"
if [[ ! -d "${workflows_dir}" ]]; then
  echo "No .github/workflows directory found" >&2
  exit 1
fi

mapfile -t workflow_files < <(find "${workflows_dir}" -maxdepth 1 -type f -print | sort)
if [[ ${#workflow_files[@]} -eq 0 ]]; then
  echo "No workflow files found" >&2
  exit 1
fi

echo "Select workflow file:"
for i in "${!workflow_files[@]}"; do
  rel="${workflow_files[$i]#${repo_root}/}"
  printf "%2d) %s\n" "$((i+1))" "${rel}"
done

read -r -p "Enter number: " selection
if ! [[ "${selection}" =~ ^[0-9]+$ ]]; then
  echo "Invalid selection" >&2
  exit 1
fi

idx=$((selection-1))
if (( idx < 0 || idx >= ${#workflow_files[@]} )); then
  echo "Selection out of range" >&2
  exit 1
fi

workflow_rel="${workflow_files[$idx]#${repo_root}/}"

latest_run_json="$(gh run list --workflow "${workflow_rel}" --limit 1 --json databaseId,headSha,headBranch,displayTitle,createdAt,status,conclusion)"
run_id="$(echo "${latest_run_json}" | jq -r '.[0].databaseId // empty')"
head_sha="$(echo "${latest_run_json}" | jq -r '.[0].headSha // empty')"
head_branch="$(echo "${latest_run_json}" | jq -r '.[0].headBranch // empty')"
run_title="$(echo "${latest_run_json}" | jq -r '.[0].displayTitle // empty')"
created_at="$(echo "${latest_run_json}" | jq -r '.[0].createdAt // empty')"

if [[ -z "${run_id}" ]]; then
  echo "No runs found for workflow ${workflow_rel}" >&2
  exit 1
fi

echo "Latest run:"
echo "  workflow: ${workflow_rel}"
echo "  run_id:   ${run_id}"
echo "  branch:   ${head_branch}"
echo "  title:    ${run_title}"
echo "  created:  ${created_at}"
echo "  sha:      ${head_sha}"

commit_msg="$(gh api "/repos/{owner}/{repo}/commits/${head_sha}" --jq '.commit.message' 2>/dev/null || true)"
if [[ -n "${commit_msg}" ]]; then
  echo "  commit:   ${commit_msg%%$'\n'*}"
fi

out_root="${repo_root}/workflow-logs/${run_id}"
passed_dir="${out_root}/passed_jobs_logs"
failed_dir="${out_root}/failed_jobs_logs"
mkdir -p "${passed_dir}" "${failed_dir}"

jobs_json="$(gh run view "${run_id}" --json jobs)"
job_count="$(echo "${jobs_json}" | jq -r '.jobs | length')"
if [[ "${job_count}" == "0" ]]; then
  echo "No jobs found for run ${run_id}" >&2
  exit 1
fi

sanitize() {
  local s="$1"
  s="${s//\//-}"
  s="${s// /_}"
  s="${s//:/-}"
  s="${s//[^A-Za-z0-9_.-]/}"
  echo "${s}"
}

echo "Downloading job logs to: ${out_root}"

echo "${jobs_json}" | jq -r '.jobs[] | @base64' | while read -r row; do
  job_name="$(echo "${row}" | base64 --decode | jq -r '.name')"
  job_id="$(echo "${row}" | base64 --decode | jq -r '.databaseId')"
  conclusion="$(echo "${row}" | base64 --decode | jq -r '.conclusion // ""')"

  file_name="$(sanitize "${job_name}")"
  if [[ -z "${file_name}" ]]; then
    file_name="job-${job_id}"
  fi

  target_dir="${failed_dir}"
  if [[ "${conclusion}" == "success" ]]; then
    target_dir="${passed_dir}"
  fi

  echo "- ${job_name} (${conclusion:-unknown})"
  gh run view "${run_id}" --job "${job_id}" --log > "${target_dir}/${file_name}.log" || true

done

echo "Done"

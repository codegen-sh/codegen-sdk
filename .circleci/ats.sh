#!/usr/bin/env bash
if ! command -v jq &> /dev/null; then
    apt update
    apt install jq -y
fi
export PATH=$PATH:$HOME/.local/bin
echo "Git fetch"
git fetch
echo "Creating commit"
uv run --frozen codecovcli create-commit -t ${CODECOV_TOKEN}
echo "Creating report"
uv run --frozen codecovcli create-report -t ${CODECOV_TOKEN}
echo "Running static analysis"
uv run --frozen codecovcli static-analysis --token ${CODECOV_STATIC_TOKEN} --folders-to-exclude .venv
ATS_COLLECT_ARGS="${ATS_COLLECT_ARGS}${DEFAULT_TESTS},"
echo "Label analysis with base sha: ${BASE_SHA} and default tests: ${ATS_COLLECT_ARGS}"
runner_param="collect_tests_options=${ATS_COLLECT_ARGS}"
response=$(uv run --frozen codecovcli label-analysis --token ${CODECOV_STATIC_TOKEN} --base-sha=$BASE_SHA --dry-run --dry-run-format="json" --runner-param "$runner_param")
mkdir codecov_ats
jq <<< "$response" '.runner_options + .ats_tests_to_run | .[1:] | map(gsub("\""; "")) | join(" ")' --raw-output > codecov_ats/tests_to_run.txt
jq <<< "$response" '.runner_options + .ats_tests_to_skip | .[1:] | map(gsub("\""; "")) | join(" ")' --raw-output > codecov_ats/tests_to_skip.txt
testcount() { jq <<< "$response" ".$1 | length - 1"; }
run_count=$(testcount ats_tests_to_run)
skip_count=$(testcount ats_tests_to_skip)
echo "Run count: $run_count"
echo "Skip count: $skip_count"
if [ ! -s codecov_ats/tests_to_run.txt ]; then
    echo "No tests to run, collecting from default tests"
    PYTEST_ARGS="${COLLECT_ARGS} ${DEFAULT_TESTS}"
    echo "Using args: ${PYTEST_ARGS}"
    TESTS_TO_RUN=$(PYTEST_ARGS=${PYTEST_ARGS} ./.circleci/collect.sh)
    echo "${TESTS_TO_RUN}" > codecov_ats/tests_to_run.txt
    run_count=1
    echo "Added ${TESTS_TO_RUN} as fallback. New run count: $run_count"
fi

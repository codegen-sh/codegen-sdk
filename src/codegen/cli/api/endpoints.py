from codegen.cli.api.modal import MODAL_PREFIX

RUN_ENDPOINT = f"https://{MODAL_PREFIX}--cli-run.modal.run"
DOCS_ENDPOINT = f"https://{MODAL_PREFIX}--cli-docs.modal.run"
EXPERT_ENDPOINT = f"https://{MODAL_PREFIX}--cli-ask-expert.modal.run"
IDENTIFY_ENDPOINT = f"https://{MODAL_PREFIX}--cli-identify.modal.run"
CREATE_ENDPOINT = f"https://{MODAL_PREFIX}--cli-create.modal.run"
DEPLOY_ENDPOINT = f"https://{MODAL_PREFIX}--cli-deploy.modal.run"
LOOKUP_ENDPOINT = f"https://{MODAL_PREFIX}--cli-lookup.modal.run"
RUN_ON_PR_ENDPOINT = f"https://{MODAL_PREFIX}--cli-run-on-pull-request.modal.run"
PR_LOOKUP_ENDPOINT = f"https://{MODAL_PREFIX}--cli-pr-lookup.modal.run"

# Base URLs
CODEGEN_API_URL = "https://api.codegen.sh"
CODEGEN_WEB_URL = "https://codegen.sh"

# API endpoints
CODEGEN_API_DOCS = f"{CODEGEN_API_URL}/docs"
CODEGEN_API_EXAMPLES = f"{CODEGEN_API_URL}/examples"
CODEGEN_API_CODEMOD = f"{CODEGEN_API_URL}/codemod"
CODEGEN_API_CODEMOD_DEPLOY = f"{CODEGEN_API_URL}/codemod/deploy"
CODEGEN_API_CODEMOD_DEPLOY_STATUS = f"{CODEGEN_API_URL}/codemod/deploy/status"
CODEGEN_API_CODEMOD_DEPLOY_CANCEL = f"{CODEGEN_API_URL}/codemod/deploy/cancel"
CODEGEN_API_CODEMOD_DEPLOY_LOGS = f"{CODEGEN_API_URL}/codemod/deploy/logs"

# Web URLs
CODEGEN_WEB_PLAYGROUND = f"{CODEGEN_WEB_URL}/playground"
CODEGEN_WEB_DOCS = f"{CODEGEN_WEB_URL}/docs"

# System prompt URL
CODEGEN_SYSTEM_PROMPT_URL = "https://gist.githubusercontent.com/jayhack/15681a2ceaccd726f19e6fdb3a44738b/raw/17c08054e3931b3b7fdf424458269c9e607541e8/codegen-system-prompt.txt"

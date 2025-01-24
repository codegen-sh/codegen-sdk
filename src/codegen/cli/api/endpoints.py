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

# Quick PR Review Bot

This example demonstrates how to build a GitHub PR review bot using Codegen and Modal. The bot automatically reviews pull requests when they are opened or updated, providing quick, focused feedback on code quality, potential issues, and dependencies.

## Features

- Automatic PR review on open/update
- Analysis of modified code and its dependencies
- Concise, actionable feedback using GPT-4
- Deployed as a serverless service using Modal
- Posts reviews directly as PR comments

## Prerequisites

1. A Modal account and the Modal CLI installed
2. A GitHub account and personal access token
3. OpenAI API key (used by Codegen)

## Setup

1. Install dependencies:
   ```bash
   pip install modal-client codegen PyGithub
   ```

2. Create a Modal secret for the webhook:
   ```bash
   modal secret create webhook-secret
   ```

3. Create a Modal secret for your credentials:
   ```bash
   modal secret create quick-pr-review-secrets GITHUB_TOKEN=your_github_token OPENAI_API_KEY=your_openai_key
   ```

4. Deploy the service using Modal:
   ```bash
   modal deploy api.py
   ```

5. Set up GitHub webhook:
   - Go to your repository's Settings > Webhooks
   - Add new webhook
   - Get your webhook URL from Modal's dashboard or by running:
     ```bash
     modal endpoint show quick-pr-review/process_pr
     ```
   - Set content type to `application/json`
   - Select "Pull request" events
   - Enable the webhook

## How it Works

1. When a PR is opened or updated, GitHub sends a webhook event to the Modal endpoint
2. The service:
   - Initializes a Codegen codebase for the repository
   - Analyzes modified symbols and their dependencies
   - Generates a focused review using GPT-4
   - Posts the review as a PR comment

## Customization

You can customize the review behavior by:
- Adjusting the dependency depth in `review_pr()`
- Modifying the system prompt for different review focuses
- Changing the GPT-4 parameters (temperature, max_tokens)
- Adding additional analysis using Codegen's capabilities

## Security Notes

- Credentials are stored securely in Modal secrets
- Modal handles webhook authentication automatically
- Use appropriate GitHub token permissions (PR read/write access only)

## Example Output

The bot will post reviews in this format:

```markdown
## Quick Code Review

• Code Quality: [feedback on code structure and practices]
• Potential Issues: [identified bugs or concerns]
• Performance: [performance implications]
• Security: [security considerations]

[Additional context-specific feedback]
```

## Limitations

- Currently supports Python codebases only
- Reviews are focused on quick feedback rather than deep analysis
- Requires appropriate GitHub permissions and webhook setup 
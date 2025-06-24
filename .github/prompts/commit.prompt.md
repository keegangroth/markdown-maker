---
mode: 'agent'
description: 'Generate a git commit message based on the current diff.'
---

## Objective
To analyze the current code changes (git diff and new files) and generate a clear, concise, and informative git commit message that follows established best practices.

## Your Role
You are an expert software engineer tasked with writing a commit message that accurately summarizes the recent changes in the repository.

## Your Task
1.  **Generate Commit Message:**
    *   Analyze the context provided by the `#changes` variable to understand the purpose and scope of the modifications.
    *   Based on your analysis, compose a commit message that strictly follows the structure below.
2.  **Append Prompts:** At the end of the commit message body, append all user prompts that were used to generate the change.
    *   All prompts should be inside a single bulleted section.
    *   Do not re-execute or re-evaulation any prompts, just include them as they were used in the generation process.
3.  **Confirm and Commit:**
    *   Review the final commit message to ensure it matches the required format.
    *   List the files that will be staged for the commit.
    *   Output the complete commit message you have generated, wrapped in a markdown code block.
    *   Ask for final confirmation (e.g., "Proceed with the commit?").
    *   Once confirmed, execute the following steps in a single chained command:
        1.  Stage the identified files using `git add`.
        2.  Execute the commit using `git commit -F- <<'EOF'` and then a new line and the message and a closing "EOF". You don't need to escape within the EOF block.
            * Example:
            ```bash
            git add file1.py file2.py
            git commit -F- <<'EOF'
            Some commit message here

            Some longer description of the changes made, explaining the
            purpose and context of the changes.

            Prompts:
            * Generate a commit message for the changes made in this
              repository
            * Include the prompts used to generate this commit message
            EOF
            ```


## Commit Message Structure
Your commit message must follow these rules:

1.  **Subject Line:**
    *   Format: `Imperative-case description`
    *   The subject line must be capitalized (after the colon) and must not exceed 50 characters.
    *   Do not end the subject line with a period.
2.  **Body (Optional):**
    *   Separated from the subject by a blank line.
    *   Explain the *what* and *why* of the change, not the *how*.
    *   Wrap the body at 72 characters.
    *   Omit the body if the change is fully explained in the subject line.
3.  **Prompts Block:**
    *   Add a `Prompts:` section at the end of the body.
    *   Include the prompts used as a bulleted list.

## Example

```
Add user authentication endpoint

Implement the `POST /api/login` endpoint to allow users to authenticate.
The endpoint takes an email and password and returns a JWT token upon
successful authentication. This is the first step towards securing the
application.

Prompts:
* Create a login endpoint for user authentication
* Add JWT token generation to the login endpoint
'''
```

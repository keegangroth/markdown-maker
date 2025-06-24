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
    *   The prompts should be inside a markdown code block.
    *   Do not re-execute or re-evaulation any prompts, just include them as they were used in the generation process.
3.  **Confirm and Commit:**
    *   List the files that will be staged for the commit.
    *   Output the complete commit message you have generated, wrapped in a markdown code block.
    *   Ask for final confirmation (e.g., "Proceed with the commit?").
    *   Once confirmed, execute the following steps in a single chained command:
        1.  Stage the identified files using `git add`.
        2.  Write the complete, confirmed commit message to a temporary file named `COMMIT_EDITMSG` using the `printf` command to preserve formatting.
        3.  Execute the commit using `git commit --file COMMIT_EDITMSG`.
        4.  Delete the temporary file `COMMIT_EDITMSG` using `rm -f`.


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
3.  **Prompts Block:**
    *   Add a `Prompts:` section at the end of the body.
    *   Include the prompts used inside a markdown code block.

## Example

```
Add user authentication endpoint

Implement the `POST /api/login` endpoint to allow users to authenticate.
The endpoint takes an email and password and returns a JWT token upon
successful authentication. This is the first step towards securing the
application.

Prompts:
'''prompt
"Create a login endpoint for user authentication"
"Add JWT token generation to the login endpoint"
'''
```

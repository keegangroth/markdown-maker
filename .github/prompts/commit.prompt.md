---
mode: 'agent'
description: 'Generate a git commit message based on the current diff.'
---

## Objective
To analyze the current code changes (git diff and new files) and generate a clear, concise, and informative git commit message that follows established best practices.

## Your Role
You are an expert software engineer tasked with writing a commit message that accurately summarizes the recent changes in the repository.

## Your Task
1.  **Gather Context:**
    *   Run `git diff` to get the changes for all modified files.
    *   Run `git status --porcelain` to identify any new, untracked files.
2.  **Analyze the Changes:** Review the collected diff and the list of new files to understand the purpose and scope of the changes.
3.  **Generate the Commit Message:** Based on your analysis, compose a commit message that strictly follows the structure below.
4.  **Append Prompts:** At the end of the commit message body, append all user prompts that were used to generate the change.
    *   The prompts should be inside a markdown code block.
    *   Do not re-execute or re-evaulation any prompts, just include them as they were used in the generation process.
5.  **Confirm Before Committing:**
    *   Output the complete commit message you have generated, wrapped in a markdown code block.
    *   Ask for confirmation from the user before proceeding (e.g., "Does this commit message look correct?").
6.  **Execute the Commit:**
    *   Once the user confirms:
    1.  Stage the identified files using `git add`.
    2.  Write the complete, confirmed commit message to a temporary file named `COMMIT_EDITMSG`. Overwrite any existing file with that name.
    3.  Execute the commit using `git commit --file COMMIT_EDITMSG`.
    4.  Delete the temporary file `COMMIT_EDITMSG`.


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

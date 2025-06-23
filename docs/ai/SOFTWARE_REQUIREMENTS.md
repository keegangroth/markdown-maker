# Software Requirements Specification

## 1. High-Level Vision & Scope

### Problem Statement
To provide an easy way for developers to convert content from Confluence into Markdown, so it can be used with various AI tools. Support for Google Docs will be deferred to a future version.

### Target Audience
Developers who are members of a team in a larger organization.

### Core Value Proposition
The tool will be trivial to use, taking care of many steps for the user, and will support being run regularly to sync updates, avoiding cumbersome manual exports.

### Key Features (MVP)
1.  A command-line interface (CLI) to trigger the conversion.
2.  Support for Confluence URLs.
3.  Traversal of child/nested pages within a Confluence space.
4.  Conversion of basic text formatting (headings, lists, bold, italics, code blocks).
5.  A simple and secure authentication mechanism.

### Out of Scope (MVP)
*   Google Docs support.
*   Handling of images, charts, and diagrams.
*   Conversion of comments and suggestions.
*   A complex, dedicated "sync" feature (though the design should allow for it later).

## 2. Functional Requirements & User Stories

### User Story 1: Convert a single Confluence page
> **As a** developer,
> **I want to** run a single command that points to a Confluence page URL and lets me specify an output directory,
> **So that I can** get a clean Markdown file of its content saved to a specific location on my local machine.

#### Acceptance Criteria
*   **Given** I have authenticated with Confluence, **when** I run the command `convert --url "..."`, **then** a new Markdown file named after the Confluence page's title should be created in my current directory.
*   **Given** I have authenticated with Confluence, **when** I run the command `convert --url "..." --output-dir "docs/my-project"`, **then** a new Markdown file should be created inside the `docs/my-project` directory.
*   **Given** I specify an output directory that does not exist, **when** the command runs, **then** the directory (and any parent directories) should be created automatically.
*   **Given** the Confluence page contains headings, paragraphs, and a bulleted list, **when** the conversion runs, **then** the resulting Markdown file should correctly use `#` for headings and `*` for list items.
*   **Given** I provide an invalid or malformed Confluence URL, **when** the command runs, **then** it should output a clear error message (e.g., "Error: Invalid Confluence URL provided.").
*   **Given** I provide a valid URL for a page I don't have permission to access, **when** the command runs, **then** it should output a clear error message indicating a permission issue.

### User Story 2: Convert a Confluence page and its children
> **As a** developer,
> **I want to** provide a URL to a parent Confluence page and have the tool automatically convert that page and all of its child pages,
> **So that I can** get a complete documentation set as a collection of Markdown files that mirror the Confluence page hierarchy.

#### Acceptance Criteria
*   **Given** I provide a URL to a Confluence page that has child pages, **when** I run the command with a `--recursive` flag, **then** the tool should create a directory structure that matches the Confluence page hierarchy.
*   **Given** the Confluence pages contain links to other pages within the same conversion scope, **when** the conversion runs, **then** the links in the Markdown files should be updated to relative links that point to the corresponding local Markdown files.
*   **Given** the tool encounters a child page it doesn't have permission to access during a recursive conversion, **when** the command runs, **then** it should output a warning message for that specific page and continue converting the others.
*   **Given** I run the command *without* a `--recursive` flag, **then** only the single page specified by the URL should be converted, and no child pages should be fetched.

## 3. Non-Functional Requirements (NFRs)

### Performance
*   A single-page conversion should complete in under 60 seconds.
*   A large recursive conversion (e.g., 100+ pages) should complete in under 30 minutes.
*   For conversions taking longer than 15 seconds, the tool must provide real-time progress indication to the user.

### Scalability
*   **Content Scale:** The tool should be able to reliably handle recursive conversions of Confluence spaces containing up to 200 pages.
*   **Concurrent Execution:** The tool must support multiple, independent instances running concurrently on the same machine without interfering with each other.

### Security
*   **Configuration Files:** The tool will use a dual-file configuration system: a primary `config.yml` for non-secret settings and a local `.secrets.yml` for credentials. The secrets file must be included in `.gitignore`.
*   **Credential Handling:** The application must load credentials from the local secrets file and must not contain any hardcoded secrets.

### Usability & Accessibility
*   **Help Menu:** The CLI must provide a comprehensive help menu via a `--help` flag.
*   **Error Handling:** The tool must provide detailed and specific error messages, raising language-standard exceptions with full stack traces for debugging.

### Reliability
*   The tool should be robust and handle errors gracefully without crashing unexpectedly.

## 4. Data & Integration Requirements

### Data Model
*   **Page:** A representation of a Confluence page with its title, content, and relationship to child pages.
*   **Configuration:** Non-secret settings from the main config file.
*   **Credentials:** Secret API tokens from the local secrets file.

### Third-Party Integrations
*   Confluence Cloud REST API.

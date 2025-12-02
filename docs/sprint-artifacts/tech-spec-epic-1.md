# Epic Technical Specification: Foundation & Project Setup

Date: 2025-11-30
Author: Ra
Epic ID: 1
Status: Draft

---

## Overview

This epic establishes the fundamental technical groundwork for the Companion Network project. It focuses on setting up a modern, reproducible Python development environment, initializing the project structure with Google ADK and MCP components, and configuring essential dependencies. This foundation is a prerequisite for all subsequent agent development and ensures that the project starts with industry-standard best practices for version control, dependency management, and security.

## Objectives and Scope

**In-Scope:**
*   **Environment Setup:** Installation and configuration of `uv` (package manager) and Python 3.10+ runtime.
*   **Project Structure:** Creation of the directory hierarchy for `alice_companion`, `bob_companion`, `shared`, and the root application.
*   **Dependency Management:** Installation of core libraries (`google-adk`, `mcp[cli]`, `gradio`, `python-dotenv`) and generation of `uv.lock`.
*   **Configuration:** Setup of `.env` for secrets and `.env.example` for documentation.
*   **Version Control:** Initialization of the Git repository with a Python-AI specific `.gitignore`.
*   **Documentation:** Creation of a `README.md` with clear setup and run instructions.

**Out-Scope:**
*   Implementation of agent logic (Alice/Bob behavior).
*   Implementation of MCP tools or servers.
*   Development of the Gradio UI.
*   Database schema creation (beyond file exclusion).

## System Architecture Alignment

This epic directly implements the "Project Initialization" and "Version Control Strategy" sections of the [Architecture Document](docs/architecture.md).
*   **Tooling:** Adopts `uv` as the unified tool for dependency and environment management (ADR-005).
*   **Structure:** Implements the defined folder layout separating Alice, Bob, and Shared components.
*   **Security:** Enforces the "Local-First" and "Secrets Management" principles by configuring `.env` handling immediately.

## Detailed Design

### Services and Modules

This epic does not implement runtime services but establishes the module structure:

| Module/Directory | Responsibility |
| :--- | :--- |
| `alice_companion/` | Package for Alice's agent code, MCP server, and client. |
| `bob_companion/` | Package for Bob's agent code, MCP server, and client. |
| `shared/` | Package for shared utilities, data models, and logger. |
| `app.py` | Entry point for the Gradio application (placeholder/setup). |

### Data Models and Contracts

*   **Configuration:**
    *   `.env`: Stores `GOOGLE_API_KEY` (Secret).
    *   `pyproject.toml`: Defines project metadata (name, version) and dependencies.
    *   `uv.lock`: Defines exact transitive dependency versions.

### APIs and Interfaces

*   **CLI Commands:** The project will be runnable via `python app.py` (once implemented) and managed via `uv` commands (`uv sync`, `uv add`).

### Workflows and Sequencing

**Setup Workflow (Developer Experience):**
1.  Clone Repository.
2.  Install `uv`.
3.  Run `uv sync` (creates venv and installs locked deps).
4.  Copy `.env.example` to `.env` and add API key.
5.  Ready to code.

## Non-Functional Requirements

### Performance
*   **Installation Speed:** Dependency installation should be fast (leveraging `uv`'s caching and Rust implementation).

### Security
*   **Secret Management:** API keys must NEVER be committed to version control. `.gitignore` must explicitly exclude `.env`.

### Reliability/Availability
*   **Reproducibility:** The build must be deterministic across different machines using `uv.lock`.

### Observability
*   N/A for setup epic.

## Dependencies and Integrations

*   **Python:** 3.10+
*   **Package Manager:** `uv` (latest)
*   **Core Libraries:**
    *   `google-adk >= 1.19.0`
    *   `mcp[cli] >= 1.22.0`
    *   `gradio` (latest stable)
    *   `python-dotenv`

## Acceptance Criteria (Authoritative)

1.  **Environment Ready:** `uv` is installed, and a virtual environment is created and activated with Python 3.10+.
2.  **Structure Created:** Directories for `alice_companion`, `bob_companion`, and `shared` exist with `__init__.py` files.
3.  **Dependencies Installed:** `uv pip list` shows `google-adk`, `mcp`, `gradio`, and `python-dotenv`. `uv.lock` exists.
4.  **Secrets Configured:** `.env` exists and is ignored by Git. `.env.example` exists and is tracked.
5.  **Git Initialized:** Repo is initialized. `.gitignore` correctly excludes `.env`, `__pycache__`, and `.venv`.
6.  **Documentation:** `README.md` allows a fresh developer to set up the project successfully.

## Traceability Mapping

| AC ID | Requirement | Component | Test Idea |
| :--- | :--- | :--- | :--- |
| AC1 | FR26 (Foundation) | Env Setup | Run `uv --version` and `python --version` inside venv. |
| AC2 | FR26 (Foundation) | File System | Check for existence of directories and `__init__.py` files. |
| AC3 | FR26 (Foundation) | Dependencies | Run `uv pip list` and check for required packages. |
| AC4 | NFR-Security | Config | `git status` should NOT show `.env`. |
| AC5 | NFR-Reliability | Git | `git check-ignore .env` returns true. |
| AC6 | NFR-Usability | Docs | Follow README instructions on a clean shell. |

## Risks, Assumptions, Open Questions

*   **Risk:** `uv` is a newer tool; developers might be unfamiliar. **Mitigation:** Detailed setup instructions in README.
*   **Assumption:** User has a valid Google Cloud/AI Studio API key.

## Test Strategy Summary

*   **Manual Verification:** Execute the setup commands in the README from scratch to verify reproducibility.
*   **Git Check:** Verify `.gitignore` rules by attempting to add an ignored file.

## Post-Review Follow-ups

*   [ ] [Med] Update AC1 Version Requirement (AC #1) - Ref: Story 1.1

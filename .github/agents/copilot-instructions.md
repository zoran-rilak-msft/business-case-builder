# business-case-builder Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-10

## Active Technologies
- Python 3.12+ (helper scripts only; agent orchestration is Copilot-native) + python-docx (Word generation), matplotlib (charts), python-pptx (PPTX input parsing), azure-devops (ADO work item fetching), pydantic (data validation in scripts) (001-business-case-builder)
- File-system based — generated reports saved as .docx files; no database; conversation state managed by Copilot Chat contex (001-business-case-builder)

- Python 3.12+ + Semantic Kernel (agent orchestration), Microsoft Graph SDK (M365 data), Azure DevOps SDK, python-docx (Word generation), matplotlib (charts), python-pptx (PPTX input), MSAL (authentication), Rich (terminal UI) (001-business-case-builder)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12+: Follow standard conventions

## Recent Changes
- 001-business-case-builder: Added Python 3.12+ (helper scripts only; agent orchestration is Copilot-native) + python-docx (Word generation), matplotlib (charts), python-pptx (PPTX input parsing), azure-devops (ADO work item fetching), pydantic (data validation in scripts)

- 001-business-case-builder: Added Python 3.12+ + Semantic Kernel (agent orchestration), Microsoft Graph SDK (M365 data), Azure DevOps SDK, python-docx (Word generation), matplotlib (charts), python-pptx (PPTX input), MSAL (authentication), Rich (terminal UI)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->

# ApplyGenie MCP — Registry Submissions & Launch Directory 🚀

Use this document to register ApplyGenie across the global MCP ecosystem, registries, and developer directories.

---

## 1. Official MCP Community Registry (`modelcontextprotocol/servers` & `awesome-mcp-servers`)

### Pull Request Title:
`Add ApplyGenie: Autonomous job application copilot & interview engine`

### Entry to add under "Desktop & Browser Automation" or "Productivity":
```markdown
- [ApplyGenie](https://github.com/Eternalcodertanishq3/applygenie-mcp) - Autonomous job application copilot and mock interview engine using desktop vision, stealth browser form filling, and local SQLite application tracking.
```

### Pull Request Description:
```markdown
### Name
ApplyGenie MCP

### Description
ApplyGenie is a Python-based Model Context Protocol (MCP) server that empowers AI assistants (Claude Desktop, Cursor, Antigravity, VS Code) to:
1. Control desktop and capture screen state via fast `mss` grabs and DPI-corrected inputs.
2. Autonomously detect and populate complex ATS job application forms (Workday, Greenhouse, Oracle) using Playwright DOM + accessibility tree parsing.
3. Automatically upload PDF/DOCX resumes and manage a local answer memory bank.
4. Track all applied roles in a local, private SQLite database with conversion analytics.
5. Simulate technical coding interviews (Socratic 4-rung hint ladders) and behavioral STAR interviews ("I vs We" ownership analysis).

### Repository
https://github.com/Eternalcodertanishq3/applygenie-mcp

### Author
Tanishq Mangal (@Eternalcodertanishq3)

### License
MIT
```

---

## 2. Smithery.ai Registry

* **Submission Link:** [https://smithery.ai/new](https://smithery.ai/new)
* **Repository URL:** `https://github.com/Eternalcodertanishq3/applygenie-mcp`
* **Configuration:** Pre-configured via `smithery.yaml` in the repo root:
  ```yaml
  startCommand:
    type: stdio
    config:
      command: python
      args:
        - "-m"
        - "applygenie.server"
  ```

---

## 3. Glama.ai MCP Directory

* **Submission Link:** [https://glama.ai/mcp/servers](https://glama.ai/mcp/servers)
* **Repo:** `Eternalcodertanishq3/applygenie-mcp`
* **Tags:** `automation`, `browser`, `job-search`, `interview`, `desktop-control`

---

## 4. Community Launch Posts (Reddit & X/Twitter)

### X / Twitter Launch Pitch:
```text
Built & open-sourced ApplyGenie 🧞‍♂️ — an autonomous job application copilot & AI mock interview engine powered by Model Context Protocol (MCP)!

✨ Desktop vision & DPI-scaled mouse/keyboard control
⚡ Playwright stealth ATS form detector & autofill
📄 Local resume parser & SQLite application CRM
🎤 Socratic coding ladders + STAR behavioral coaching

Built with Python, FastMCP, and Playwright.
Check it out on GitHub: https://github.com/Eternalcodertanishq3/applygenie-mcp
```

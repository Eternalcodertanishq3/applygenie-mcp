# ApplyGenie Safety & Human-in-the-Loop Architecture 🛡️

ApplyGenie is designed from the ground up under a **Copilot philosophy**: it performs the tedious perceptual parsing, data mapping, and form filling tasks, but requires human agency for definitive actions.

---

## 1. Core Principles

1. **Zero Unattended Submissions**: The `browser_submit_form` tool demands an explicit `confirm=True` flag. By default, ApplyGenie populates 95% of the form, takes a screenshot for your visual verification, and pauses for your approval.
2. **Local Sovereignty**: All personal data (resumes, work history, phone, email, notes, interview records) is stored exclusively in `~/.applygenie/` on your physical machine. No central servers or cloud databases receive your data.
3. **Corner Failsafe**: In the event of unintended cursor control, moving the mouse to the top-left corner `(0, 0)` immediately halts execution via `FailsafeTriggered`.
4. **Rate Limiting & Human Cadence**: Automated key typing and clicks introduce random timing variations (jitter) to prevent website flagging and avoid runaway execution loops.
5. **Prompt Injection Defense**: Visual content on web pages is treated strictly as untrusted display input, preventing third-party website text from triggering unexpected local OS commands.

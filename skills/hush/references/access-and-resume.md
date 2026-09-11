# Access, interruption, and resumption

The person wants the task finished with minimal effort. A necessary unlock request helps finish it; silent omission does not.

## Request once, continue, resume

1. Inspect required access early, including the requested phone/device. Record the blocked source before visiting easier substitutes.
2. Ask for the smallest concrete action through asynchronous user input when available: “Please unlock iPhone Mirroring with your Mac login, then leave the iPhone locked and tell me when ready. I’ll continue website settings meanwhile.” If asynchronous input is unavailable, use the host's ordinary user-input channel and checkpoint. Never request credentials in chat.
3. Record one outstanding request per common cause. One locked phone can block many apps; it does not require one prompt per app. State which work the request enables.
4. Continue reachable independent tasks. Do not repeat unchanged access checks or prompts in a tight loop. A reply, service completion, or final reconciliation is a useful checkpoint.
5. On “done,” verify the actual state and account. Resume queued work with fresh UI observations. Acknowledgement is not evidence of authentication or permission to change unrelated settings.
6. If access still fails, explain the changed or persistent blocker once with a specific next action. Try a legitimate alternative route that serves the same channel, then continue elsewhere.
7. If only pending access remains, save an awaiting-access checkpoint and yield to the person. The task remains incomplete; resume on their next reply. Do not schedule background retries unless requested.

## Common boundaries

| Condition | Response |
| --- | --- |
| Mac login / Face ID / 2FA | Person authenticates in the relevant app. Do not disable security or extract saved secrets. |
| iPhone was unlocked and mirroring disconnected | Ask the person to lock it again, reconnect through visible controls, and verify the current screen. |
| Missing tool or OS automation permission | Identify the missing capability and request required setup through the host. A settings skill does not provide tools by itself. Continue other supported routes. |
| Wrong account, managed account, or shared-device ambiguity | Establish the intended account before changes. Do not log out another person or modify organization-wide defaults. Queue unresolved scope questions. |
| CAPTCHA, new legal terms, sensitive permission | Follow the host's approval/handoff rules. No silent acceptance or workaround. |
| Network error, session expiry, rate limit | Inspect error and saved state. Retry a transient failure proportionately or switch routes; honor service retry guidance and avoid request loops. |
| User takes over the UI | Stop conflicting actions, keep the checkpoint, and resume from fresh state when control is returned. |
| User cancels or narrows scope | Stop the affected work. Preserve verified changes and summarize outstanding items; do not keep pursuing the old scope. |

## Resuming safely

Keep account, channel/device, category, original value, intended value, observed saved value, evidence, and outstanding action distinct. If a previous attempt has uncertain state, inspect before writing. Do not overwrite newer choices, guess original values, or enable junk just to demonstrate that a toggle works. Undo restores only known changes from this run and requires its own verification; it is not a bulk reset.

An unsubscribe landing page is not always confirmation. Inspect whether the requested category actually changed, whether another submit is required, and whether the action affects a deliberate subscription or paid membership. Unknown or suspicious links should not receive credentials or private data; prefer the service's signed-in preferences.

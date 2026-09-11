# Testing Hush honestly

Testing must distinguish the instruction workflow from the optional report renderer. Passing report tests does not prove the agent discovered all apps, requested access correctly, made good decisions, or saved real settings.

For “test the skill,” carry forward the requested device/service scope from the conversation. Do not silently substitute a three-site smoke test for phone coverage. If the user explicitly requests a bounded sample, label the sample and untouched scope clearly. A request to test with fixtures or without changes must remain in that mode.

## Live acceptance checks

- **Access:** request essential access promptly, continue independent work, then resume the original queue once the user is ready. A pending request makes the dependent test blocked, not passed.
- **Discovery:** inspect actual notification activity when accessible, reconcile enabled/installed/account sources, and retain low-volume and undiscovered-source gaps. Screen Time use time, badges, and notification counts must not be conflated.
- **Decisions:** inspect descriptions, preserve direct/transactional and deliberate alerts, do not re-enable useful alerts already off, and seek finer controls for mixed categories. Check account/device/channel distinctions and off-master behavior.
- **Mutation:** where unwanted notifications are still enabled and the user authorized cleanup, capture before, change, save, and verify. If all sampled settings are already correct, mark mutation/save as **not exercised**. Do not turn marketing on to create a test case.
- **Recovery:** verify real interruptions/resumptions if they occur; otherwise use clearly labeled fixtures/manual scenario review. Never engineer an account lockout, security failure, or unwanted notification for a test.
- **Reporting:** generate a report from actual observations, distinguish verified changes from attempts and pre-existing values, and show pending access/scope gaps. Historical changes do not count as new changes.
- **Undo:** inspect the route and original value. Actual undo is **not exercised** unless an authorized change is restored and reverified. Do not claim execution from merely writing instructions.

Record each test as `passed`, `failed`, `blocked`, or `not_exercised`, with its method (`live`, `automated`, or `manual_review`) and concrete evidence. “No changes needed” can pass a rerun/idempotence check while leaving save/undo paths unexercised.

Before recommending public promotion, report tested platforms and outstanding coverage honestly. Keep live account evidence private. Fix and validate demonstrated instruction/report bugs; do not claim every edge case is solved. Never publish private test artifacts as a substitute for a synthetic demo.

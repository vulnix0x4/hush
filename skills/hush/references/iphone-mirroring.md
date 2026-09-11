# Physical iPhone through Mac

This route changes app/account settings, not notification interception. Use current host tool documentation; examples from the tested CUA environment are not assumed capabilities everywhere.

## Access and navigation

- Discover available apps as needed. The observed iPhone Mirroring bundle ID was `com.apple.ScreenContinuity`.
- Mac login prompts require user authentication. Using/unlocking the iPhone can end mirroring; it normally must remain locked. If access cannot be recovered with authorized actions, queue a final handoff and work elsewhere.
- Do not disable Face ID or device security. Some app authentication requires the physical phone.
- Observed shortcuts: Command-1 Home Screen, Command-2 App Switcher, Command-3 Spotlight. Check current tool instructions.
- Spotlight finds Settings/apps quickly. Wait for the field before typing; animation can drop or reorder characters. Verify the text and select-all/retype if needed. Click the app icon center, not its label or a similarly named document/Settings result.
- Settings' search can find Screen Time. Confirm its device and period.

## Observe before acting

Mirrored content may expose only window controls through accessibility. Use screenshots when semantic controls are absent. Derive coordinates from the latest screenshot; never store the reference session's dimensions or positions as reusable automation.

Refresh accessibility state after actions as the tool requires. An unchanged tree does not prove the phone was unchanged. Obtain a screenshot when the tree cannot answer what happened.

Half-open sheets and moving controls indicate animation; take a follow-up observation rather than tapping a transient position. Avoid arbitrary long sleeps. A Done tap immediately after a toggle can be ignored during saving; verify the sheet closed.

## Scrolling and recovery

Use the documented scroll API. The tested mirroring tool explicitly required scroll, not drag. Honor current host restrictions.

Short deterministic scroll batches help long lists; inspect between batches. Moving the target to a different visible list region or margin sometimes recovered scrolling. Increasing nominal page count did not reliably increase movement.

If stuck, inspect for modal/focus/nested-region/list-boundary issues. Try settings search, another account menu, or the website. Uber's alternative account route recovered an otherwise stuck task. Stop a route after repeated informed failures; do not retry endlessly.

Dismiss incidental non-binding notices only when their effect is clear. A camera-unavailable notice can appear even when only settings are needed. Repeated unrelated prompts such as Undo Typing indicate unreliable control: defer that route and continue elsewhere. Never type into an unverified field to get past a prompt.

Check every final toggle: rapid batches can leave one unchanged. Complete Save/Update/Done and reopen when needed. Keep prior values for undo. Do not retain screenshots of unrelated messages or private account details as public assets.

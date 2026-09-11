# Quiet Notifications

**Keep the useful alerts. Turn off the noise.**

A reusable Codex skill that works through notification settings across devices, apps, and signed-in services. It prioritizes actual notification senders, finds finer controls inside apps and websites, saves changes, and checks that they stuck.

It works autonomously through reachable settings and puts access blockers and ambiguous choices at the end. The default policy preserves communication, commitments, safety, transactions, and deliberately requested alerts while disabling promotions, engagement nudges, and signup-default marketing.

## Install

Copy `skills/quiet-notifications` into your Codex skills directory. From this repository:

```sh
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/quiet-notifications "${CODEX_HOME:-$HOME/.codex}/skills/"
```

If an existing `quiet-notifications` folder is present, inspect or back it up before replacing it. Start a new Codex task if the skill is not immediately discovered.

## Run

```text
Use $quiet-notifications to clean up unnecessary notifications across
my devices and services. Keep important and deliberately requested alerts.
Work through everything you can access and put unresolved items at the end.
```

You can narrow the scope or add exceptions in the same request: “Only this iPhone,” “Keep sports scores,” or “Keep all newsletters.” These preferences override the defaults. The skill can also be selected automatically for matching notification-cleanup requests.

## How it works

1. **Find the senders.** Rank actual Screen Time notification activity first, then OS permissions, installed apps, signed-in services, and focused history/mail discovery when authorized. Notification volume sets priority, not whether something is junk.
2. **Change the source.** Inspect category descriptions and separate push, email, SMS, and seller preferences. Use account controls instead of blanket app muting when useful alerts share the app.
3. **Verify the result.** Save explicitly, check fresh state, record original values, and keep undo instructions. An unsaved toggle never counts as a success.
4. **Account for the whole pass.** Every discovered account/channel has an outcome. Mixed controls stay intact when finer settings cannot be found; locked services wait in the final handoff.
5. **Report clearly.** A concise result plus a private offline report shows verified changes, useful alerts preserved, coverage, remaining work, and undo details.

[Read the default policy](skills/quiet-notifications/references/policy.md) · [View the fictional sample report](demo/report.md) · [Open the HTML preview locally](demo/report.html)

## What it needs

- Codex or a compatible agent that can read skills and control the relevant apps, browser, or account preferences.
- Existing signed-in sessions and authorized access. For physical iPhone settings, an available device-control route such as iPhone Mirroring with Mac UI automation is needed. This repository does not provide those tools.
- Python 3 for the optional report renderer; it has no third-party dependencies. Without it, the agent can report inline.

The skill includes navigation and recovery lessons from hands-on app cleanup, but interfaces change. It reads current controls instead of replaying fixed screen coordinates. Its strongest device-specific guidance covers iPhone through Mac; other platforms use the available tools and current UI.

This is a settings workflow, not an OS notification interceptor. It cannot guarantee permanent silence or access to every service. Authentication, missing controls, and mixed categories can leave partial coverage. Required approvals still apply; routine questions and access requests are consolidated at the end while other work continues.

It does not cancel paid subscriptions, leave rewards programs, change security settings, send messages, or set up recurring monitoring. It does disable clear marketing subscriptions through preference controls. Ambiguous editorial subscriptions are preserved for review.

## Reports and privacy

Generate a report from a private run ledger:

```sh
python3 skills/quiet-notifications/scripts/render_report.py /path/to/private-ledger.json --out /path/to/private-report
```

The [ledger schema](skills/quiet-notifications/references/reporting.md) explains the fields. The renderer produces HTML and Markdown without network requests or external assets. Keep personal run files outside this repository. Review and redact before sharing; `.gitignore` cannot protect files saved under arbitrary names.

Everything in `demo/` is fictional. The repository contains no private cleanup history, account identifiers, or screenshots.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 skills/quiet-notifications/scripts/render_report.py demo/ledger.json --out demo
```

Tests check report integrity, verification counts, contradictory states, and escaping. They do not simulate access to live apps or guarantee future settings behavior. [Behavior review cases](tests/behavior-cases.md) capture the decisions to check when adapting the skill.

## License

MIT. Reuse and adapt the skill; keep personal account evidence out of contributions.

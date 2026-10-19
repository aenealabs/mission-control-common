# How Mission Control works

Mission Control is a set of small tools for running engineering IT products: each one takes a
problem end to end, shows its work, and leaves the decisions to people. Every app runs on its
own; connected, they hand work to each other instead of re-typing it.

## The same rules in every app

| Who | Does what |
| --- | --- |
| **Code** | Computes every score, count, date, and threshold. The rules are written down and shown next to the result. |
| **The AI** | Reads and drafts: contracts, transcripts, tickets, requests. Everything it says must quote its source or match a value, and code checks that before anything is used. What fails a check is shown and flagged, never silently used. |
| **A person** | Decides. Proposals from the rules or the AI are only proposals. Overriding a proposed score, rating, roadmap placement, fix, or outcome, rejecting a finished draft, or dropping anything the AI drafted or extracted needs a reason, which is kept with the decision. Rewording a draft needs no reason, but the AI's original is kept beside it and the change is logged. |
| **The audit log** | Records every reading, decision, sync, and hand-off, with who did it, and every refused attempt. Each app's log is searchable. |

Nothing writes to a system of record (PLM, ERP, the work tracker, the directory) without a
person approving it, and most connections are read-only.

## How work moves between apps

All hand-offs go to **Backlog Pilot's inbox**. Nothing enters the backlog directly: someone
opens the item in Backlog Pilot, the AI drafts stories from it, and a person reviews them.

| From | Sends | Why |
| --- | --- | --- |
| Leadership Pilot | Problems heard in interviews; proposed personas | Turn what stakeholders said into traced backlog work |
| PLM Insight | Data-quality and engineering-change problems | Get recurring data issues fixed at the source |
| Support Pilot | Recurring problems behind many tickets | Fix the cause, not each ticket |
| App Portfolio | Migrate and Eliminate decisions | Plan the retirement work |

Each item keeps a link back to where it came from, so a story can always be traced to the
interview, ticket cluster, or decision behind it. Leadership Pilot also reads Backlog Pilot's
roadmap (read-only) for status reporting.

## Connecting the apps

Two settings, the same in every app:

- `MISSION_CONTROL_APPS` lists the apps and their addresses, for the app menu and these pages:
  `Backlog Pilot=https://bp.example.com, Leadership Pilot=https://lp.example.com, ...`
- A shared suite token (each app's `*_SUITE_TOKEN`, Backlog Pilot's `BP_SUITE_TOKEN`) lets an
  app post to the inbox. Without it, the app runs on its own and the send buttons are hidden.

Each app also needs Backlog Pilot's address (its `*_BACKLOG_URL` setting) to send work there.

## Signing in and roles

In the demo, a menu in the app bar switches between fictional people. With single sign-on
(Microsoft Entra ID or any OpenID Connect provider), people sign in with their work account
and an app role makes someone an **approver**. Approvers make the decisions; what else each
role can do is on each app's Help pages.

Every refused attempt is in the audit log: an action someone is not allowed to take, an
action tried without signing in, a failed sign-in, and a request to Backlog Pilot's suite API
without the right token. Opening a page while signed out is not refused; it asks you to
sign in.

## The demo

Every app ships with fictional data and recorded AI readings, so the whole suite runs offline
with no AI account. The mode chip in the app bar says which mode is on. Set the app's
provider setting to use the Claude API live.

## What the apps share

The app menu, these pages, and the base look (Brightlayer UI colors and components) come from
one shared package, `mission-control-common`, so a fix or a new app in the menu is made once.
Each app keeps its own screens, rules, and data.

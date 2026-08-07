# Diagnostic Zones (ADT - Agentic Delegation Trust)

The TM x DOK matrix produces seven diagnostic zones that reveal the health of the collaboration practice.

## Zone Definitions

| Zone | Description | Signal | Action |
|------|-------------|--------|--------|
| **Frontier** | TM and DOK matched and growing together | Operating at the productive edge | Document and share |
| **Growing** | Approaching a match between tool sophistication and cognitive depth | Building toward effective use | Keep pushing DOK 3+ work |
| **Leveraging** | Strategic thinking encoded in the system (recipes, workflows, conventions) | Prompt-level DOK appears low because complexity lives in configuration | Protect this mode for execution weeks |
| **Expected** | Tool usage and cognitive depth appropriate for current level | Healthy starting position | Ask "why" before implementing |
| **Thinking Ahead** | Cognitive depth exceeds tool sophistication | Thinking at a higher level than tools support | Adopt more powerful orchestration |
| **Underutilizing** | Tool sophistication exceeds cognitive depth with no encoded depth | Powerful tools for simple tasks | Deepen the questions being asked |
| **Overpowered** | Significant mismatch between tool complexity and task depth | Resources spent without proportional return | Redirect toward problems requiring analysis |

## The Matrix

```
              DOK 1         DOK 2          DOK 2+C≥10%    DOK 3           DOK 4
            (Recall)    (Application)   (Leveraging)  (Strategic)     (Extended)
           +----------+--------------+--------------+-------------+-------------+
Tier 5-6   | Over-    | Underutil-   | Leveraging   |  Frontier   |  Frontier   |
(Symphony/ | powered  |   izing      |              |             |             |
 Virtuoso) |          |              |              |             |             |
           +----------+--------------+--------------+-------------+-------------+
Tier 3-4   | Over-    |  Expected    |   Growing   |  Frontier   |
(Ensemble/ | powered  |              |             |             |
 Chamber)  |          |              |             |             |
           +----------+--------------+-------------+-------------+
Tier 1-2   | Expected |   Growing    |  Thinking   |  Thinking   |
(Solo/     |          |              |   Ahead     |   Ahead     |
 Duet)     |          |              |             |             |
           +----------+--------------+-------------+-------------+
```

## Zone Calculation Logic

```
DOK >= 3.0 -> dok_band = 4
DOK >= 2.5 -> dok_band = 3
DOK >= 2.0 -> dok_band = 2
DOK <  2.0 -> dok_band = 1

TM Tier 5-6:
  dok_band >= 3 -> Frontier
  dok_band == 2 AND compression >= 10% -> Leveraging
  dok_band == 2 AND compression < 10%  -> Underutilizing
  dok_band == 1 -> Overpowered

TM Tier 3-4:
  dok_band >= 4 -> Frontier
  dok_band == 3 -> Growing
  dok_band == 2 -> Expected
  dok_band == 1 -> Overpowered

TM Tier 1-2:
  dok_band >= 3 -> Thinking Ahead
  dok_band == 2 -> Growing
  dok_band == 1 -> Expected
```

## Leveraging vs Underutilizing

When a practitioner operates at TM 5+ with DOK band 2, the question is: is the low prompt-level DOK a problem or a feature?

| | Leveraging | Underutilizing |
|---|---|---|
| Compression | >= 10% | < 10% |
| Meaning | Strategic thinking encoded in recipes, workflows, conventions | Tools genuinely exceed cognitive depth |
| Signal | Healthy. The cognitive investment happened at design time. | Opportunity. The tools are capable of more. |
| Typical pattern | URL triggers full review workflow; "proceed" executes multi-step orchestration; parallel sub-agents batch-process work | Long explicit prompts for simple tasks; no delegation patterns; tools used as chat |
| Growth nudge | Protect this mode. When design work returns, depth will follow. | Deepen the questions. Build recipes to encode repeated patterns. |

**Source:** Dakota Fabro (2026), Three Dimensions Framework, Block Builder Fellowship

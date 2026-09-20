# 0001. Record architecture decisions as ADRs
- Status: Accepted
- Date: 2026-09-18

## Context
The repo will be extended in later iterations, possibly by another AI assistant using Spec Driven Development.
Chat history is not a durable place for decisions.

## Decision
Every non-trivial decision gets an ADR in `docs/adr/` (template in `README.md`). Requirements and acceptance
criteria live in `docs/spec.md`. Agent-facing working rules live in `AGENTS.md`.

## Consequences
+ Decisions and their reasons survive across sessions and tools.
- ADRs must be updated (or superseded, never silently edited) when a decision changes.

## Alternatives considered
Decisions only in the README (mixes how-to with why); no written record (loses context).

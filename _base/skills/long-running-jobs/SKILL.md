---
name: long-running-jobs
description: Discipline for work that takes minutes to hours — simulations, synthesis and place-and-route, long builds, batch conversions, hardware sweeps. Use when a command will not return promptly, when several such jobs run at once, when a job seems finished but produced no verdict, when stray processes hold files or burn CPU, or when deciding whether to wait, poll, or kill. Covers bounding every run, checking the artifact instead of the notification, cleaning orphans before starting, and reporting honestly whether work is actually in progress.
---

# Long-Running Jobs

## Core Goal

Know, at any moment, whether work is actually progressing — and be able to say
so truthfully. A job that is running, a job that finished an hour ago, and a job
that hung are three different states, and they look identical from the outside
unless you check.

## The Rule That Matters Most

**Check the artifact, not the notification.**

A completion notice may never arrive: the harness can lose a background task, a
process can outlive its parent, a wrapper can exit while its child keeps
running. Waiting for the notice while the result already sits on disk is the
most expensive way to be idle, and it looks — to the person watching — exactly
like working.

Measured 27.08.2026: a dual-simulator run finished at 13:23 and the result was
not collected until 14:31. An hour of nothing, spent waiting for an event that
had already happened.

So: **poll the output file, the log, the report, the exit marker.** Ask "is the
answer on disk yet?", never "has anyone told me it is done?".

## Bound Every Run

Anything that can run forever eventually will.

- Give every job a wall-clock limit, even ones that "obviously" terminate.
- A job that prints its summary is **not** necessarily a job that exited. Verify
  the process is gone, not that the output looks complete.
- Prefer a self-terminating job (a testbench with `$finish`, a script with an
  explicit exit) over an externally-killed one. When the job cannot terminate
  itself, say so out loud at launch, so the limit is a known part of the plan
  rather than a surprise.

Measured 27.08.2026 on this project: `run_verilator.sh` used Verilator's
generated main, which loops until `$finish`. Most testbenches here have none —
20 of 89. Five such runs accumulated from midday, each burning 20 000–35 000
seconds of CPU, printing their summaries and never exiting. They also held files
open and broke later runs. The fix was one `timeout` plus a warning when the
testbench has no `$finish`.

## Clean Before You Start, Not After

Orphaned processes hold locks on working directories and libraries. The next run
then fails for a reason that has nothing to do with what changed, and the
failure is easy to misread as a defect in the work.

- Before launching, check for and remove stragglers from previous attempts.
- After killing a job, verify it is actually gone before relaunching.
- Symptom to recognise instantly: `Device or resource busy` on a working
  directory, or a tool complaining it cannot access its own library.

## Running Several At Once

- Jobs writing into the **same** working directory cannot run in parallel; they
  clobber each other's scratch state. Parallelise across directories.
- Keep a bounded number in flight. More parallel jobs than cores turns a
  ten-minute wait into an hour and makes every timing measurement noisy.
- Record what each job is for. "Four processes are running" is not a status; it
  is an admission that the status is unknown.

## Report Honestly

When asked whether work is in progress, check first and answer from the check.

- If nothing is running, say nothing is running.
- If a job finished and the result was not collected, say that, and say for how
  long.
- Do not describe a launched job as progress until its result exists.

The failure mode is not idleness; it is **reporting activity that is not
happening**. That costs trust far beyond the wasted time.

## Learning

When a long job surprises you — hangs, finishes silently, leaves debris, or
turns out to have been dead for an hour — record the mechanism here with the
measurement that revealed it. Tool-specific launch recipes belong in that tool's
own skill; what belongs here is the discipline that applies to all of them.

# Architecture

## One automation blueprint, one helper

The blueprint is a single automation blueprint, imported from a URL and instantiated once per
appliance. Its state lives in one user-created `input_select`. An automation blueprint was chosen
over a template blueprint because it imports from the UI, Spook can offer updates for it, and an
existing `input_select` keeps every dashboard and automation that already reads it working.

A helper-free variant, a template blueprint that creates its own state sensor, is deferred until
this state machine has proven itself on real appliances.

## No timer or self-trigger helpers

Debouncing uses the `for:` option of `numeric_state` triggers, so a dip shorter than the finish
delay never reaches the state machine. `for:` restarts when Home Assistant restarts or automations
reload, so a reconcile step re-derives the state from current readings at startup and on reload.

## Interrupted jobs

`paused` and `detached_overload` always mean a job was running and was interrupted; `unplugged`
always means no job was running when power was cut. A paused job that does not draw power again
within the resume grace period ends as `idle`, and is never reported as finished.
A job cut off by an overload stays `detached_overload` through any switching of the plug. Either
kind of interruption is abandoned once the plug has been back on, and any overload clear, for the
whole grace period, counted from whichever came last.

## Queued runs

The automation runs in `queued` mode, so a user's slow action is never cancelled by the next power
reading, and triggers that fire meanwhile are applied afterwards in the order they fired. No run
waits through a change that a queued trigger could act on: every wait ends on such a change and
leaves it to that trigger's own run.

## Configuration check

Each run first checks that the helper has all six state labels as options, that the labels are
distinct, and that the finish threshold is below the start threshold. Every label is required, even
for a plug without a switch or overload sensor, so setup is one fixed list to copy. Options are not
added automatically: `input_select.set_options` changes them only until Home Assistant restarts,
after which the helper would discard its saved state. A configuration that fails writes nothing.
The problem is shown as a persistent notification at startup, on reload, when the automation is
switched on or when the helper's options change, and is cleared once the check passes.

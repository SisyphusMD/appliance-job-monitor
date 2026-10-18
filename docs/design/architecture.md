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

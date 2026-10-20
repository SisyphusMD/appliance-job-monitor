# appliance-job-monitor

A Home Assistant blueprint that tells when a washer, dryer or dishwasher starts, finishes, is
paused or is abandoned, using nothing but the power reading of the smart plug it is connected to.

> **Primary repository**: developed at
> [forgejo.bryantserver.com/SisyphusMD/appliance-job-monitor](https://forgejo.bryantserver.com/SisyphusMD/appliance-job-monitor).
> The [GitHub copy](https://github.com/SisyphusMD/appliance-job-monitor) is a read-only mirror.
> **Please file issues and pull requests on
> [GitHub](https://github.com/SisyphusMD/appliance-job-monitor/issues).** The Forgejo repository
> does not take external issues.

## What it does

Each appliance gets one `input_select` helper that holds its state: `idle`, `job_ongoing`,
`paused`, `job_completed`, `unplugged` or `detached_overload`. The blueprint moves it between those
states from the plug's power reading, and runs your own actions at each step, such as a phone
notification when a job finishes.

- A job starts when power stays above a threshold, and finishes when it stays below one for a
  configurable time, so short dips during a cycle never end a job early.
- Switching the plug off mid-job pauses the job instead of finishing it, and no "finished"
  notification is sent for a job that never resumed.
- Only real power changes are considered, so attribute-only updates from a Zigbee plug do not
  wake the automation.
- State labels are configurable, and the defaults match the
  [leofabri appliance status monitor](https://github.com/leofabri/hassio_appliance-status-monitor),
  so dashboards built for it keep working.

## Install

[![Open your Home Assistant instance and show the blueprint import dialog with this blueprint pre-filled.](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2FSisyphusMD%2Fappliance-job-monitor%2Freleases%2Flatest%2Fdownload%2Fappliance-job-monitor.yaml)

Or go to **Settings > Automations & scenes > Blueprints > Import blueprint** and paste:

```text
https://github.com/SisyphusMD/appliance-job-monitor/releases/latest/download/appliance-job-monitor.yaml
```

That link always serves the newest release, so re-importing the blueprint from its menu on the
Blueprints page updates it. Home Assistant 2024.10 or newer is required.

## Set up an appliance

### 1. Create the state helper

Go to **Settings > Devices & services > Helpers > Create helper > Dropdown**, name it (for example
"Washer state") and add these six options:

```text
idle
job_ongoing
paused
job_completed
unplugged
detached_overload
```

All six are needed even if the plug has no switch or overload sensor. If you change the state
labels in the blueprint, use your labels here instead.

If you keep helpers in YAML, a [package](https://www.home-assistant.io/docs/configuration/packages/)
does the same:

```yaml
input_select:
  washer_state:
    name: Washer state
    icon: mdi:washing-machine
    options:
      - idle
      - job_ongoing
      - paused
      - job_completed
      - unplugged
      - detached_overload
```

Leave out `initial:`. With it, the helper resets on every restart, and a job running at that moment
would be forgotten.

### 2. Create the automation

Go to **Settings > Automations & scenes > Blueprints**, pick **Appliance job monitor** and fill in:

- **Power sensor**: the plug's power reading, in watts.
- **State helper**: the dropdown from step 1.
- **Plug switch** (optional): the plug's on/off switch. With it, switching a running job off
  pauses the job instead of finishing it.
- **Overload sensor** (optional): a binary sensor that turns on when the plug trips on overload.
- **Thresholds and timing**: a job starts once power stays above the start threshold for the start
  delay, and finishes once it stays below the finish threshold for the finish delay. The defaults
  are 5 W, 3 W and 10 seconds. A dishwasher that sits near 0 W while drying needs a
  finish delay longer than its longest quiet spell, often a few minutes.
- **Actions**: what to run at each step. For example, under **When a job finishes**:

```yaml
action: notify.mobile_app_your_phone
data:
  message: The washer is done.
```

Create one automation per appliance, each with its own helper.

If something is wrong with the setup, such as a missing option, the automation does nothing and a
notification titled "*name* is not running" says what to fix. It clears itself once the setup is
right.

## States

| State | Meaning |
| --- | --- |
| `idle` | Nothing running. |
| `job_ongoing` | A job is running. |
| `paused` | A running job was switched off at the plug. It resumes if the appliance draws power again. |
| `job_completed` | The last job finished. Stays until the next job starts or the plug is switched off. |
| `unplugged` | The plug was switched off, or tripped on overload, with no job running. |
| `detached_overload` | The plug tripped on overload during a job. It resumes if the appliance draws power again. |

A paused or overload-tripped job that has not drawn power again within the resume grace period
(5 minutes by default) of the plug being back on and any overload clearing goes back to `idle`,
and runs **When a paused job never resumes** instead of reporting a finished job.

## Moving from the leofabri blueprint

Keep your existing dropdown helper, so dashboards and automations that read it keep working, and
check that it has all six options above. Create an automation from this blueprint pointing at it,
then delete the old automation. The old blueprint's other helpers (the job cycle, self-trigger and
timer) are not used and can be deleted once you no longer need them.

## License

[MIT](LICENSE).

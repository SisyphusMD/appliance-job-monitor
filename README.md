# appliance-job-monitor

A Home Assistant blueprint that tells when a washer, dryer or dishwasher starts, finishes, is
paused or is abandoned, using nothing but the power reading of the smart plug it is connected to.

> **Primary repository**: developed at
> [forgejo.bryantserver.com/SisyphusMD/appliance-job-monitor](https://forgejo.bryantserver.com/SisyphusMD/appliance-job-monitor).
> The [GitHub copy](https://github.com/SisyphusMD/appliance-job-monitor) is a read-only mirror.
> **Please file issues and pull requests on
> [GitHub](https://github.com/SisyphusMD/appliance-job-monitor/issues).** The Forgejo repository
> does not take external issues.

> **Status: in development.** There is no release yet, so there is nothing to import.

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

## License

[MIT](LICENSE).

# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-20

### Added

- A Home Assistant automation blueprint that tracks a washer, dryer or dishwasher through its jobs
  from its smart plug's power reading, keeping the state in a dropdown helper with six options:
  idle, job_ongoing, paused, job_completed, unplugged and detached_overload.
- Optional plug switch: a job switched off midway is paused instead of finished, resumes when the
  appliance draws power again, and is abandoned after a grace period otherwise.
- Optional overload sensor: a job cut off by an overload trip is marked as such and handled like a
  paused job.
- Actions for each step: job started, resumed, finished, paused, abandoned, unplugged and cut off
  by overload.
- A persistent notification naming what to fix when the setup is incomplete or invalid.

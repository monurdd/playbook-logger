# Playbook Logger

Playbook Logger is a callback plugin example that writes task results as line-delimited JSON (JSONL) into the `logs/` directory when running Ansible playbooks.

Features
- Produces a JSONL logfile per run with a unique `session_id`.
- Log filename format: `./logs/<playbook>-<session_id>.jsonl` (when playbook name is available).
- Payload fields: `@timestamp`, `session_id`, `playbook`, `play`, `task`, `host`, `status`, `changed`, `duration_ms`, `msg`, `module`, `item_count`.

Requirements
- Ansible
- Python 3

Installation / Activation
1. Ensure the `callback_plugins/` folder is present in the project and enable the callback plugin in `ansible.cfg`. Example:

```ini
[defaults]
callbacks_enabled = playbook_logger
callback_plugins = /absolute/path/to/playbook-logger/callback_plugins
```

2. Run playbooks normally:

```bash
ansible-playbook -i inventory/hosts playbooks/loop.yml
```

Output / Logs
- Generated logs are written to the `logs/` directory.
- Example file: `logs/loop-370af263-a05c-4014-b29f-8425104c2358.jsonl`.
- Each line is a valid JSON object representing the result of a single task.

Troubleshooting
- If no log file appears, ensure Ansible is reading the intended `ansible.cfg` (Ansible ignores a local `ansible.cfg` in a world-writable directory).
- Verify write permissions for the `logs/` directory.

Development / Notes
- The `playbook` field is used in the filename when the playbook path/name is available; the `play` field may be `null` when plays inside the playbook do not have a `name` attribute.


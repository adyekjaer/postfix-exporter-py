# Postfix Exporter Py

**postfix-exporter-py** is a Prometheus exporter written in Python that reads Postfix mail logs and exposes relevant metrics in a highly configurable and easy-to-use way. This exporter allows you to monitor your Postfix mail server performance, queue statistics, delivery status, and more in real-time via Prometheus.

It is meant to run in a docker conainer under e.g. docker compose and not directly on the host although that is supported.
You would need to create your own systemd files

---

## Alternatives in GoLang
  * https://github.com/Hsn723/postfix_exporter
  * https://github.com/sergeymakinen/postfix_exporter

Thanks to both projects for test files and inpiration

---

## Features

* Parses Postfix `mail.log` files to extract key metrics.
* Exposes metrics such as:
  * Number of messages in queue
  * Deferred, bounced, and rejected messages
  * Number of recipients per message
  * SMTP rejects
* Fully configurable log path, metrics via config file

---

## Todo
  * Delivery delays and status codes
  * Work as a systemd process
  * Work in a kubernetes environment

---

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/adyekjaer/postfix-exporter-py.git
cd postfix-exporter-py

# Optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Start tailing mail.log
python src/postfix_exporter.py <some flags>
```

## Docker compose

```bash
# Clone the repository
git clone https://github.com/adyekjaer/postfix-exporter-py.git
cd postfix-exporter-py

# Optional: edit compose.yaml
vim compose.yaml

# Start tailing mail.log
docker compose up
```

---

## Configuration

Configuration is provided via a YAML file (default: `config.yaml`).
This file is more or less just regexes to suit your needs.
You'll need to provide process name, subprocess, name of section, metric type and the regex.
With a process and subprocess all regexes are performed in sequence until match is found - order as you see fit if required.

There are 3 static metrics that are build-in:

  * postfix_queue_length (Gauge)
  * postfix_message_size (Histogram)
  * postfix_message_nrcpt (Histogram)

Example `config.yaml`:

```yaml
postfix:
  qmgr:
    entering_queue:
      type: counter
      metric_name: postfix_qmgr_entering_queue
      help: 'Qmgr messages entering queue events'
      regex: '^(?P<id>[A-F0-9]{6,}): from=<(?P<from>[^>]*)>, size=(?P<size>\d+), nrcpt=(?P<nrcpt>\d+)'
    removed:
      type: counter
      metric_name: postfix_qmgr_removed
      help: 'Qmgr messages removed from queue events'
      regex: '^(?P<id>[A-F0-9]{6,}): removed'
```

**Options:**

| Option                  | Description                                         |
| ----------------------- | --------------------------------------------------- |
| `logfile`               | Path to your Postfix mail log file                  |
| `config`                | Path to configuration file                          |
| `test`                  | Parses entire file, then exits                      |
| `log_unsupported_lines` | Outputs lines that was not recognized by any regex  |
| `time-format`           | BSD or ISO based timestamps                         |
| `postqueue`             | Use postqueue for the additional queue metrics      |
| `port`                  | HTTP port to listen on for prom metrics             |

---

## Usage

```bash
# Run the exporter
python postfix_exporter.py --config config.yaml

# By default, the metrics will be exposed at http://localhost:9115/metrics
```

You can configure the port via command-line arguments or the config file.

### Prometheus Scrape Configuration

Add the exporter to your Prometheus `scrape_configs`:

```yaml
scrape_configs:
  - job_name: 'postfix'
    static_configs:
      - targets: ['localhost:9115']
```

---

## Metrics Exposed

Here are some example metrics you can expect:

| Metric                                   | Labels                                 | Description                                                           |
| ---------------------------------------- | -------------------------------------- | --------------------------------------------------------------------- |
| `postfix_queue_length`                   | `queue_name`                          | Number of messages in each postfix queue (active, deferred, hold, incoming, maildrop) |
| `postfix_unsupported_log_entries_total`  | `subprocess`, `level`                 | Total number of unsupported Postfix log entries                       |
| `postfix_message_size_bytes`             |                                        | Size of Postfix log messages in bytes (histogram)                     |
| `postfix_message_nrcpt_total`            |                                        | Number of recipients for Postfix log messages (histogram)             |
| `postfix_log_levels_total`               | `level`, `process`, `subprocess`      | Total number of Postfix log entries by level, process, and subprocess |
| `postfix_qmgr_entering_queue`            |                                        | Qmgr messages entering queue events                                   |
| `postfix_qmgr_removed`                   |                                        | Qmgr messages removed from queue events                               |
| `postfix_qmgr_expired`                   |                                        | Qmgr messages expired events                                          |
| `postfix_cleanup_processes`              |                                        | Total cleanup processes                                               |
| `postfix_smtp_connections`               |                                        | Total SMTP connections                                                |
| `postfix_smtp_disconnections`            |                                        | Total SMTP disconnections                                             |
| `postfix_smtp_lost_connections`          |                                        | Total SMTP lost connections                                           |
| `postfix_smtp_noqueue_reject`            |                                        | Total SMTPD noqueue reject events                                     |
| `postfix_smtp_sasl_failed`               |                                        | Total SMTP SASL authentication failures                               |
| `postfix_smtp_sent`                      |                                        | Total SMTP sent messages                                              |
| `postfix_smtp_deferred`                  |                                        | Total SMTP deferred messages                                          |
| `postfix_smtp_bounced`                   |                                        | Total SMTP bounced messages                                           |
| `postfix_pickup_requests`                |                                        | Total pickup requests                                                 |
| `postfix_relay_smtp_deferred`            |                                        | Total relay SMTP deferred messages                                    |
| `postfix_relay_smtp_connection_timeout`  | `host`, `ip`                          | Total relay SMTP connection timeouts                                  |
| `postfix_local_sent`                     |                                        | Total local sent messages                                             |
| `postfix_virtual_sent`                   |                                        | Total virtual sent messages                                           |
| `postfix_bounce_bounced`                 |                                        | Total bounce bounced messages                                         |
| `postfix_lmtp_sent`                      |                                        | Total LMTP sent messages                                              |
| `postfix_lmtp_deferred`                  |                                        | Total LMTP deferred messages                                          |
| `postfix_lmtp_bounced`                   |                                        | Total LMTP bounced messages                                           |
| `postfix_submission_smtp_connections`    |                                        | Total Submission SMTP connections                                     |
| `postfix_submission_smtp_disconnections` |                                        | Total Submission SMTP disconnections                                  |
| `postfix_submission_smtp_lost_connections`|                                       | Total Submission SMTP lost connections                                |
| `postfix_submission_smtp_authentication` |                                        | Total Submission SMTP successful authentications                      |
| `postfix_submission_smtp_noqueue`        |                                        | Total Submission SMTP noqueue events                                  |
| `postfix_submission_smtp_sasl_failed`    |                                        | Total Submission SMTP SASL authentication failures                    |

You can add more metrics depending on your configuration.

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests to improve functionality, add metrics, or fix bugs.

---

## License

MIT License. See `LICENSE` file for details.

---

## Contact

For questions or support, open an issue on the GitHub repository.


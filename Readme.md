# Postfix Exporter Py

**postfix-exporter-py** is a Prometheus exporter written in Python that reads Postfix mail logs and exposes relevant metrics in a highly configurable and easy-to-use way. This exporter allows you to monitor your Postfix mail server performance, queue statistics, delivery status, and more in real-time via Prometheus.

---

## Features

* Parses Postfix `mail.log` files to extract key metrics.
* Exposes metrics such as:

  * Number of queued messages
  * Deferred, bounced, and rejected messages
  * Delivery delays and status codes
  * Number of recipients per message
  * Milter and SMTP rejects
* Fully configurable log path, metric labels, and update intervals.
* Lightweight Python implementation.
* Easy integration with Prometheus and Grafana.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/postfix-exporter-py.git
cd postfix-exporter-py

# Optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Configuration is provided via a YAML or JSON config file (default: `config.yaml`).

Example `config.yaml`:

```yaml
log_path: /var/log/mail.log
update_interval: 15  # seconds between metrics updates
metrics:
  track_queued: true
  track_rejected: true
  track_deferred: true
  track_bounced: true
  track_delivery_delay: true
labels:
  host: my-mail-server
```

**Options:**

| Option            | Description                                         |
| ----------------- | --------------------------------------------------- |
| `log_path`        | Path to your Postfix mail log file                  |
| `update_interval` | Time in seconds between metric collection           |
| `metrics`         | Boolean flags to enable/disable specific metrics    |
| `labels`          | Optional Prometheus labels to attach to all metrics |

---

## Usage

```bash
# Run the exporter
python postfix_exporter.py --config config.yaml

# By default, the metrics will be exposed at http://localhost:9110/metrics
```

You can configure the port via command-line arguments or the config file.

### Prometheus Scrape Configuration

Add the exporter to your Prometheus `scrape_configs`:

```yaml
scrape_configs:
  - job_name: 'postfix'
    static_configs:
      - targets: ['localhost:9110']
```

---

## Metrics Exposed

Here are some example metrics you can expect:

| Metric                            | Labels       | Description                                                           |
| --------------------------------- | ------------ | --------------------------------------------------------------------- |
| `postfix_queue_total`             | `queue_type` | Number of messages in a specific queue (active, deferred, hold, etc.) |
| `postfix_messages_rejected_total` | `reason`     | Total number of rejected messages with rejection reason               |
| `postfix_messages_bounced_total`  |              | Total number of bounced messages                                      |
| `postfix_messages_deferred_total` |              | Total number of deferred messages                                     |
| `postfix_delivery_delay_seconds`  | `recipient`  | Delivery delay in seconds                                             |
| `postfix_recipients_per_message`  | `queue_id`   | Number of recipients for each queued message                          |

You can add more metrics depending on your configuration.

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests to improve functionality, add metrics, or fix bugs.

---

## License

MIT License. See `LICENSE` file for details.

---

## Contact

For questions or support, contact `yourname@example.com` or open an issue on the GitHub repository.


import os
import subprocess
import re
import pytest

EXPORTER_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/postfix_exporter.py'))
STATIC_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), './testdata/mail_iso.log'))
CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/config.yaml'))

@pytest.fixture(scope="module")
def run_exporter():
    # Run exporter in test mode and capture output
    try:
        result = subprocess.run([
            'python', EXPORTER_SCRIPT,
            '--test',
            '--logfile', STATIC_LOG,
            '--config', CONFIG,
            '--postqueue'
        ], capture_output=True, text=True, check=True)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        print("Return code:", result.returncode)
    except subprocess.CalledProcessError as e:
        print("Subprocess failed!")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise

    return result.stdout

def parse_metrics(output):
    metrics = {}
    for line in output.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            name = parts[0]
            value = parts[1]
            metrics[name] = value
    return metrics

def test_metric_names_and_values(run_exporter):
    metrics = parse_metrics(run_exporter)
    # Dictionary of expected metric names and their expected values (set value to None to only check presence)
    expected_metrics = {
        'postfix_message_size_bytes_count': 2.0,
        'postfix_message_nrcpt_total_count': 2.0,
        'postfix_log_levels_total': 1.0,
        'postfix_qmgr_entering_queue': 2.0,
        'postfix_qmgr_removed': 1.0,
        'postfix_qmgr_expired': 1.0,
        'postfix_cleanup_processes': 1.0,
        'postfix_smtp_connections': 1.0,
        'postfix_smtp_disconnections': 1.0,
        'postfix_smtp_lost_connections': 1.0,
        'postfix_smtp_noqueue_reject': 3.0,
        'postfix_smtp_sasl_failed': 1.0,
        'postfix_smtp_sent': 2.0,
        'postfix_smtp_deferred': 0.0,
        'postfix_smtp_bounced': 1.0,
        'postfix_pickup_requests': 0.0,
        'postfix_local_sent': 0.0,
        'postfix_virtual_sent': 1.0,
        'postfix_bounce_bounced': 0.0,
        'postfix_lmtp_sent': 1.0,
        'postfix_lmtp_deferred': 0.0,
        'postfix_lmtp_bounced': 1.0,
        'postfix_submission_smtp_connections': 1.0,
        'postfix_submission_smtp_disconnections': 1.0,
        'postfix_submission_smtp_lost_connections': 0.0,
        'postfix_submission_smtp_authentication': 1.0,
        'postfix_submission_smtp_noqueue': 0.0,
        'postfix_submission_smtp_sasl_failed': 0.0,
        'postfix_relay_smtp_deferred': 1.0,
        'postfix_relay_smtp_connection_timeout': 1.0,
        'postfix_message_bytes': 2038.0
    }
    for metric, expected_value in expected_metrics.items():
        found = None
        for name in metrics:
            if name.startswith(metric):
                found = name
                break
        assert found, f"Metric {metric} not found in output"
        if expected_value is not None:
            assert metrics[found] == str(expected_value), f"Metric {metric} value {metrics[found]} != expected {expected_value}"

def test_postfix_queue_length_labels(run_exporter):
    metrics = parse_labeled_metrics(run_exporter)
    expected_queues = {
        "active": 2.0,
        "deferred": 2.0,
        "hold": 1.0,
        "incoming": 1.0,
        "maildrop": 0.0,
    }
    found_queues = {q: False for q in expected_queues}
    for metric in metrics:
        if metric['name'] == 'postfix_queue_length' and 'queue_name' in metric['labels']:
            queue = metric['labels']['queue_name']
            if queue in expected_queues:
                assert metric['value'] == expected_queues[queue], f"Value for queue {queue} is {metric['value']}, expected {expected_queues[queue]}"
                found_queues[queue] = True
    for queue, found in found_queues.items():
        assert found, f"Metric for queue_name={queue} not found"

def test_postfix_message_nrcpt_total_bucket_labels(run_exporter):
    metrics = parse_labeled_metrics(run_exporter)
    expected = [
        {"le": "1.0", "value": 1.0},
        {"le": "2.0", "value": 2.0},
        {"le": "3.0", "value": 2.0},
        {"le": "4.0", "value": 2.0},
        {"le": "5.0", "value": 2.0},
        {"le": "6.0", "value": 2.0},
        {"le": "7.0", "value": 2.0},
        {"le": "8.0", "value": 2.0},
        {"le": "9.0", "value": 2.0},
        {"le": "10.0", "value": 2.0},
        {"le": "+Inf", "value": 2.0}
    ]
    for exp in expected:
        found = False
        for metric in metrics:
            if metric['name'] == 'postfix_message_nrcpt_total_bucket':
                labels = metric['labels']
                if labels.get('le') == exp['le']:
                    assert metric['value'] == exp['value'], f"Value for {exp} is {metric['value']}, expected {exp['value']}"
                    found = True
                    break
        assert found, f"Metric with labels {exp} not found"
def test_postfix_message_size_bytes_bucket_labels(run_exporter):
    metrics = parse_labeled_metrics(run_exporter)
    expected = [
        {"le": "0.0", "value": 0.0},
        {"le": "1024.0", "value": 1.0},
        {"le": "5120.0", "value": 2.0},
        {"le": "10240.0", "value": 2.0},
        {"le": "51200.0", "value": 2.0},
        {"le": "102400.0", "value": 2.0},
        {"le": "512000.0", "value": 2.0},
        {"le": "1.048576e+06", "value": 2.0},
        {"le": "5.24288e+06", "value": 2.0},
        {"le": "1.048576e+07", "value": 2.0},
        {"le": "2.097152e+07", "value": 2.0},
        {"le": "3.145728e+07", "value": 2.0},
        {"le": "4.194304e+07", "value": 2.0},
        {"le": "5.24288e+07", "value": 2.0},
        {"le": "1.048576e+08", "value": 2.0},
        {"le": "1.572864e+08", "value": 2.0},
        {"le": "2.097152e+08", "value": 2.0},
        {"le": "+Inf", "value": 2.0}
    ]
    for exp in expected:
        found = False
        for metric in metrics:
            if metric['name'] == 'postfix_message_size_bytes_bucket':
                labels = metric['labels']
                if labels.get('le') == exp['le']:
                    assert metric['value'] == exp['value'], f"Value for {exp} is {metric['value']}, expected {exp['value']}"
                    found = True
                    break
        assert found, f"Metric with labels {exp} not found"
def test_postfix_unsupported_log_entries_total_labels(run_exporter):
    metrics = parse_labeled_metrics(run_exporter)
    expected = [
        {"level": "unknown", "subprocess": "unknown", "value": 14.0},
        {"level": "info", "subprocess": "postfix1[12345]", "value": 1.0},
        {"level": "info", "subprocess": "unknown", "value": 1.0},
        {"level": "info", "subprocess": "postscreen", "value": 25.0},
        {"level": "error", "subprocess": "postscreen", "value": 1.0},
        {"level": "warning", "subprocess": "smtpd", "value": 1.0},
        {"level": "info", "subprocess": "smtpd", "value": 3.0},
        {"level": "info", "subprocess": "lmtp", "value": 1.0},
        {"level": "info", "subprocess": "smtp", "value": 6.0},
        {"level": "info", "subprocess": "cleanup", "value": 2.0},
        {"level": "info", "subprocess": "qmgr", "value": 1.0}
    ]
    for exp in expected:
        found = False
        for metric in metrics:
            if metric['name'] == 'postfix_unsupported_log_entries_total':
                labels = metric['labels']
                if labels.get('level') == exp['level'] and labels.get('subprocess') == exp['subprocess']:
                    assert metric['value'] == exp['value'], f"Value for {exp} is {metric['value']}, expected {exp['value']}"
                    found = True
                    break
        assert found, f"Metric with labels {exp} not found"
def test_postfix_log_levels_total_labels(run_exporter):
    metrics = parse_labeled_metrics(run_exporter)
    expected = [
        {"level": "info", "process": "postfix1[12345]", "subprocess": "", "value": 1.0},
        {"level": "info", "process": "postfix", "subprocess": "unknown", "value": 1.0},
        {"level": "info", "process": "postfix", "subprocess": "postscreen", "value": 25.0},
        {"level": "error", "process": "postfix", "subprocess": "postscreen", "value": 1.0},
        {"level": "warning", "process": "postfix", "subprocess": "smtpd", "value": 2.0},
        {"level": "info", "process": "postfix", "subprocess": "smtpd", "value": 9.0},
        {"level": "info", "process": "postfix", "subprocess": "lmtp", "value": 3.0},
        {"level": "info", "process": "postfix", "subprocess": "smtp", "value": 9.0},
        {"level": "info", "process": "postfix", "subprocess": "cleanup", "value": 3.0},
        {"level": "info", "process": "postfix", "subprocess": "qmgr", "value": 5.0},
        {"level": "info", "process": "postfix", "subprocess": "virtual", "value": 1.0},
        {"level": "info", "process": "postfix", "subprocess": "submission/smtpd", "value": 3.0},
        {"level": "info", "process": "postfix", "subprocess": "relay/smtp", "value": 2.0},
    ]
    for exp in expected:
        found = False
        for metric in metrics:
            if metric['name'] == 'postfix_log_levels_total':
                labels = metric['labels']
                if labels.get('level') == exp['level'] and labels.get('process') == exp['process'] and labels.get('subprocess') == exp['subprocess']:
                    assert metric['value'] == exp['value'], f"Value for {exp} is {metric['value']}, expected {exp['value']}"
                    found = True
                    break
        assert found, f"Metric with labels {exp} not found"
def parse_labeled_metrics(output):
    metrics = []
    metric_re = re.compile(r'^(?P<name>\w+)(\{(?P<labels>[^}]*)\})?\s+(?P<value>.+)$')
    for line in output.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        m = metric_re.match(line)
        if m:
            name = m.group('name')
            labels_str = m.group('labels')
            value = float(m.group('value'))
            labels = {}
            if labels_str:
                for label in labels_str.split(','):
                    k, v = label.split('=')
                    labels[k.strip()] = v.strip('"')
            metrics.append({'name': name, 'labels': labels, 'value': value})
    return metrics
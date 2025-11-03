import yaml
import re
from prometheus_client import Counter, Gauge

class ConfigLoader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.metrics = {}
        self.regexes = {}
        self.labels = {}
        self.config = None
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self._validate_and_create_metrics()

    def _validate_and_create_metrics(self):
        if not self.config:
            raise ValueError('Config file is empty or invalid')
        for process, subprocesses in self.config.items():
            if process not in self.metrics:
                self.metrics[process] = {}
                self.regexes[process] = {}
                self.labels[process] = {}
            for subprocess, metrics in subprocesses.items():
                self.metrics[process][subprocess] = []
                self.regexes[process][subprocess] = []
                self.labels[process][subprocess] = []
                for metric_key, metric in metrics.items():
                    name = metric.get('metric_name')
                    help_text = metric.get('help', '')
                    metric_type = metric.get('type', 'counter').lower()
                    regex = metric.get('regex')
                    labels = metric.get('labels', [])
                    if not (name and regex):
                        raise ValueError(f'Metric definition missing name or regex: {metric}')
                    try:
                        compiled_regex = re.compile(regex)
                    except re.error as e:
                        raise ValueError(f'Invalid regex for metric {name}: {e}')
                    self.regexes[process][subprocess].append(compiled_regex)
                    self.labels[process][subprocess].append(labels)
                    if metric_type == 'counter':
                        self.metrics[process][subprocess].append(Counter(name, help_text, labels))
                    elif metric_type == 'gauge':
                        self.metrics[process][subprocess].append(Gauge(name, help_text, labels))
                    else:
                        raise ValueError(f'Unsupported metric type: {metric_type}')

    def get_metric(self, process, subprocess):
        return self.metrics.get(process, {}).get(subprocess)

    def get_regex(self, process, subprocess):
        return self.regexes.get(process, {}).get(subprocess)

    def get_labels(self, process, subprocess):
        return self.labels.get(process, {}).get(subprocess)

    def get_all_metrics(self):
        return self.metrics

    def get_all_regexes(self):
        return self.regexes

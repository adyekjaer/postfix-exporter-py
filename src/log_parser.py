from prometheus_client import Counter, Histogram
import re
from config_loader import ConfigLoader


class LogParser:


    def __init__(self, time_format, config_loader, log_unsupported_lines=False):
        self.config_loader = config_loader
        self.log_unsupported_lines = log_unsupported_lines
        # Optionally, for convenience, you can keep direct references:
        self.metrics = config_loader.get_all_metrics()
        self.regexes = config_loader.get_all_regexes()
        self.labels = getattr(config_loader, 'labels', {})
        self.time_format = time_format

        qmgr_regex = (
            r'^(?P<id>[A-F0-9]{6,}): from=<(?P<from>[^>]*)>, size=(?P<size>\d+), nrcpt=(?P<nrcpt>\d+)'
        )
        self.qmgr_regex_compiled = re.compile(qmgr_regex)

        # Add hardcoded unsupported log entries metric
        self.unsupportedLogEntries = Counter(
            'postfix_unsupported_log_entries_total',
            'Total number of unsupported Postfix log entries',
            ['subprocess', 'level']
        )

        # Add hardcoded histograms for size and nrcpt metrics
        self.postfix_message_size = Histogram(
            'postfix_message_size_bytes',
            'Size of Postfix log messages in bytes',
            buckets=[
                0,
                5 * 1024,
                1 * 1024 * 1024,
                2 * 1024 * 1024,
                3 * 1024 * 1024,
                4 * 1024 * 1024,
                5 * 1024 * 1024,
                10 * 1024 * 1024,
                50 * 1024 * 1024,
                100 * 1024 * 1024,
                150 * 1024 * 1024,
                200 * 1024 * 1024, float('inf')]
        )
        self.postfix_message_nrcpt = Histogram(
            'postfix_message_nrcpt_total',
            'Number of recipients for Postfix log messages',
            buckets=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, float('inf')]
        )

        # Add hardcoded counters for different levels
        self.postfix_log_levels = Counter(
            'postfix_log_levels_total',
            'Total number of Postfix log entries by level, process, and subprocess',
            ['level', 'process', 'subprocess']
        )

    def add_to_unsupported_line(self, line, subprocess, level):
        if getattr(self, 'log_unsupported_lines', False):
            print(f"Unsupported Line: {line}, Subprocess: {subprocess}, Level: {level}")
        if hasattr(self, 'unsupportedLogEntries'):
            self.unsupportedLogEntries.labels(subprocess, level).inc()

    def add_to_histogram(self, histogram, value, field_name):
        try:
            float_value = float(value)
            histogram.observe(float_value)
        except Exception as err:
            print(f"Couldn't convert value '{value}' for {field_name}: {err}")

    def add_to_histogram_by_label(self, histogram, value, field_name, *labels):
        try:
            float_value = float(value)
            histogram.labels(*labels).observe(float_value)
        except Exception as err:
            print(f"Couldn't convert value '{value}' for {field_name}: {err}")

    def parse_line(self, line):
        """
        Parse a postfix log line into columns: date_time, hostname, process/subprocess, message.
        Returns a dict or None if not matched.
        """
        # BSD syslog: Jan 1 00:00:00 hostname postfix/postscreen[12345]: message
        # ISO8601/RFC3339: 2025-10-31T11:54:03.121850+00:00 hostname postfix/cleanup[34481]: message
        bsd_regex = r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+([^:]+):\s*(.*)$'
        # ISO8601: allow Z, +00, +0000, +00:00, etc. and relax process part
        iso_regex = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}(?::?\d{2})?)?)\s+(\S+)\s+([^:]+):\s*(.*)$'


        if self.time_format == 'bsd':
            line_regex = bsd_regex
        elif self.time_format == 'iso8601':
            line_regex = iso_regex

        m = re.match(line_regex, line)
        if m:
            date_time, hostname, process, message = m.groups()
            # Split process/subprocess
            if '/' in process:
                proc, subproc = process.split('/', 1)
                # Remove PID in brackets from subprocess, e.g. 'virtual[34482]' -> 'virtual'
                if subproc and '[' in subproc:
                    subproc = subproc.split('[', 1)[0]
            else:
                proc, subproc = process, None
            return {
                'date_time': date_time,
                'hostname': hostname,
                'process': proc,
                'subprocess': subproc,
                'message': message
            }
        return None

    def parse(self, line):
        if not (line_details := self.parse_line(line)):
            self.add_to_unsupported_line(line, "unknown", "unknown")
            return

        process = line_details['process']
        subprocess = line_details['subprocess']
        message = line_details['message']

        # Extract severity/level from message if present (e.g., 'warning:', 'error:', etc.)
        level_match = re.match(r'^(warning|error|fatal|panic): ', message)
        level = level_match.group(1) if level_match else "info"

        # Increment log level counter
        self.postfix_log_levels.labels(level, process, subprocess or '').inc()

        # Increment histograms for message length and size
        if process == 'postfix' and subprocess == 'qmgr':
            m = self.qmgr_regex_compiled.match(message)
            if m:
                size = m.group('size')
                nrcpt = m.group('nrcpt')
                if size:
                    self.postfix_message_size.observe(float(size))
                if nrcpt:
                    self.postfix_message_nrcpt.observe(int(nrcpt))

        # Try all regexes/metrics for this process/subprocess
        regex_list = self.regexes.get(process, {}).get(subprocess, [])
        metric_list = self.metrics.get(process, {}).get(subprocess, [])
        matched = False
        for regex, metric in zip(regex_list, metric_list):
            if regex and metric:
                m = regex.match(message)
                if m:
                    metric.inc()
                    matched = True
                    break
        if not matched:
            self.add_to_unsupported_line(line, subprocess or process, level)


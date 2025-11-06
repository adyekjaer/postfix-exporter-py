from postqueue_reader import PostqueueReader
from prometheus_client.core import GaugeMetricFamily
from prometheus_client import REGISTRY
from prometheus_client import start_http_server, generate_latest
from log_parser import LogParser
from file_tailer import FileTailer
from config_loader import ConfigLoader
import os
import argparse

CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), './', 'config.yaml'))

class QueueCollector:
    def __init__(self, postqueue_reader):
        self.postqueue_reader = postqueue_reader

    def collect(self):
        # Postqueue -j metric on each collection
        known_queues = ['active', 'deferred', 'hold', 'incoming', 'maildrop']
        queue_counts = {}
        try:
            queue_counts = self.postqueue_reader.get_queue_length_by_name()
        except Exception:
            # If we can't read data, default to zero for all
            queue_counts = {}
        metric = GaugeMetricFamily(
            'postfix_queue_length',
            'Number of messages in each postfix queue',
            labels=['queue_name']
        )
        for queue_name in known_queues:
            count = queue_counts.get(queue_name, 0)
            metric.add_metric([queue_name], count)
        yield metric

def main():

    parser = argparse.ArgumentParser(description='Postfix Prometheus Exporter')
    parser.add_argument('--logfile', required=True, help='Path to postfix log file')
    parser.add_argument('--config', required=False, help='Path to config file', default=CONFIG)
    parser.add_argument('--port', type=int, default=9115, help='Port to expose metrics')
    parser.add_argument('--test', required=False, action='store_true', help='Run in test mode')
    parser.add_argument('--log-unsupported', required=False, action='store_true', help='Log unsupported lines to console')
    parser.add_argument('--time-format', choices=['bsd', 'iso8601'], default='iso8601', help='Time format in logs (bsd or iso8601)')
    parser.add_argument('--postqueue', required=False, action='store_true', help='Get queue metrics using postqueue -j')
    args = parser.parse_args()

    config_loader = ConfigLoader(args.config)
    log_parser = LogParser(args.time_format, config_loader)
    log_parser.log_unsupported_lines = args.log_unsupported

    if args.postqueue:
        postqueue_reader = PostqueueReader(test_mode=args.test)

    if args.test:
        # Test mode: read and parse the full file, then exit
        with open(args.logfile, 'r') as f:
            for line in f:
                log_parser.parse(line)

        if args.postqueue:
            # Run the postqueue reader once (registers metric for output)
            REGISTRY.register(QueueCollector(postqueue_reader))
        print(generate_latest().decode('utf-8'))
        return


    file_tailer = FileTailer(args.logfile, log_parser)

    if args.postqueue:
        REGISTRY.register(QueueCollector(postqueue_reader))

    start_http_server(args.port)
    print(f"Serving metrics on port {args.port}")
    file_tailer.tail()

if __name__ == '__main__':
    main()

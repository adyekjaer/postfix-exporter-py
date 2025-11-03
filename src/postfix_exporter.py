import argparse
from prometheus_client import start_http_server, generate_latest
from log_parser import LogParser
from file_tailer import FileTailer
from config_loader import ConfigLoader

def main():
    parser = argparse.ArgumentParser(description='Postfix Prometheus Exporter')
    parser.add_argument('--logfile', required=True, help='Path to postfix log file')
    parser.add_argument('--config', required=False, help='Path to config file', default='./config.yaml')
    parser.add_argument('--port', type=int, default=9115, help='Port to expose metrics')
    parser.add_argument('--test', required=False, action='store_true', help='Run in test mode')
    parser.add_argument('--log_unsupported_lines', required=False, action='store_true', help='Log unsupported lines to console')
    parser.add_argument('--time-format', choices=['bsd', 'iso8601'], default='iso8601', help='Time format in logs (bsd or iso8601)')
    args = parser.parse_args()

    config_loader = ConfigLoader(args.config)
    log_parser = LogParser(args.time_format, config_loader)
    log_parser.log_unsupported_lines = args.log_unsupported_lines

    if args.test:
        # Test mode: read and parse the full file, then exit
        with open(args.logfile, 'r') as f:
            for line in f:
                log_parser.parse(line)
        print("Test mode: finished parsing file.")
        print("\nPrometheus metrics output:\n")
        print(generate_latest().decode('utf-8'))
        return

    file_tailer = FileTailer(args.logfile, log_parser)
    start_http_server(args.port)
    print(f"Serving metrics on port {args.port}")
    file_tailer.tail()

if __name__ == '__main__':
    main()

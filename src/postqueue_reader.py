import os
import subprocess
import json

class PostqueueReader:
    def __init__(self, postqueue_cmd='/usr/sbin/postqueue -j', test_mode=False):
        self.postqueue_cmd = postqueue_cmd
        self.test_mode = test_mode
        self.test_file_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'testdata', 'queue.json')


    def read_queue(self):
        lines = []
        if self.test_mode:
            try:
                with open(self.test_file_path, 'r') as f:
                    lines = f.readlines()
            except Exception as e:
                raise RuntimeError(f"Failed to read test queue file: {e}")
        else:
            try:
                result = subprocess.run(self.postqueue_cmd.split(), capture_output=True, check=True, text=True)
                lines = result.stdout.splitlines()
            except Exception as e:
                raise RuntimeError(f"Failed to run postqueue -j: {e}")
        # Parse each line as a JSON object
        queue_entries = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                queue_entries.append(json.loads(line))
            except Exception as e:
                # Optionally log or handle parse errors
                continue
        return queue_entries

    def get_queue_length_by_name(self):
        """
        Returns a dict: {queue_name: count}
        """
        queue_entries = self.read_queue()
        counts = {}
        for entry in queue_entries:
            qn = entry.get('queue_name', 'unknown')
            counts[qn] = counts.get(qn, 0) + 1
        return counts

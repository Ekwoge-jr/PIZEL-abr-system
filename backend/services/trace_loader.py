## used to load the network trace dataset from the data folder into the rl model


from pathlib import Path
import random



class TraceLoader:
    # Accept a specific folder name (e.g., "train_traces" or "test_traces")
    def __init__(self, trace_folder: str = "train_traces"):
        self.trace_dir = (
            Path(__file__).parent.parent.parent /
            "data" /
            trace_folder
        )
        self.traces = []
        self.load_traces()

    def load_traces(self):
        # Keeps your original loading logic intact...
        for file in self.trace_dir.iterdir():
            if file.is_file():
                trace = []
                with open(file, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) < 2:
                            continue
                        timestamp = float(parts[0])
                        throughput = float(parts[1])
                        trace.append((timestamp, throughput))
                if trace:
                    self.traces.append(trace)

    def get_random_trace(self):
        return random.choice(self.traces)




"""
class TraceLoader:

    def __init__(self):

        self.trace_dir = (
            Path(__file__).parent.parent.parent /
            "data" /
            "cooked_traces"
        )

        self.traces = []

        self.load_traces()


    def load_traces(self):

        for file in self.trace_dir.iterdir():

            if file.is_file():

                trace = []

                with open(file, "r") as f:

                    for line in f:

                        parts = line.strip().split()

                        if len(parts) < 2:
                            continue

                        timestamp = float(parts[0])

                        throughput = float(parts[1])

                        trace.append(

                            (
                                timestamp,
                                throughput
                            )

                        )

                if trace:
                    self.traces.append(trace)


    def get_random_trace(self):

        return random.choice(self.traces)
"""
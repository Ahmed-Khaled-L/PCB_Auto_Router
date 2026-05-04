import time
import os

class MetricsLogger:
    def __init__(self, log_file="routing_metrics.log"):
        self.log_file = log_file
        self.start_time = 0
        
        # Create the file and write the CSV header if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("Algorithm,Grid_Size,Path_Length,Visited_Nodes,Execution_Time_ms\n")

    def start_timer(self):
        """Starts the high-resolution performance counter."""
        self.start_time = time.perf_counter()

    def stop_timer(self):
        """Returns elapsed time in milliseconds."""
        end_time = time.perf_counter()
        return (end_time - self.start_time) * 1000 

    def log_metrics(self, algorithm_name, grid, net, total_time_ms):
        """Extracts grid data and appends it to the log file."""
        path_length = len(net.path) if net.path else 0
        
        # Count exactly how many nodes were explored
        visited_count = sum(
            1 for x in range(grid.width) for y in range(grid.height)
            if grid.get_node(x, y).visited
        )

        # Format as CSV: Algorithm, Grid_Size, Path_Length, Visited, Time
        log_entry = f"{algorithm_name},{grid.width}x{grid.height},{path_length},{visited_count},{total_time_ms:.4f}\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry)
            
        print(f"[METRICS] Logged -> {algorithm_name} | Visited: {visited_count} | Time: {total_time_ms:.4f} ms")
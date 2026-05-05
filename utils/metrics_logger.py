import time
import os

class MetricsLogger:
    def __init__(self, log_file="routing_metrics.log"):
        self.log_file = log_file
        self.start_time = 0
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("Algorithm,Grid_Size,Net_ID,Path_Length,Visited_Nodes,Execution_Time_ms\n")

    def start_timer(self):
        """Starts the high-resolution performance counter."""
        self.start_time = time.perf_counter()

    def stop_timer(self):
        """Returns elapsed time in milliseconds."""
        end_time = time.perf_counter()
        return (end_time - self.start_time) * 1000 

    def log_net_metrics(self, algorithm_name, grid, net, net_id, total_time_ms):
        """Instantly logs metrics for a specific net without scanning the grid."""
        path_length = len(net.path) if net.path else 0
        
        # O(1) Lookup: No more scanning the grid!
        visited_count = len(net.search_history)
        
        log_entry = f"{algorithm_name},{grid.width}x{grid.height},{net_id},{path_length},{visited_count},{total_time_ms:.4f}\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry)
            
        print(f"[METRICS] Logged -> Net {net_id} | Alg: {algorithm_name} | Visited: {visited_count} | Time: {total_time_ms:.4f} ms")
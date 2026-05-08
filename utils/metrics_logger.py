import time
import os
import datetime

class MetricsLogger:
    def __init__(self, log_file="routing_metrics.csv", summary_file="run_summary.csv"):
        self.log_file = log_file
        self.summary_file = summary_file
        self.start_time = 0
        
        # Net-by-Net Log
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("Algorithm,Grid_Size,Net_ID,Path_Length,Visited_Nodes,Execution_Time_ms\n")
                
        # Global Run Summary Log
        if not os.path.exists(self.summary_file):
            with open(self.summary_file, "w") as f:
                f.write("Timestamp,Benchmark,Grid_Size,Router,Optimizer,Total_Nets,Routed,Failed,Total_Wirelength,Total_Time_ms\n")
    def start_timer(self):
        """Starts the high-resolution performance counter."""
        self.start_time = time.perf_counter()

    def stop_timer(self):
        """Returns elapsed time in milliseconds."""
        end_time = time.perf_counter()
        return (end_time - self.start_time) * 1000

    def log_net_metrics(self, algorithm_name, grid, net, net_id, total_time_ms):
        """Logs metrics for a specific net."""
        path_length = len(net.path) if net.path else 0
        visited_count = len(net.search_history)
        
        log_entry = f"{algorithm_name},{grid.width}x{grid.height},{net_id},{path_length},{visited_count},{total_time_ms:.4f}\n"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def log_run_summary(self, benchmark_name, grid, router_name, optimizer_name, total_nets, routed, failed, total_length, total_time_ms):       
        """Logs global metrics for the entire optimization and routing run."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"{timestamp},{benchmark_name},{grid.width}x{grid.height},{router_name},{optimizer_name},{total_nets},{routed},{failed},{total_length},{total_time_ms:.4f}\n"        
        with open(self.summary_file, "a") as f:
            f.write(log_entry)
            
        # Print a beautiful summary to the terminal
        print("\n" + "="*50)
        print("📈 ROUTING RUN SUMMARY")
        print("="*50)
        print(f"Benchmark: {benchmark_name}")   # <-- NEW LINE
        print(f"Router:    {router_name}")
        print(f"Optimizer: {optimizer_name}")
        print(f"Board:     {grid.width}x{grid.height} cells")
        print(f"Nets:      {routed}/{total_nets} Successfully Routed ({failed} Deadlocks)")
        print(f"Length:    {total_length} Total Grid Units (Copper Wirelength)")
        print(f"Time:      {total_time_ms:.2f} ms (Including Optimization)")
        print("="*50 + "\n")
# core/multi_net_manager.py
class MultiNetManager:
    def __init__(self, nets, optimizer=None):
        self.nets = nets
        self.optimizer = optimizer
        self.current_index = 0

    def prepare_queue(self):
        """Delegates the heavy lifting to the injected strategy."""
        if self.optimizer:
            self.nets = self.optimizer.optimize(self.nets)
        else:
            print("[MANAGER] No optimizer provided. Nets will route in default order.")

from .src.worker_service import SimpleWorker


def start_worker():
    worker = SimpleWorker()
    worker.start()
    return worker


if __name__ == "__main__":
    worker = start_worker()
    
    try:
        import signal
        import sys
        
        def signal_handler(sig, frame):
            print(f"Received signal {sig}, shutting down...")
            worker.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        while True:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down worker...")
        worker.stop()
# Group #:B49
# Student names: Sarthak Tyagi, Juelin Zhou
 
import threading
import queue
import time, random

# constants 
NUM_PRODUCERS = 4           
NUM_CONSUMERS = 5           
ITEMS_PER_PRODUCER = 5      # each producer makes this many items (20 total)
SENTINEL = None             # special value to signal consumers to stop

def consumerWorker(buffer: queue.Queue) -> None:
    """
    Target worker for a consumer thread.
    Continuously retrieves items from the buffer and processes them.
    When a sentinel (None) is recieved, the consumer knows its time to stop.
    """
    while True:
        item = buffer.get()  # blocks until an item is availble
        
        if item is SENTINEL:
            # sentinel recieved, time to exit!
            print(f"{threading.current_thread().name} recieved sentinel, exiting.")
            buffer.task_done()
            break
        
        # simulate some processing time with random delay
        time.sleep(random.uniform(0.1, 0.3))
        print(f"{threading.current_thread().name} consumed: {item}")
        buffer.task_done()
  
def producerWorker(buffer: queue.Queue) -> None:
    """
    Target worker for a producer thread.
    Produces ITEMS_PER_PRODUCER items and adds them to the buffer.
    Each item is a string with the producer name and item number for easy tracking.
    """
    for i in range(ITEMS_PER_PRODUCER):
        # simulate some production time with random delay
        time.sleep(random.uniform(0.1, 0.3))
        
        #create an item using thread name and item number for clarity!
        item = f"{threading.current_thread().name}_item{i}"
        buffer.put(item)
        print(f"{threading.current_thread().name} produced: {item}")
    
    print(f"{threading.current_thread().name} finished producing!")

if __name__ == "__main__":
    buffer = queue.Queue()  # thread safe FIFO queue used as our buffer
    
    # create and start producer threads
    producers = []
    for i in range(NUM_PRODUCERS):
        t = threading.Thread(
            target=producerWorker, 
            args=(buffer,), 
            name=f"Producer-{i}"
        )
        producers.append(t)
        t.start()
    
    # create and start consumer threads
    # using daemon=True as a safety net so program wont hang if something goes wrong
    # however we still use sentinels for graceful termination!
    consumers = []
    for i in range(NUM_CONSUMERS):
        t = threading.Thread(
            target=consumerWorker, 
            args=(buffer,), 
            name=f"Consumer-{i}", 
            daemon=True
        )
        consumers.append(t)
        t.start()
    
    # wait for producers to finish
    for p in producers:
        p.join()
    print("\nAll producers finished!\n")
    
    # send sentinels to stop consumers
    # one sentinel per consumer thread so each one knows to exit
    for _ in range(NUM_CONSUMERS):
        buffer.put(SENTINEL)
    
    # wait for all items to be processed
    buffer.join()
    print("\nAll items consumed! Program ending gracefully.")
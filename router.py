from modules.rip_router import RIPRouter, RouterScheduler
from modules.rip_config import get_router_id, get_router_inputs, get_router_outputs

def main():
    router = RIPRouter(get_router_id(), get_router_inputs(), get_router_outputs())

    # Override default timeouts for more efficient testing
    router.routing_table.timeout = 18
    router.routing_table.gc_time = 6

    router_scheduler = RouterScheduler(update_freq=5, print_freq=2)

    while True:
        router_scheduler.scheduler_task(router)

if __name__ == "__main__":
    try:
        main()
    except(KeyboardInterrupt):
        print("\nExiting Gracefully")
        exit()
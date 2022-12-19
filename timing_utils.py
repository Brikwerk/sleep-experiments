import time
import math


def clock_perf_counter():
    return time.perf_counter() * 1e9


def clock_perf_counter_ns():
    return time.perf_counter_ns()


def period_sleepspin(clock, prev_time, frequency, scale=1):
    sleep_estimate_ns = 5e6
    mean = 5e6
    m2 = 0
    count = 1
    duration_ns = 1e9 / frequency # Frequency time duration in ns

    # Take into account any time that has passed since the start
    # of the last loop iteration. Ex: things done inside the loop.
    duration_ns = duration_ns - (clock() - prev_time)

    # Attempt to sleep until we estimate that the
    # sleep function will overshoot the remaining time.
    while duration_ns > sleep_estimate_ns:
        t1 = clock()
        time.sleep(1e-3) # Sleep for a millisecond
        t2 = clock()

        # Get how long the sleep took in ns
        observed_ns = t2 - t1
        duration_ns = duration_ns - observed_ns

        # Update the sleep estimate using Welford's algorithm
        # and the newly observed sleep time
        count += 1
        delta = observed_ns - mean
        mean += delta / count
        m2 += delta * (observed_ns - mean)
        stddev = math.sqrt(m2 / (count - 1))
        sleep_estimate_ns = mean + scale * stddev
    
    # Spin lock until we burn the remaining time
    t1 = clock()
    while clock() - t1 < duration_ns:
        pass


def period_spinlock(clock, prev_time, frequency):
    # Thrash until time is up
    while True:
        elapsed = clock() - prev_time
        delay = (1e9 / frequency) - elapsed
        if delay < 0:
            break


def period_sleep(clock, prev_time, frequency):
    frame_time = clock()
    elapsed = frame_time - prev_time
    # Get how long we need to sleep in nanoseconds
    delay = (1e9 / frequency) - elapsed
    if delay > 0:
        # Convert delay back to seconds and sleep
        time.sleep(delay / 1e9)


def loop(period_func, clock, num_periods, frequency):
    prev_time = clock()
    periods = []
    for i in range(num_periods):
        # Wait until we need to loop (according to the frequency)
        period_func(clock, prev_time, frequency)

        # Get difference from prev loop in milliseconds
        # record as the past period
        current_time = clock()
        periods.append((current_time - prev_time) / 1e6)

        prev_time = current_time
    
    return periods
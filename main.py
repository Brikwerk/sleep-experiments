import time
import csv
from sys import platform

from matplotlib import pyplot as plt
import numpy as np

from timing_utils import *
from stress import StressTest


if __name__ == "__main__":
    num_periods = 5000
    frequencies = [132, 60]
    stest = StressTest()

    period_funcs = [
        (period_sleepspin, "Sleep Spin"),
        (period_spinlock, "Spin Lock"),
        (period_sleep, "Sleep"),
    ]
    clocks = [
        (clock_perf_counter, "Perf Counter"),
        (clock_perf_counter_ns, "Perf Counter NS")
    ]

    for stress in [False, True]:
        print(f"::: Stress: {stress} :::")

        if stress:
            stest.start() # Start a stress test
            print("Starting Stress Test...")
            time.sleep(5) # Kill some time to let the test start
        for frequency in frequencies:
            print(f"=== Frequency: {frequency}Hz ===")

            # Loop and record results
            loop_periods = []
            loop_labels = []
            loop_labels = []
            abs_errors = []
            stats_upper_bound = ((1 / frequency) * 1.2) * 1e3
            stats = [["Clock/Period Name", "Min (ms)", "Max (ms)", "Mean (ms)", "Std. (ms)",
                    f"Periods > {stats_upper_bound:.2f}ms", "CPU Usage"]]
            for clock, clock_name in clocks:
                for period_func, period_func_name in period_funcs:
                    print(f"--- Clock: {clock_name} | Period Function: {period_func_name} ---")
                    cpu_time = time.process_time_ns()
                    total_time = clock()
                    periods = loop(period_func, clock,
                                num_periods, frequency)
                    total_time = clock() - total_time
                    cpu_time = time.process_time_ns() - cpu_time
                    print(f"Min: {min(periods)} | Max: {max(periods)} | Avg: {np.mean(periods)}")
                    print("---")

                    # Create a name for the loop run
                    if "NS" in clock_name:
                        name = f"NS {period_func_name}"
                    else:
                        name = f"{period_func_name}"

                    # Save periods for later inspection/plotting
                    loop_periods.append(periods)
                    loop_labels.append(name)

                    # Generate stats
                    curr_stats = []
                    curr_stats.append(name)
                    curr_stats.append(min(periods))
                    curr_stats.append(max(periods))
                    curr_stats.append(np.mean(periods))
                    curr_stats.append(round(np.std(periods), 7))
                    curr_stats.append(np.sum(np.array(periods) > stats_upper_bound))
                    curr_stats.append(f"{(cpu_time / total_time) * 100}%")
                    stats.append(curr_stats)

                    # Absolute Error
                    abs_error = np.array(periods) - (1/frequency) * 1e3
                    abs_error = np.mean(np.abs(abs_error))
                    abs_errors.append(abs_error)

            # Create x/y plot x-axis elements
            x = list(range(len(loop_periods[0])))

            # x/y plot for sleep-based periods
            fig, ax = plt.subplots(1,1, figsize=(12,4))
            ax.set_title("Sleep Periods")
            ax.set_ylabel("Milliseconds")
            ax.set_xlabel("Periods")
            ax.plot(x, loop_periods[2])
            ax.plot(x, loop_periods[5])
            ax.legend([
                    loop_labels[2],
                    loop_labels[5]])
            plt.tight_layout()
            plt.savefig(f"{platform}_{frequency}Hz_stress{stress}_sleep_xy_plot.png")

            fig, ax = plt.subplots(2,1, figsize=(12,8))
            # Second-based x/y plots for periods
            ax[0].set_title("Second-based Periods")
            ax[0].set_ylabel("Milliseconds")
            ax[0].set_xlabel("Periods")
            for i in range(0,2):
                ax[0].plot(x, loop_periods[i])
            ax[0].legend(loop_labels[:3])
            # Nanosecond-based x/y plots for periods
            ax[1].set_title("Nanosecond-based Periods")
            ax[1].set_ylabel("Milliseconds")
            ax[1].set_xlabel("Periods")
            for i in range(3,5):
                ax[1].plot(x, loop_periods[i])
            ax[1].legend(loop_labels[3:])
            plt.tight_layout()
            plt.savefig(f"{platform}_{frequency}Hz_stress{stress}_spin_xy_plot.png")
            
            # Create a copy of the periods without the sleep periods
            spin_periods = loop_periods.copy()
            spin_periods.pop(2), spin_periods.pop(4)
            spin_period_labels = loop_labels.copy()
            spin_period_labels.pop(2), spin_period_labels.pop(4)
            # Create a copy of the periods with just the sleep periods
            sleep_periods = [loop_periods[2], loop_periods[5]]
            sleep_period_labels = [loop_labels[2], loop_labels[5]]

            fig, ax = plt.subplots(1,3, figsize=(12,5))
            # Absolute Error Boxplots
            ax[0].set_title("Period Mean Absolute Error")
            ax[0].set_yscale("log")
            ax[0].bar(loop_labels, abs_errors)
            ax[0].xaxis.set_ticks(loop_labels)
            ax[0].set_xticklabels(loop_labels, rotation=45, ha='right')
            # Sleep Spin Vs. Spin Lock
            ax[1].set_title("Sleep Spin & Spin Lock Boxplots")
            ax[1].set_ylabel("Milliseconds")
            ax[1].boxplot(spin_periods, showfliers=False)
            ax[1].set_xticklabels(spin_period_labels, rotation=45, ha='right')
            # Seconds Sleep Vs. NSeconds Sleep
            ax[2].set_title("Second and Nanosecond Sleep Boxplots")
            ax[2].set_ylabel("Milliseconds")
            ax[2].boxplot(sleep_periods, showfliers=False)
            ax[2].set_xticklabels(sleep_period_labels, rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f"{platform}_{frequency}Hz_stress{stress}_bar_and_boxplots.png")

            # Save stats to a CSV
            with open(f"{platform}_{frequency}Hz_stress{stress}_stats.csv","w") as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerows(stats)
        
        if stress:
            stest.stop()

from collections import defaultdict
from functools import partial
from scipy import stats
from sys import stdout
from time import time
import logging
import matplotlib; matplotlib.use('TkAgg')  # osx pipenv requirement
import matplotlib.pyplot as plt
import random
import config
import log
import data_gen

ONE_MILLION = 1e6

SMALL_ARRAY_TOLERANCE = 10

LOG = logging.getLogger('GALAXY')


def complexity_n(counts, data, verbose=False):
    """
    Count unique elements of data with complexity N.

    :param counts: Caller must allocate counts dictionary
    :param data: Sorted list of data
    :param verbose: Debugging flag to print out results
    :return: The number of operations done to populate counts dictionary

    """
    for x in data:
        counts[x] += 1

    if verbose:
        LOG.info('Element\tCount')
        keys = list(counts.keys())
        keys.sort()
        for element, count in counts.items():
            LOG.info(f'{element}\t{count}')

    return len(data)


def complexity_better_than_n(counts, data):
    """
    Count unique elements of data with complexity better-than-N.

    :param counts: Caller must allocate counts dictionary
    :param data: Sorted list of data
    :return: The number of operations done to populate counts dictionary

    """

    jump = 1

    idx_start = 0
    idx_left = idx_start
    idx_test = idx_left + jump
    idx_right = idx_test

    LOG.debug('Initial: %s, start %i, left %i, test %i, right %i',
              data[idx_start], idx_start, idx_left, idx_test, idx_right)

    iterations = 0
    seen_tests = set()
    while idx_test < len(data):
        assert(idx_start <= idx_left <= idx_test <= idx_right)

        if idx_test in seen_tests:
            raise Exception(f'Efficiency: Algorithm testing index {idx_test} '
                            f'more than once for value {data[idx_left]}')
        seen_tests.add(idx_test)

        iterations += 1
        if iterations >= len(data) + SMALL_ARRAY_TOLERANCE:
            raise Exception(f'Fail fast: Algorithm should complete in less '
                            f'than {iterations} iterations for data length {len(data)}')

        if data[idx_start] == data[idx_test] and \
                (idx_test == len(data)-1 or
                 data[idx_test] != data[idx_test+1]):

            counts[data[idx_left]] = idx_test - idx_start + 1
            LOG.debug('Found end-point: %s, count %i ',
                      data[idx_left], counts[data[idx_left]])

            jump = 1
            idx_start = idx_test + 1
            idx_left = idx_start
            idx_test = idx_left + jump
            idx_right = idx_test
            seen_tests.clear()

        elif data[idx_start] == data[idx_test]:
            still_moving_right = idx_test == idx_right
            if still_moving_right:
                # Try to jump twice as far forward as last time
                idx_left = idx_test
                jump *= 2
                if idx_test + jump >= len(data):
                    # Over the end of the array
                    idx_test = len(data)-1
                    idx_right = idx_test
                    jump = idx_test - idx_left
                    LOG.debug('1-Forwards end-of-array %s, start % i, left % i, test % i, delta %i, right %i',
                              data[idx_start], idx_start, idx_left, idx_test, jump, idx_right)
                else:
                    # Move 2x forward
                    idx_test += jump
                    idx_right = idx_test
                    LOG.debug('2-Forwards: %s, start %i, left %i, test %i, delta %i, right %i',
                              data[idx_start], idx_start, idx_left, idx_test, jump, idx_right)
            else:
                # Gone too far back, jump forwards half way between test and right
                idx_left = idx_test
                jump = max(1, (idx_right - idx_test) // 2)
                assert(idx_right - idx_test >= 0)
                assert(idx_test + jump <= len(data)-1)
                idx_test += jump
                LOG.debug('3-Forwards: %s, start %i, left %i, test %i, delta %i, right %i',
                          data[idx_start], idx_start, idx_left, idx_test, jump, idx_right)
        else:
            # Hit next group
            jump = max(1, (idx_test - idx_left) // 2)
            assert(idx_test - idx_left >= 0)
            idx_right = idx_test
            idx_test -= jump
            LOG.debug('4-Backwards: %s, start %i, left %i, test %i, delta %i, right %i',
                      data[idx_start], idx_start, idx_left, idx_test, jump, idx_right)

    if idx_test < len(data) or idx_left == len(data)-1:
        counts[data[idx_start]] = len(data) - idx_start
        LOG.debug('Found end-point: %s, count %i', data[idx_start], counts[data[idx_start]])

    LOG.debug('Total iterations: %i', iterations)
    LOG.debug('Data length: %i', len(data))
    return iterations


def _run_complexity_func(complexity_func, gen_data, n_samples, n_repeats):
    t0 = time()
    data = gen_data(n_samples)
    data.sort()
    counts = defaultdict(int)
    t1 = time()
    for _ in range(n_repeats):
        counts.clear()
        complexity_func(counts, data)
    t2 = time()
    total_in_dict = sum([count for count in counts.values()])
    assert(total_in_dict == n_samples)
    setup_time = t1 - t0
    total_seconds = t2 - t1
    average_seconds = total_seconds / n_repeats
    return setup_time, average_seconds


def _plot_complexity(title, runner, generate_data):
    num_samples = 10000
    max_samples = 1e7
    num_repeats = 3
    ys = []
    xs = []
    LOG.info('*' * 80)
    LOG.info('---- %s ----' % title)
    LOG.info('Elements (m)\tRepeats\tSetup (sec)\tAverage (sec)\tTotal (sec)')
    while num_samples <= max_samples:
        stdout.flush()
        t0 = time()
        setup, avg = runner(generate_data, num_samples, num_repeats)
        t1 = time()
        LOG.info('%.2f\t\t%i\t%.4f\t\t%.4f\t\t\t%.4f' % (num_samples / ONE_MILLION, num_repeats, setup, avg, t1 - t0))
        xs.append(num_samples)
        ys.append(avg)
        num_samples *= 10
    xs_millions = [x/ONE_MILLION for x in xs]
    slope, intercept, r_value, p_value, std_err = stats.linregress(xs_millions, ys)
    LOG.info('Comparison of "Elements (m)" versus "Average (sec)":')
    LOG.info('\t%s Equation:' % title)
    LOG.info('\t\ttime = %.3f x elements_millions + %.3f' % (slope, intercept))
    LOG.info('\t\tp_value: %.3f' % p_value)
    LOG.info('\t\tLinear? %s' % (p_value < 0.05))
    LOG.info('*' * 80)
    plt.plot(xs_millions, ys)
    plt.xlabel('Number of Elements (millions)')
    plt.ylabel('Seconds')
    plt.title('Time to Count Elements - %s' % title)
    plt.show()


def _plot_complexity_n(generate_data):
    run_complexity_n = partial(_run_complexity_func, complexity_n)
    _plot_complexity('O(n)', run_complexity_n, generate_data)


def _plot_complexity_better_than_n(generate_data):
    run_complexity_better_than_n = partial(_run_complexity_func, complexity_better_than_n)
    _plot_complexity('Sub O(n)', run_complexity_better_than_n, generate_data)


def _verify_exact_same_results():
    n_checks = 1000
    for _ in range(n_checks):
        data = data_gen.generate_uniform_alpha(random.randint(5, 1000))
        data.sort()
        counts1 = defaultdict(int)
        counts2 = defaultdict(int)
        complexity_n(counts1, data)
        complexity_better_than_n(counts2, data)
        for key, value in counts1.items():
            if counts2[key] != value:
                raise Exception('Counts wrong for %s: Expected %i, Got %i' %
                                (key, value, counts2[key]))
    LOG.info('Both implementations result in the exact same counts')


if __name__ == '__main__':
    args = config.parse_args()
    log.setup_logger(args.log_level)
    random.seed(1)
    _verify_exact_same_results()
    generate_data_func = data_gen.get_distribution_generator('normal')
    _plot_complexity_n(generate_data_func)
    _plot_complexity_better_than_n(generate_data_func)

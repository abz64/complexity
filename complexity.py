"""
This module analyzes the better-than-n complexity implementation by fitting a function
to a set of random samples.
"""
from scipy.optimize import curve_fit
import numpy as np
from sys import stdout
import random
import data_gen
import config
import log
import matplotlib.pyplot as plt
from collections import defaultdict
import algos
import logging

LOG = logging.getLogger('COMPLEXITY')


def log_complexity(x, p1, p2):
    return p1 * np.log(x) + p2


def estimate_complexity_better_than_n():
    xs = []
    ys = []
    for _ in range(100):
        print('.', end='')
        stdout.flush()
        n_elements = random.randint(50, 1e6)
        data = data_gen.generate_uniform_alpha(n_elements)
        data.sort()
        counts = defaultdict(int)
        iterations = algos.complexity_better_than_n(counts, data)
        xs.append(n_elements)
        ys.append(iterations)
    print()
    p_opt, p_cov = curve_fit(log_complexity, xs, ys, p0=(2.0, 2.0))
    p1 = p_opt[0]
    p2 = p_opt[1]
    LOG.info('Equation:')
    LOG.info('\titerations = %.2f x log(n_elements) + %.2f' % (p1, p2))
    curve_xs = np.linspace(min(xs), max(xs), 1000)
    curve_ys = log_complexity(curve_xs, p1, p2)
    plt.plot(curve_xs, curve_ys, 'r')

    plt.scatter(xs, ys)
    plt.xlabel('Number of Elements')
    plt.ylabel('Number of Iterations')
    plt.title('Complexity')
    plt.show()


if __name__ == '__main__':
    args = config.parse_args()
    log.setup_logger(args.log_level)
    random.seed(1)
    estimate_complexity_better_than_n()

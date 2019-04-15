"""
This module contains functions to generate random data sets and view them.

"""

import random
import matplotlib
import logging
import numpy as np

matplotlib.use('TkAgg')  # osx pipenv requirement

import matplotlib.pyplot as plt


UNICODE_A = ord('a')
UNICODE_Z = ord('z')
UNICODE_MEAN = (UNICODE_A + UNICODE_Z) // 2
LETTERS_IN_ALPHABET = UNICODE_Z - UNICODE_A
UNICODE_STD = 10

LOG = logging.getLogger('DATA_GEN')


def generate_uniform_alpha(n_elements=1000):
    """
    Returns an unsorted list of characters between 'a' and 'z'. The distribution
    of of the elements is uniform.

    :param n_elements: length required
    :return: unsort list of chars
    """
    assert(n_elements > 0)
    domain = range(UNICODE_A, UNICODE_Z + 1)
    codes = random.choices(domain, k=n_elements)
    return list(map(chr, codes))


def generate_normal_alpha(mean, std, n_elements=1000):
    """
    Returns an unsorted list of characters between 'a' and 'z'. The distribution
    of of the elements is normal.

    :param mean: mean of the distribution
    :param std: standard deviation of the distribution
    :param n_elements: length required
    :return: unsort list of chars
    """
    assert (n_elements > 0)
    codes = np.random.normal(mean, std, n_elements).round().astype(np.int)
    return list(map(chr, codes))


def get_distribution_generator(name='uniform'):
    """
    Wrapper function to make the above data generators have the same interface.

    :param name: Name of the distribution {uniform|normal}
    :return: function from n_elements to random data
    """
    LOG.info(f'Used distribution: {name}')
    if name == 'uniform':
        return generate_uniform_alpha
    elif name == 'normal':
        return lambda n_elements: generate_normal_alpha(UNICODE_MEAN, UNICODE_STD, n_elements)
    else:
        raise Exception(f'Unknown distribution {name}')


def _plot_histogram_of_alphas(codes, title):
    number_of_bins = LETTERS_IN_ALPHABET+1
    plt.hist(codes, number_of_bins, density=True, facecolor='g', alpha=0.75)
    plt.xlabel(f'a={UNICODE_A},z={UNICODE_Z}')
    plt.ylabel('Probability')
    plt.title(title)
    plt.grid(True)
    plt.show()


def _test_generate_uniform_alpha():
    n_samples = 5000
    xs = generate_uniform_alpha(n_samples)
    assert(len(xs) == n_samples)
    codes = list(map(ord, xs))
    assert(UNICODE_A <= min(codes) and max(codes) <= UNICODE_Z)
    _plot_histogram_of_alphas(codes, 'Uniform Distribution')


def _test_generate_normal_alpha():
    n_samples = 5000
    xs = generate_normal_alpha(UNICODE_MEAN, UNICODE_STD, n_samples)
    assert (len(xs) == n_samples)
    codes = list(map(ord, xs))
    _plot_histogram_of_alphas(codes, 'Normal Distribution')


if __name__ == '__main__':
    random.seed(1)
    _test_generate_uniform_alpha()
    _test_generate_normal_alpha()

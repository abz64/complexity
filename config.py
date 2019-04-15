"""
Simple module to setup arguments to program.
"""

from argparse import ArgumentParser


def parse_args():
    """
    Common utility function for argument parsing.
    :return: argparse object
    """
    parser = ArgumentParser(description='Complexity', conflict_handler='resolve')
    parser.add_argument('--log-level', help='Set log level {DEBUG|INFO}', default='INFO')
    return parser.parse_args()

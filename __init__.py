import os

# text colors
class bcolors:
    magenta = '\033[95m'
    blue = '\033[94m'
    grey = '\033[37m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    nc = '\033[0m'

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

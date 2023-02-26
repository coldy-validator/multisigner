from os import path,getcwd

# text colors
class bcolors:
    magenta = '\033[95m'
    blue = '\033[94m'
    grey = '\033[37m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    nc = '\033[0m'

__location__ = path.realpath(
    path.join(getcwd(), path.dirname(__file__)))

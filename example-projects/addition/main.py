#!/usr/bin/env python

import sys

def main():
    args = sys.argv[1:]
    try:
        numbers = [int(x) for x in args]
    except:
        print("Error: could not parse arguments {0} as integers".format(args))
    else:
        result = sum(numbers)
        print("The sum is {0}".format(result))

if __name__ == "__main__":    
    main()
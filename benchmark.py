from time import clock

import example


def bench(func: callable, args: list):
    s = 0
    before = clock()
    for _ in range(10):
        s = func(*args)
    after = clock()

    print('%s %d elapsed %.7f' % (func.__name__, s, after - before))


def sum_array():
    arr = [a * 3 + 1 for a in range(10000)]

    bench(example.sum_array, [arr])
    bench(sum, [arr])


def tests():
    sum_array()


if __name__ == '__main__':
    tests()

# Problem 401: 510698. Squares of Numbers

def s(n):
    for i in range(1, n + 1):
        yield i * i

n = int(input())
for square in s(n):
    print(square)


# Problem 402: 510704. Even Numbers Generator

n = int(input())
def even(n):
    for i in range(0, n + 1, 2):
        yield i

for ev in even(n):
    if ev != 0:
        print(",", end="")
    print(ev, end="")


# Problem 403: 510705. Divisibility Check

def divisible(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())
for d in divisible(n):
    print(d, end=" ")


# Problem 404: 510706. Squares from A to B

def squares(a, b):
    for i in range(a, b + 1):
        yield i * i

a, b = list(map(int, input().split()))
for x in squares(a, b):
    print(x)


# Problem 405: 510723. The Countdown

def countdown(n):
    for i in range(n, -1, -1):
        yield i

n = int(input())
for c in countdown(n):
    print(c)


# Problem 406: 510707. Fibonacci Generator

def fib(n):
    a, b = 0, 1
    for i in range(n):
        yield a
        a, b = b, a + b

n = int(input())
for f in fib(n):
    if f != 0:
        print(",", end="")
    print(f, end="")


# Problem 407: 510708. Reverse Iterator

def reverse(n):
    yield n[::-1]

n = input()
for i in reverse(n):
    print(i)


# Problem 408: 510709. Prime Numbers Range

import math
def prime(n):
    for num in range(2, n + 1):
        isprime = True
        for i in range(2, int(math.sqrt(num)) + 1):
            if num % i == 0:
                isprime = False
                break
        if isprime:
            yield num

n = int(input())
for p in prime(n):
    print(p, end=" ")


# Problem 409: 510710. Powers of Two

def poww(n):
    for i in range(n + 1):
        yield 2 ** i

n = int(input())
for p in poww(n):
    print(p, end=" ")


# Problem 410: 510711. Limited Cycle

def lim(a, k):
    yield a * k

a = input().split()
k = int(input())
for i in lim(a, k):
    print(*i)
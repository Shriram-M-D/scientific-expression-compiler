# Test Cases for Scientific Expression Compiler

## Basic Arithmetic

2 + 3
5 - 2
4 _ 7
15 / 3
10 % 3
2 + 3 _ 4
(2 + 3) \* 4

## Power and Factorial

2^3
2^10
5!
10!
(3 + 2)!

## Unary Minus

-5
-(2 + 3)
-2^2
(-2)^2

## Scientific Functions - Trigonometry

sin(0)
sin(pi/2)
sin(pi/4)
cos(0)
cos(pi)
tan(pi/4)
asin(0.5)
acos(0.5)
atan(1)

## Scientific Functions - Logarithmic

log(100)
log(1000)
ln(e)
ln(e^2)
exp(0)
exp(1)
exp(2)

## Scientific Functions - Roots

sqrt(16)
sqrt(144)
cbrt(8)
cbrt(27)
abs(-5)
abs(5)

## Constants

pi
e
2 \* pi
e^2

## Complex Expressions

sin(pi/4) + cos(pi/4)
sqrt(144) + cbrt(27)
2^10 - 5!
log(100) / log(10)
abs(-5!) + sqrt(25)

## Numerical Differentiation

diff(x, x, 0)
diff(x, x, 1)
diff(x^2, x, 0)
diff(x^2, x, 1)
diff(x^2, x, 3)
diff(x^3, x, 2)
diff(sin(x), x, 0)
diff(sin(x), x, pi/2)
diff(cos(x), x, 0)
diff(exp(x), x, 0)
diff(ln(x), x, 1)
diff(x^2 + 2\*x + 1, x, 1)

## Numerical Integration (Trapezoidal)

integrate(1, x, 0, 1)
integrate(x, x, 0, 1)
integrate(x, x, 0, 10)
integrate(x^2, x, 0, 1)
integrate(x^2, x, 0, 3)
integrate(x^2, x, 0, 10)
integrate(sin(x), x, 0, pi)
integrate(cos(x), x, 0, pi/2)
integrate(exp(x), x, 0, 1)
integrate(1/x, x, 1, e)

## Combined Operations

2 _ sin(pi/4) + 3 _ cos(pi/4)
sqrt(sin(pi/4)^2 + cos(pi/4)^2)
log(e^5)
ln(exp(3))
abs(-10) + sqrt(100)

## Edge Cases

0 + 0
1 _ 1
0 _ 100
100 / 1
pi / pi
e / e

## Expected Errors (for testing error handling)

# sqrt(-1) # Domain error

# log(0) # Domain error

# log(-5) # Domain error

# 1/0 # Division by zero

# diff(x^2) # Missing arguments

# integrate(x^2, x) # Missing bounds

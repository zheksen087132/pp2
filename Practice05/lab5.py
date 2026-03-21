#501
import re

s = input()

if re.match(r'Hello', s):
    print("Yes")
else:
    print("No")

#502
import re

s = input()
sub = input()

if re.search(sub, s):
    print("Yes")
else:
    print("No")

#503
import re

s = input()
pattern = input()

matches = re.findall(pattern, s)
print(len(matches))

#504
import re

s = input()

digits = re.findall(r'\d', s)
print(" ".join(digits))

#505
import re

s = input()

if re.match(r'^[A-Za-z].*\d$', s):
    print("Yes")
else:
    print("No")

#506
import re

s = input()

match = re.search(r'\S+@\S+\.\S+', s)

if match:
    print(match.group())
else:
    print("No email")


#507
import re

s = input()
pattern = input()
replacement = input()

result = re.sub(pattern, replacement, s)
print(result)


#508
import re

s = input()
pattern = input()

parts = re.split(pattern, s)
print(",".join(parts))

#509
import re

s = input()

words = re.findall(r'\b[a-zA-Z]{3}\b', s)
print(len(words))


#510
import re

s = input()

if re.search(r'cat|dog', s):
    print("Yes")
else:
    print("No")


#511
import re

s = input()

uppercase_letters = re.findall(r'[A-Z]', s)
print(len(uppercase_letters))


#512
import re

s = input()

sequences = re.findall(r'\d{2,}', s)
print(" ".join(sequences))


#513
import re

s = input()

words = re.findall(r'\w+', s)
print(len(words))

#514
import re

s = input()

pattern = re.compile(r'^\d+$')

if pattern.fullmatch(s):
    print("Match")
else:
    print("No match")


#515
import re

s = input()

def double_digit(match):
    return match.group() * 2

result = re.sub(r'\d', double_digit, s)
print(result)


#516
import re

s = input()

match = re.match(r'Name: (.*), Age: (.*)', s)
if match:
    name, age = match.groups()
    print(name, age)


#517
import re

s = input()

dates = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', s)
print(len(dates))


#518
import re

s = input()
pattern = input()

escaped_pattern = re.escape(pattern)

matches = re.findall(escaped_pattern, s)
print(len(matches))


#519
import re

s = input()

pattern = re.compile(r'\b\w+\b')
words = pattern.findall(s)
print(len(words))
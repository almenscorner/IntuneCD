#!/usr/bin/env python3

# Courtesy of https://www.techiedelight.com/check-string-matches-with-wildcard-pattern/

# Recursive function to check if the input matches
# with a given wildcard pattern
def isMatch(word, n, pattern, m):
 
    # end of the pattern is reached
    if m == len(pattern):
        # return true only if the end of input is also reached
        return n == len(word)
 
    # if the input reaches its end, return when the
    # remaining characters in the pattern are all '*'
    if n == len(word):
        for i in range(m, len(pattern)):
            if pattern[i] != '*':
                return False
 
        return True
 
    # if the current wildcard character is '?' or the current character in
    # the pattern is the same as the current character in the input string
    if pattern[m] == '?' or pattern[m] == word[n]:
        # move to the next character in the pattern and the input string
        return isMatch(word, n + 1, pattern, m + 1)
 
    # if the current wildcard character is '*'
    if pattern[m] == '*':
        # move to the next character in the input or
        # ignore '*' and move to the next character in the pattern
        return isMatch(word, n + 1, pattern, m) or isMatch(word, n, pattern, m + 1)
 
    # we reach here when the current character in the pattern is not a
    # wildcard character, and it doesn't match the current
    # character in the input string
    return False
 
 
# Check if a string matches with a given wildcard pattern
def isMatching(word, pattern):
    return isMatch(word, 0, pattern, 0)
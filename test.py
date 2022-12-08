from collections import defaultdict
survey = ["AN", "CF", "MJ", "RT", "NA"]
choices = [5, 3, 2, 7, 5]
result = "TCMA"


def solution(survey, choices):
    indicator = [('R', 'T'), ('C', 'F'), ('J', 'M'), ('A', 'N')]
    answer = ''
    personality = defaultdict(int)
    for s, c in zip(survey, choices):
        if c < 4:
            personality[s[0]] += (4 - c)
        elif c > 4:
            personality[s[1]] += (c - 4)
    for i in indicator:
        if personality[i[0]] >= personality[i[1]]:
            answer += i[0]
        else:
            answer += i[1]
    return answer


# solution(survey, choices)

def test(a: list) -> list:
    a[0] = 5

import numpy as np
if __name__ == "__main__":
    np_arr = np.array([1, 2, 3])
    list_arr = [1, 2, 3]
    # test(arr)
    print(arr)
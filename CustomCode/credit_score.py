
def creditScore(currScore):
    x = (currScore + 0.428)/2
    y = -(5*x)+10  # credit score equation
    return y


def creditScoreNew(currScore):
    y = -(5*currScore)+10  # credit score equation
    return y
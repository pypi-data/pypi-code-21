import pandas as pd
import numpy as np

attack=pd.read_csv("scores-eval-attack", sep=" ", header=None)
real=pd.read_csv("scores-eval-real", sep=" ", header=None)

attack[0]=2
attack[1]="attack"
print(attack.head())

real[0]=1
real[1]=1
print(real.head())

scores=pd.concat([real,attack])
print(scores)
scores.to_csv("scores-eval", sep=" ", index=None, header=None)

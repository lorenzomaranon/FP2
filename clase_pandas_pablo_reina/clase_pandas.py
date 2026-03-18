import pandas as pd
'''

s = pd.Series([10, 20, 30, 40])
print(s)
df = pd.DataFrame({
    "nombre": ["Ana", "Luis", "Marta"],
    "edad": [20, 21, 19],
    "altura": [160,170,165]
})

print(df)

'''
# df = pd.read_csv("clase_pandas_pablo_reina/BostonHousing.csv")
# #print(df.head())
# #print(df[df["RM"]>7]["RM"]) 
# # print(df["RM"].max())
# df["PRICE_PER_ROOM"] = df["MEDV"]/df["RM"]
# print(df)
# print(df.groupby("CHAS")["MEDV"].mean())
# df.to_csv("clase_pandas_pablo_reina/BostonModified.csv", index=False)


#1
df = pd.read_csv("clase_pandas_pablo_reina/BostonHousing.csv")
#2
print(f"Ej 2: {df.iloc[0:5]}")
#3
print(df[(df["RM"]>7) & (df["MEDV"]>30)])
#4
print(df["CRIM"].sum())
#5
print(df["CHAS"].value_counts())
#6
big_house = df["RM"]>6.5
df["BIG_HOUSE"] = big_house
print(df["BIG_HOUSE"].head())
#7

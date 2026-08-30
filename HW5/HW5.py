
P_S = 0.30
P_notS = 0.70

P_C_given_S = 0.05
P_notC_given_S = 0.95

P_C_given_notS = 0.01
P_notC_given_notS = 0.99

P_T_given_C = 0.90
P_T_given_notC = 0.20


P_S_C_T = P_S * P_C_given_S * P_T_given_C

print("41. =", P_S_C_T)


P_C = (P_S * P_C_given_S) + \
      (P_notS * P_C_given_notS)

P_notC = 1 - P_C

P_T = (P_T_given_C * P_C) + \
      (P_T_given_notC * P_notC)

print("42. =", P_T)


P_C_given_T = (P_T_given_C * P_C) / P_T

print("43. =", P_C_given_T)



P_T_given_S = (
    P_C_given_S * P_T_given_C
    +
    P_notC_given_S * P_T_given_notC
)

# ใช้ Bayes
P_S_given_T = (P_T_given_S * P_S) / P_T

print("44. =", P_S_given_T)



P_C_and_T = P_C * P_T_given_C

people = 1000 * P_C_and_T

print("45. =", people)
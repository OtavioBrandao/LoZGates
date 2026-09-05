from BackEnd.equivalencia import check_universal_equivalence

test_cases = [
    ('P > Q', 'Q > P'),
    ('P > Q', '!P | Q'),
    ('P & Q', 'Q & P'),
    ('P | Q', 'Q | P'),
    ('P', '!P'),
    ('!(P & Q)', '!P | !Q')
]

for exp1, exp2 in test_cases:
    res = check_universal_equivalence(exp1, exp2)
    s = "EQUIVALENTES" if res else "NÃO EQUIVALENTES"
    print(f"{exp1} / {exp2} -> {s}")

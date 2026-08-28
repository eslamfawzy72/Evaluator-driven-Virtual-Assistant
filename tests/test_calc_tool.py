from agents.tools.calculator import calculator


# Basic arithmetic
print(calculator.invoke("92 + 95 + 89"))

# Average
print(calculator.invoke("average(92, 95, 89)"))

# Difference
print(calculator.invoke("95 - 89"))

# Power
print(calculator.invoke("2 ** 3"))

# Percentage improvement
print(calculator.invoke("percentage(100, 80)"))

# Ratio
print(calculator.invoke("ratio(92, 89)"))
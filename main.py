from agent import run_agent


user_input = input("You: ")

response = run_agent(user_input)

print("\nMuse:")
print(response)
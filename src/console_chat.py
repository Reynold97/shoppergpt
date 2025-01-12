from src.buyergpt import BuyerGPT


s = BuyerGPT()
print("ShopperGPT Demo:")

while True:
    human_input = input("Human Input: ")
    if human_input == 'exit':
        break
    response = s.run(human_input=human_input)
    print("ShopperGPT Response: " + response)
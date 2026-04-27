import random 

print("\nROCK PAPER SCISSORS GAME")
print("Instruciton: ")
print("Type rock, paper or scissors to play.")
print("Type quit anytime to exit.")

choices = ("rock","paper","scissors")
choices2 = ("scissors","rock","paper")

user_s = 0 
com_s = 0
 

while True:

    player = input("\nEnter a choice (rock,paper,scissors): ").lower()
    computer = random.choice(choices)

    if player == "quit":
        print("\n Game ended!")
        break

    if player not in choices:
        player = input("Enter a valid choice (rock,paper,scissors): ").lower()

    print(f"\nPlayer: {player},")
    print(f"Computer: {computer}")

    if player == computer:
        print("Its a tie!")

    elif choices.index(player) == choices2.index(computer):
        print("You win!")
        user_s += 1
    
    else:
        print("You lose!")
        com_s += 1
    
    if not input ("\nPlay again? (y/n): ").lower() == "y":
        break


print("\nScoreboard:")
print("You: ", user_s)
print("Computer: ", com_s)
print("Thanks for playing.\n")
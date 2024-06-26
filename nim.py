import math
import random
import time


class Nim():

    def __init__(self, initial=[1, 3, 5, 7]):

        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):

        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):

        return 0 if player == 1 else 1

    def switch_player(self):

        self.player = Nim.other_player(self.player)

    def move(self, action):

        pile, count = action

        # Check for errors
        if self.winner is not None:
            raise Exception("Game already won")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        # Update pile
        self.piles[pile] -= count
        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):

        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):

        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):

        # print(self.q[(state,action)])
        state_copy = tuple(state)
        if (state_copy, action) in self.q:
            return self.q[(state_copy,action)]
        else:
            return 0

    def update_q_value(self, state, action, old_q, reward, future_rewards):

        state_copy = tuple(state)
        self.q[(state_copy, action)] = old_q + self.alpha * (reward + future_rewards - old_q)

        # print(f"update_q_value: {self.q[(state_copy, action)]}")

    def best_future_reward(self, state):
        ans = -10
        actions = Nim.available_actions(state)
        possible = None
        zero_action = None

        for action in actions:
            try:
                temp = self.q[(tuple(state), action)]
                
                if (temp > ans):
                    ans = temp
                    possible = action
            except:
                continue

        if ans < 0 :
            return 0
        else:
            # print(f"best: {self.q[(tuple(state), possible)]}")
            return self.q[(tuple(state), possible)]


    def choose_action(self, state, epsilon=True):
        required_action = None
        ans = -10

        probability = random.randint(1,10)

        if epsilon is False or probability <= (10-(self.epsilon*10)):
            actions = Nim.available_actions(state)
            # print(actions)
            # print("NoneType")
            # print(state)
            count = 0
            required_action = next(iter(actions))
            for action in actions:
                try:
                    temp = self.q[(tuple(state), action)]
                    # print(temp)
                    if (temp > ans):
                        ans = temp
                        required_action = action
                except:
                    continue
            # print(required_action)
            return required_action
        else:
            # print("Not NoneType")
            actions = Nim.available_actions(state) 

            return random.choice(list(actions))

                        
def train(n):
    """
    Train an AI by playing `n` games against itself.
    """

    player = NimAI()

    # Play n games
    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:

            # Keep track of current state and action
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)
            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")

    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:

        # Print contents of piles
        print()
        print("Piles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        # Compute available actions
        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                print("Invalid move, try again.")

        # Have AI make a move
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print()
            print("GAME OVER")
            winner = "Human" if game.winner == human_player else "AI"
            print(f"Winner is {winner}")
            return

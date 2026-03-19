import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd

class BlackjackGame:
    def __init__(self):
        self.deck = self.create_deck()

    def create_deck(self):
        """Create a deck of cards."""
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = []
        for suit in suits:
            for rank in ranks:
                if rank in ['J', 'Q', 'K']:
                    value = 10
                elif rank == 'A':
                    value = 11  # Ace defaults to 11
                else:
                    value = int(rank)
                deck.append({'rank': rank, 'suit': suit, 'value': value})
        return deck

    def shuffle_deck(self):
        """Shuffle the deck."""
        random.shuffle(self.deck)

    def deal_card(self):
        """Deal a card."""
        if len(self.deck) < 10:  # Reshuffle if not enough cards
            self.deck = self.create_deck()
            self.shuffle_deck()
        return self.deck.pop()

    def calculate_hand_value(self, hand):
        """Calculate hand value."""
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['rank'] == 'A')

        # Handle Ace value (11 or 1)
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def is_bust(self, hand):
        """Check if bust."""
        return self.calculate_hand_value(hand) > 21

    def is_blackjack(self, hand):
        """Check if blackjack."""
        return len(hand) == 2 and self.calculate_hand_value(hand) == 21

class ImprovedMonteCarloPlayer:
    def __init__(self, epsilon_start=0.9, epsilon_end=0.05, epsilon_decay=0.995):
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.returns = defaultdict(list)
        self.state_action_count = defaultdict(lambda: defaultdict(int))

        # Improved epsilon decay strategy
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        self.policy = defaultdict(str)
        self.episode_count = 0

    def get_state(self, player_hand, dealer_up_card):
        """Get current state - using detailed state representation."""
        player_value = self.calculate_hand_value(player_hand)
        has_usable_ace = self.has_usable_ace(player_hand)
        dealer_value = dealer_up_card['value']

        # Clip state space for better learning efficiency
        player_value = min(player_value, 21)
        dealer_value = min(dealer_value, 11)

        return (player_value, dealer_value, has_usable_ace)

    def has_usable_ace(self, hand):
        """Check if there is a usable Ace (counted as 11 without busting)."""
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['rank'] == 'A')

        # Has Ace and current total <= 21 means usable Ace
        return aces > 0 and value <= 21 and any(card['rank'] == 'A' for card in hand)

    def calculate_hand_value(self, hand):
        """Calculate hand value."""
        value = sum(card['value'] for card in hand)
        aces = sum(1 for card in hand if card['rank'] == 'A')

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value
    
    def get_basic_strategy_action(self, state):
        """Basic strategy as initial policy."""
        player_value, dealer_value, has_usable_ace = state

        if has_usable_ace:
            # Soft hand strategy
            if player_value <= 17:
                return 'hit'
            elif player_value >= 19:
                return 'stand'
            else:  # 18
                return 'hit' if dealer_value >= 9 else 'stand'
        else:
            # Hard hand strategy
            if player_value <= 11:
                return 'hit'
            elif player_value >= 17:
                return 'stand'
            elif player_value <= 16 and dealer_value <= 6:
                return 'stand'
            else:
                return 'hit'
            
    def choose_action(self, state: tuple, training: bool = True) -> str:
        """Choose action using epsilon-greedy strategy.

        Args:
            state: Current state tuple (player_value, dealer_value, usable_ace)
            training: Whether in training mode

        Returns:
            Selected action, either 'hit' or 'stand'
        """
        if training and random.random() < self.epsilon:
            return random.choice(['hit', 'stand'])

        # Use Q-table if state has been visited
        if state in self.q_table and self.q_table[state]:
            return max(self.q_table[state], key=self.q_table[state].get)

        # Fall back to basic strategy for unseen states
        return self.get_basic_strategy_action(state)

    def update_q_table(self, episode: list, gamma: float = 1.0) -> None:
        """Update Q-table using First-Visit Monte Carlo method.

        Args:
            episode: List of (state, action, reward) tuples
            gamma: Discount factor
        """
        visited = set()
        G = 0.0

        # Traverse episode in reverse to compute returns
        for state, action, reward in reversed(episode):
            G = gamma * G + reward
            sa_pair = (state, action)

            # First-visit: only update on first occurrence
            if sa_pair not in visited:
                visited.add(sa_pair)
                self.state_action_count[state][action] += 1
                n = self.state_action_count[state][action]
                # Incremental mean update
                self.q_table[state][action] += (G - self.q_table[state][action]) / n

        self.episode_count += 1

        # Decay epsilon after each episode
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

def play_game(player, game, training=True):
    """Play one game - improved game logic."""
    game.shuffle_deck()

    # Deal initial cards
    player_hand = [game.deal_card(), game.deal_card()]
    dealer_hand = [game.deal_card(), game.deal_card()]

    episode = []

    # Check for natural blackjack
    if game.is_blackjack(player_hand):
        if game.is_blackjack(dealer_hand):
            return [(player.get_state(player_hand, dealer_hand[0]), 'stand', 0)], 21, 21
        else:
            return [(player.get_state(player_hand, dealer_hand[0]), 'stand', 1.5)], 21, game.calculate_hand_value(dealer_hand)

    # Player phase
    while True:
        if game.is_bust(player_hand):
            # Player busts, instant loss
            if episode:
                last_state, last_action, _ = episode[-1]
                episode[-1] = (last_state, last_action, -1)
            return episode, game.calculate_hand_value(player_hand), 0

        state = player.get_state(player_hand, dealer_hand[0])
        
        ###################################################################################
        #   Change to Epsilon-Greedy Strategy and Consider Q-table for action selection   #
        ###################################################################################
        # action = player.get_basic_strategy_action(state)
        action = player.choose_action(state, training)

        if action == 'hit':
            player_hand.append(game.deal_card())
            if game.is_bust(player_hand):
                episode.append((state, action, -1)) # Bust, immediate penalty
                return episode, game.calculate_hand_value(player_hand), 0 
            else:
                episode.append((state, action, 0))  # Intermediate reward is 0
        else:  # stand
            episode.append((state, action, 0))  # Stand, temporary reward 0
            break

    # Dealer phase
    while game.calculate_hand_value(dealer_hand) < 17:
        dealer_hand.append(game.deal_card())

    # Calculate final result
    player_value = game.calculate_hand_value(player_hand)
    dealer_value = game.calculate_hand_value(dealer_hand)

    if game.is_bust(dealer_hand):
        reward = 1  # Dealer busts, player wins
    elif player_value > dealer_value:
        reward = 1  # Player has higher value
    elif player_value < dealer_value:
        reward = -1  # Dealer has higher value
    else:
        reward = 0  # Draw

    # Update reward of the last step
    if episode:
        last_state, last_action, _ = episode[-1]
        episode[-1] = (last_state, last_action, reward)

    return episode, player_value, dealer_value

# Main
if __name__ == "__main__":
    # Set random seeds for reproducibility
    # random.seed(42)
    # np.random.seed(42)

    # Create game and player
    game = BlackjackGame()
    player = ImprovedMonteCarloPlayer()

    # --- Training phase ---
    num_training_episodes = 5000
    wins, losses, ties = 0, 0, 0

    print("============================================")
    print(f"Training for {num_training_episodes} episodes...")
    print("============================================")

    for i in range(num_training_episodes):
        episode, player_value, dealer_value = play_game(player, game, training=True)

        # Update Q-table with the completed episode
        player.update_q_table(episode)

        # Track outcomes from episode reward
        if episode:
            final_reward = episode[-1][2]
            if final_reward > 0:
                wins += 1
            elif final_reward < 0:
                losses += 1
            else:
                ties += 1

    print(f"\nTraining Results ({num_training_episodes} games):")
    print(f"  Wins:   {wins} ({wins / num_training_episodes * 100:.1f}%)")
    print(f"  Losses: {losses} ({losses / num_training_episodes * 100:.1f}%)")
    print(f"  Ties:   {ties} ({ties / num_training_episodes * 100:.1f}%)")

    # --- Q-table status ---
    num_states = len(player.q_table)
    total_sa_pairs = sum(len(actions) for actions in player.q_table.values())
    print(f"\nQ-table status:")
    print(f"  Learned states:        {num_states}")
    print(f"  State-action pairs:    {total_sa_pairs}")
    print(f"  Final epsilon:         {player.epsilon:.4f}")
    print(f"  Episodes processed:    {player.episode_count}")

    # --- Show a few sample Q-values ---
    print("\nSample Q-values (state -> action: value):")
    sample_states = list(player.q_table.keys())[:5]
    for state in sample_states:
        player_sum, dealer_up, usable_ace = state
        actions = player.q_table[state]
        best_action = max(actions, key=actions.get)
        print(f"  Player={player_sum}, Dealer={dealer_up}, "
              f"Ace={usable_ace} -> ", end="")
        for action, value in actions.items():
            marker = " *" if action == best_action else ""
            print(f"{action}: {value:.3f}{marker}  ", end="")
        print()

    # --- Play one demo game with learned policy ---
    print("\n============================================")
    print("Demo game (using learned policy, no exploration):")
    print("============================================")

    episode, player_value, dealer_value = play_game(player, game, training=False)

    print(f"Player's final hand value: {player_value}")
    print(f"Dealer's final hand value: {dealer_value}")

    print("\nEpisode details:")
    for i, step in enumerate(episode):
        state, action, reward = step
        player_sum, dealer_up, usable_ace = state

        print("--------------------------------------------")
        print(f"Step {i + 1}")
        print(f"  Player's hand value:    {player_sum}")
        print(f"  Dealer's up card value: {dealer_up}")
        print(f"  Usable Ace:             {usable_ace}")
        print(f"  Action:                 {action}")
        print(f"  Reward:                 {reward}")
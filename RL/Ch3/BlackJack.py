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
        if not training:
            # In evaluation mode, always choose pure Greedy action
            if state in self.policy and self.policy[state]:
                return self.policy[state]
            return self.get_basic_strategy_action(state)
          
        # Using epsilon-greedy strategy during training
        if training and random.random() < self.epsilon:
            return random.choice(['hit', 'stand'])

        # Greedy action selection
        if state in self.q_table and self.q_table[state]:
            return max(self.q_table[state], key=self.q_table[state].get)

        # If the state is unseen (the state is not learned), 
        # fall back to basic strategy as a reasonable default action
        return self.get_basic_strategy_action(state)

    def update_epsilon(self) -> None:
        
        # Update epsilon value
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def update_policy(self, episode: list, gamma: float = 1.0) -> None:
        """Update Q-table using First-Visit Monte Carlo method."""

        # Create a "set" to track visited state in this episode
        sta_act_in_episode = set()
        G = 0.0

        # Traverse episode in reverse
        for step in reversed(episode):
            state, action, reward = step
            G = reward + G  # No discount factor
 
            # Only update state-action pair on first occurrence to avoid duplicate estimation
            if(state, action) not in sta_act_in_episode:
                sta_act_in_episode.add((state, action))

                # Record the return for this state-action pair
                self.state_action_count[state][action] += 1
                self.returns[(state, action)].append(G)

                # Update Q-value using incremental mean for numerical stability
                old_q = self.q_table[state][action]
                n = self.state_action_count[state][action]
                self.q_table[state][action] = old_q + (G - old_q) / n

                # Update policy (Greedy)
                if self.q_table[state]:
                    best_action = max(self.q_table[state], key=self.q_table[state].get)
                    self.policy[state] = best_action

        # Update epsilon
        self.episode_count += 1
        if self.episode_count % 100 == 0:
            self.update_epsilon()

    
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

def train_player(num_episodes=200000):
    """Train a player using Monte Carlo method over many episodes.

    Args:
        num_episodes: Number of training episodes

    Returns:
        Tuple of (trained player, win rates list, epsilon values list)
    """
    player = ImprovedMonteCarloPlayer()
    game = BlackjackGame()

    wins, losses, ties = 0, 0, 0
    win_rates = []
    epsilon_values = []
    recent_results = []

    print("Starting training...")
    print(f"Initial epsilon: {player.epsilon:.3f}")

    for episode_num in range(num_episodes):
        ep, player_value, dealer_value = play_game(player, game, training=True)

        if ep:
            player.update_policy(ep)

            # Statistics results
            final_reward = ep[-1][2]
            recent_results.append(final_reward)

            if final_reward > 0:
                wins += 1
            elif final_reward < 0:
                losses += 1
            else:
                ties += 1

        # Record epsilon and win rate per 1000 episodes
        if (episode_num + 1) % 1000 == 0:
            recent_1000 = recent_results[-1000:] if len(recent_results) >= 1000 else recent_results
            recent_wins = sum(1 for r in recent_1000 if r > 0)
            recent_win_rate = recent_wins / len(recent_1000) if recent_1000 else 0

            win_rates.append(recent_win_rate)
            epsilon_values.append(player.epsilon)

            if (episode_num + 1) % 10000 == 0:
                total_win_rate = wins / (wins + losses + ties) if (wins + losses + ties) > 0 else 0
                print(f"Progress: {episode_num + 1}/{num_episodes}")
                print(f"  Recent 1000 games win rate: {recent_win_rate:.3f}")
                print(f"  Overall win rate: {total_win_rate:.3f}")
                print(f"  Current epsilon: {player.epsilon:.3f}")
                print(f"  States learned: {len(player.policy)}")

    total_win_rate = wins / num_episodes
    print(f"\nTraining complete!")
    print(f"Total games: {num_episodes}")
    print(f"Win: {wins}, Loss: {losses}, Tie: {ties}")

    return player, win_rates, epsilon_values


def plot_training_results(win_rates, epsilon_values):
    """Plot training progress and epsilon decay as two separate figures.

    Args:
        win_rates: List of win rates recorded every 1000 episodes
        epsilon_values: List of epsilon values recorded every 1000 episodes
    """
    episodes = [(i + 1) * 1000 for i in range(len(win_rates))]
    theoretical_optimal = 0.4268  # Blackjack theoretical optimal win rate

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    # Top: Win Rate Progress
    ax1.plot(episodes, win_rates, color='blue', linewidth=1, label='MC Win Rate')
    ax1.axhline(y=theoretical_optimal, color='red', linestyle='--',
                linewidth=1, label='Theoretical Optimal (~43%)')
    ax1.set_title('Monte Carlo Blackjack Learning - Win Rate Progress')
    ax1.set_xlabel('Episode')
    ax1.set_ylabel('Win Rate')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Bottom: Epsilon Decay
    ax2.plot(episodes, epsilon_values, color='green', linewidth=1)
    ax2.set_title('Epsilon Decay During Training')
    ax2.set_xlabel('Episode')
    ax2.set_ylabel('Epsilon')
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig('RL/Ch3/results/training_results.png', dpi=150)
    print("Saved: RL/Ch3/results/training_results.png")
    plt.close()


def test_player(player, num_games=10000):
    """Test a trained player without exploration.

    Args:
        player: Trained player instance
        num_games: Number of test games

    Returns:
        Win rate as a float
    """
    game = BlackjackGame()
    wins = 0

    for _ in range(num_games):
        ep, player_value, dealer_value = play_game(player, game, training=False)
        if ep and ep[-1][2] > 0:
            wins += 1

    win_rate = wins / num_games
    print(f"\nTest results ({num_games} games):")
    print(f"  Win rate: {win_rate:.3f}")
    return win_rate


def compare_with_basic_strategy(trained_player, num_games=10000):
    """Compare MC-learned policy against basic strategy."""
    game = BlackjackGame()
    basic_player = ImprovedMonteCarloPlayer(epsilon_start=0.0)
    basic_wins = 0

    for _ in range(num_games):
        game.shuffle_deck()
        player_hand = [game.deal_card(), game.deal_card()]
        dealer_hand = [game.deal_card(), game.deal_card()]

        # Player phase using basic strategy
        while True:
            state = basic_player.get_state(player_hand, dealer_hand[0])
            action = basic_player.get_basic_strategy_action(state)
            if action == 'hit':
                player_hand.append(game.deal_card())
                if game.is_bust(player_hand):
                    break
            else:
                break

        # Skip if player busted
        if game.is_bust(player_hand):
            continue

        # Dealer phase
        while game.calculate_hand_value(dealer_hand) < 17:
            dealer_hand.append(game.deal_card())

        player_final = game.calculate_hand_value(player_hand)
        dealer_final = game.calculate_hand_value(dealer_hand)

        if game.is_bust(dealer_hand) or player_final > dealer_final:
            basic_wins += 1

    basic_win_rate = basic_wins / num_games

    # Test Monte Carlo Strategy
    mc_win_rate = test_player(trained_player, num_games)
    
    print(f"Basic Strategy Win Rate: {basic_win_rate:.3f}")
    print(f"Monte Carlo Strategy Win Rate: {mc_win_rate:.3f}")
    print(f"Improvement: {((mc_win_rate - basic_win_rate) / basic_win_rate) * 100:.2f}%")


# Main
if __name__ == "__main__":

    # Train player - Use more episodes
    trained_player, win_rates, epsilon_values = train_player(200000)

    # Test player
    test_win_rate = test_player(trained_player, 10000)

    # Plot training results
    plot_training_results(win_rates, epsilon_values)

    # Compare with basic strategy
    compare_with_basic_strategy(trained_player, 10000)
import random
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class Player:
    """Represents a player in the Dreidel game."""
    def __init__(self, player_id, starting_coins):
        self.player_id = player_id
        self.wealth = starting_coins

    def is_out(self):
        """Check if the player is out of the game."""
        return self.wealth <= 0

    def adjust_wealth(self, amount):
        """Adjust the player's wealth by a given amount."""
        self.wealth += amount


class Game:
    """Simulates a Dreidel game."""
    POSSIBILITIES = ['nun', 'gimmel', 'hey', 'shin']

    def __init__(self, starting_coins, ante, num_players, max_rounds, enforce_pot_rule=False):
        self.players = [Player(player_id=i + 1, starting_coins=starting_coins) for i in range(num_players)]
        self.ante = ante
        self.pot = ante * num_players  # Initial pot size
        self.max_rounds = max_rounds
        self.round_results = []
        self.enforce_pot_rule = enforce_pot_rule  # Flag for the pot rule

    def enforce_pot_rule_if_needed(self):
        """Force all players to contribute 1 coin to the pot if the pot is empty or has 1 coin."""
        if self.pot <= 1:
            for player in self.players:
                if not player.is_out():
                    player.adjust_wealth(-self.ante)  # Players contribute 1 coin
                    self.pot += self.ante

    def execute_one_roll(self, player):
        """Simulate one Dreidel spin for a player."""
        if player.is_out():
            return "player out, no spin"

        # Ante up to play
        player.adjust_wealth(-self.ante)
        self.pot += self.ante

        # Roll the Dreidel
        result = random.choice(Game.POSSIBILITIES)

        if result == 'nun':
            pass  # Nothing happens
        elif result == 'gimmel':
            player.adjust_wealth(self.pot)
            self.pot = 0
        elif result == 'hey':
            half_pot = (self.pot + 1) // 2  # Round up if odd
            player.adjust_wealth(half_pot)
            self.pot -= half_pot
        elif result == 'shin':
            if not player.is_out():
                player.adjust_wealth(-self.ante)
                self.pot += self.ante

        return result

    def run(self):
        """Run the Dreidel game."""
        for round_number in range(self.max_rounds):
            active_players = [p for p in self.players if not p.is_out()]
            if len(active_players) <= 1:
                break  # Game ends if only one player remains

            # Enforce the pot rule if the flag is enabled
            if self.enforce_pot_rule:
                self.enforce_pot_rule_if_needed()

            for player in active_players:
                result = self.execute_one_roll(player)
                self.round_results.append({
                    'round': round_number,
                    'player_id': player.player_id,
                    'result': result,
                    'player_wealth': player.wealth,
                    'pot_size': self.pot,
                })

        return self.round_results


class DreidelSimulation:
    """Runs multiple Dreidel games and collects results."""
    def __init__(self, starting_coins, ante, num_players, max_rounds, num_games, enforce_pot_rule=False):
        self.starting_coins = starting_coins
        self.ante = ante
        self.num_players = num_players
        self.max_rounds = max_rounds
        self.num_games = num_games
        self.enforce_pot_rule = enforce_pot_rule
        self.results = []

    def run(self):
        random.seed(358)
        """Run all games and collect results."""
        for game_id in range(self.num_games):
            game = Game(
                starting_coins=self.starting_coins,
                ante=self.ante,
                num_players=self.num_players,
                max_rounds=self.max_rounds,
                enforce_pot_rule=self.enforce_pot_rule
            )
            results = game.run()
            for result in results:
                result['game_id'] = game_id
            self.results.extend(results)

        return pd.DataFrame(self.results)


# Run the simulation
starting_coins = 15
ante = 1
num_players = 4
max_rounds = 100
num_games = 1000

# Set the flag for the pot rule
enforce_pot_rule = False

simulation = DreidelSimulation(
    starting_coins=starting_coins,
    ante=ante,
    num_players=num_players,
    max_rounds=max_rounds,
    num_games=num_games,
    enforce_pot_rule=enforce_pot_rule
)

results_df = simulation.run()

results_df[results_df['game_id'] == 0]#.tail(10)

######### final_results_df
max_round_by_player_per_game = results_df.groupby(['game_id', 'player_id'])['round'].max().reset_index()#.rename(columns={'round':'latest_round'})
final_results_df = results_df.merge(max_round_by_player_per_game, on=['game_id', 'player_id', 'round'])

########################### Questions we have

####### How long do the games go?

num_rounds_by_game = results_df.groupby('game_id')['round'].max().reset_index()
num_rounds_by_game.describe()

####### How many games end early?
num_games - len(num_rounds_by_game[num_rounds_by_game['round'] == max_rounds - 1]) 

# sns.histplot(results_df.groupby('game_id')['round'].max(), bins=100)
# plt.show()

####### How often do people bust? 

len(results_df[results_df['player_wealth'] == 0]) / (num_players * num_games) # out of x games w/ y people, we have n busts. This is missing 12 games though
len(final_results_df[final_results_df['player_wealth'] == 0]) / (num_players * num_games)


####### How many busts per game?

busts_by_game = results_df[results_df['player_wealth'] == 0].groupby('game_id')['player_id'].nunique().reset_index().rename(columns={'player_id': 'num_busts'}) # 1-2 busts per game
busts_by_game.describe() # don't ever have 4 busts because the game ends once the 3rd has busted

busts_by_game = final_results_df[final_results_df['player_wealth'] == 0].groupby('game_id')['player_id'].nunique().reset_index().rename(columns={'player_id': 'num_busts'}) # 1-2 busts per game
busts_by_game.describe() # don't ever have 4 busts because the game ends once the 3rd has busted
bust_count = busts_by_game['num_busts'].value_counts().reset_index()
ax = sns.barplot(data=bust_count, x='num_busts', y='count')
for i in ax.containers:
    ax.bar_label(i)
plt.show()

####### When you bust, when does it happen?

results_df[results_df['player_wealth'] == 0].describe()#.groupby('game_id')['round'].min()
final_results_df[final_results_df['player_wealth'] == 0].describe()

####### Expected end state of each player? This doesn't include the 0s

results_df[results_df['round'] == max_rounds - 1].describe() #.groupby('player_id')['player_wealth'].describe()
final_results_df.describe()

####### Wealth as it progresses through the game?

agg_wealth_df =results_df.groupby(['player_id', 'round'])['player_wealth'].describe().reset_index()
agg_wealth_df[agg_wealth_df['round'] == 99]
sns.lineplot(data=agg_wealth_df, x='round', y='mean', hue='player_id', palette='bright')
plt.show()


final_wealth = final_results_df.groupby(['player_id'])[['player_wealth']].describe().reset_index()#.unstack(level=1).reset_index()
final_wealth.columns = final_wealth.columns.get_level_values(0)
final_wealth
sns.barplot(data=final_wealth, x='player_id', y='mean', hue='player_wealth', palette='bright')
plt.show()

######## what is probability of winning for each player?

results_df[results_df['round'] == max_rounds - 1].sort_values(['game_id', 'player_wealth'], ascending=[True, False])\
                                                 .groupby('game_id')['player_id'].first()\
                                                 .value_counts()

wins = final_results_df.sort_values(['game_id', 'player_wealth'], ascending=[True, False])\
                .groupby('game_id')['player_id'].first()\
                .value_counts().reset_index()
sns.barplot(data=wins, x='player_id', y='count')
plt.title('Number of Wins by Player')
plt.show()

######## how much money do you stand to win/lose/distributions of earnings

results_df['earnings'] = results_df['player_wealth'] - (starting_coins + ante)
results_df[results_df['round'] == max_rounds - 1].groupby('player_id')['earnings'].describe() # different numbers meaningfully < 1000

final_results_df['earnings'] = final_results_df['player_wealth'] - (starting_coins + ante)
final_results_df.groupby('player_id')['earnings'].describe()
final_results_df['earnings'].describe().round(2)
final_results_df['earnings'].quantile([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]).round(2)

len(final_results_df[final_results_df['earnings'] == 0]) / len(final_results_df)
len(final_results_df[final_results_df['earnings'] > 0]) / len(final_results_df)
len(final_results_df[final_results_df['earnings'] < 0]) / len(final_results_df)

sns.histplot(
    data=final_results_df, 
    x='earnings', 
    # hue='player_id', 
    # multiple='dodge', 
    # kde=False,
    palette='bright'
)
plt.title('Payout Distribution of Dreidel for 4 Players Over 1000 Games')
plt.show()

g = sns.FacetGrid(results_df[results_df['round'] == max_rounds - 1], col="player_id", col_wrap=2, height=4, sharex=True, sharey=True)
g.map(sns.histplot, "earnings", kde=False)
plt.tight_layout()
plt.show()


results_df[(results_df['player_id'] == 1) & (results_df['game_id'] == 527)]

outcome_freqs = final_results_df['earnings'].value_counts().reset_index() #/ (num_games * num_players)
outcome_freqs['freq'] = outcome_freqs['count'] / (num_games * num_players)
sns.histplot(data=outcome_freqs, x='earnings', y='freq', stat='count')
plt.title('Probability of Outcome')
plt.show()

####### How much does the house win if the house keeps whatever is in the pot at the end of 100 rounds? And let's say the house takes a % of winner's cut if everyone busts

house_earnings = results_df[results_df['round'] == max_rounds - 1]
house_earnings / num_games

final_pot_stats = final_results_df[final_results_df['player_wealth'] != 0].sort_values(['game_id', 'player_id'], ascending=[True, True])\
                .groupby('game_id')['pot_size'].last()#.sum()#.describe()
sns.histplot(data=final_pot_stats)
plt.title('Distribution of Final Pot Size over 1000 Games')
plt.show()

sum(final_pot_stats > 0) / len(final_pot_stats)

final_results_df.tail(10)
results_df.tail(10)
####### pot size over time




# pd.pivot_table(results_df, index=['round', 'result', 'pot_size', 'game_id'], columns='player_id', values='player_wealth', aggfunc='sum').reset_index()
# running_wealth_df = results_df.pivot(index='round', columns='player_id', values='player_wealth')
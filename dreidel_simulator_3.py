import datetime
import random
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
random.seed(740)
# http://www.slate.com/articles/life/holidays/2014/12/rules_of_dreidel_the_hannukah_game_is_way_too_slow_let_s_speed_it_up.html#lf_comment=249019397
# https://www.google.com/search?q=simulate+dreidel+outcomes&oq=simulate+dreidel+outcomes&aqs=chrome..69i57.5594j1j4&sourceid=chrome&ie=UTF-8
# https://www.google.com/search?q=dreidel+simulation+results&sxsrf=APq-WBvJfBcfLXL6Tt85zCI8968E7oSzbQ%3A1643632703689&ei=P9j3YZ61KZ-lptQPsqO6gAU&ved=0ahUKEwje0Mb7gNz1AhWfkokEHbKRDlAQ4dUDCA4&uact=5&oq=dreidel+simulation+results&gs_lcp=Cgdnd3Mtd2l6EAM6BwgAEEcQsAM6CAguEIAEELEDOgUIABCABDoECAAQQzoFCAAQkQI6BAgjECc6CAgAEIAEELEDOgcILhCxAxBDOgoIABCABBCHAhAUOgcIABCABBAKOgQIABAKOgUIIRCgAToFCAAQzQI6BQghEKsCSgUIPBIBNUoECEEYAEoECEYYAFDZAliaN2CROGgFcAJ4AIABXYgBqA2SAQIyM5gBAKABAcgBCMABAQ&sclient=gws-wiz
# http://educ.jmu.edu/~lucassk/Seminars/Moves%20Overheads%202015.pdf
#### simulate one turn for one player
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def execute_one_roll(player_wealth, current_pot_size, possibilities, ante, player_number):
    ## if a player doesn't have any coins they're knocked out, return exits the function and next person goes
    if player_wealth <= 0:
        dreidel_word = 'player out, no spin'
        # print(dreidel_word)
        return player_wealth, current_pot_size, dreidel_word
    # expend one coin to play
    player_wealth -= ante
    # put said coin in the pot
    current_pot_size += ante
    # roll
    result = random.randint(0,3)
    dreidel_word = possibilities[result]
    if dreidel_word == 'nun':
        pass
    elif dreidel_word == 'gimmel':
        # give player the pot
        player_wealth = player_wealth + current_pot_size
        # 0 out the pot
        current_pot_size = 0
        # print('gimmel, whole pot!')
    elif dreidel_word == 'hey':
        # give player half the pot, round up if odd
        if current_pot_size % 2 == 0:# check if even
            player_wealth = player_wealth + current_pot_size // 2
            # make the pot half the size
            current_pot_size = current_pot_size // 2
        elif current_pot_size % 2 == 1: # check if odd. could just make this an else, but for clarity
            player_wealth = player_wealth + current_pot_size // 2 + 1
            # make the pot half the size
            current_pot_size = current_pot_size // 2
        # print('hey, half pot!')
    elif dreidel_word == 'shin':
        ## check player wealth again, in the case that the ante put them over the edge to 0, so now this shin is them giving $ they don't have
        if player_wealth <= 0:
            dreidel_word = 'player out, no spin'
            return player_wealth, current_pot_size, dreidel_word
        # take one coin from the player
        player_wealth -= ante
        # put that coin in the pot
        current_pot_size += ante
        # print('shin, give one sucks to suck')

    # print(f'player_{player_number + 1} current_wealth = {player_wealth}; pot size = {current_pot_size}\n\n')
    return player_wealth, current_pot_size, dreidel_word


def run_dreidel_game(starting_coins, ante, num_players, n_rounds):
    ### initialize
    starting_pot_size = ante * num_players
    current_pot_size = starting_pot_size  # will be continuously updated
    possibilities = [
        'nun',  # do nothing
        'gimmel',  # whole pot
        'hey',  # 1/2 pot
        'shin'  # put one in the pot
    ]
    ### give all the players starting number of coins
    results_dict = {}
    results_dict['current_pot_size'] = [current_pot_size]
    results_dict['dreidel_word'] = ['start of game']
    results_dict['num_zeros'] = [0] ## tmp track the 0s to debug why it's not going to 0
    for i in range(num_players):
        globals()[f'player_{i + 1}_wealth'] = starting_coins
        ## initialize each players' wealth into a list
        results_dict[f'player_{i + 1}_wealth'] = [starting_coins]
    # todo -- make a player class with methods, feels like better way to do this
    ### simulate a game
    for round in range(n_rounds):
        # print(f'got here, turn number {turn}')
        ### simulate one full round of a game
        num_zeros = 0 # initialize this to check
        for player_number in range(num_players):
            # print(f'got here, i number {i}')
            # TODO: can we just make player_var = globals()[f'player_{player_number + 1}_wealth'] ? cleaner
            globals()[f'player_{player_number + 1}_wealth'], current_pot_size, dreidel_word = execute_one_roll(globals()[f'player_{player_number + 1}_wealth'], current_pot_size, possibilities, ante, player_number)
            ## update list in results_dict
            results_dict[f'player_{player_number + 1}_wealth'].append(globals()[f'player_{player_number + 1}_wealth'])
            results_dict['current_pot_size'].append(current_pot_size)
            results_dict['dreidel_word'].append(dreidel_word)
            ## need to check if all players except 1 have 0 wealth, then game over
            if results_dict[f'player_{player_number + 1}_wealth'][-1] == 0: # check the most recent value of the list
                num_zeros += 1
                results_dict['num_zeros'].append(num_zeros)
        if num_zeros == num_players - 1:
            # print('all players except 1 at 0, exiting game')
            return results_dict
    return results_dict


def get_results_frames(results_dict):
    pd.DataFrame(results_dict['current_pot_size'])
    roll_results_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if key in ['current_pot_size', 'dreidel_word']})
    wealth_results_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if 'player' in key})
    num_zeros_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if 'zeros' in key})

    return roll_results_df, wealth_results_df, num_zeros_df

def execute_multiple_games(starting_coins, ante, num_players, n_rounds, num_games):
    global_results = {}
    for i in range(num_games):
        results_dict = run_dreidel_game(starting_coins, ante, num_players, n_rounds)
        roll_results_df, wealth_results_df, num_zeros_df = get_results_frames(results_dict)
        ## append game number so it's easy to group on later
        roll_results_df['game_num'] = i; wealth_results_df['game_num'] = i; num_zeros_df['game_num'] = i;
        ##  put results in a big dictionary
        global_results[f'game_{i}_info_dict'] = {'roll_results_df' : roll_results_df, 'wealth_results_df' : wealth_results_df, 'num_zeros_df' : num_zeros_df, 'orig_results_dict' : results_dict}

    return global_results

def fill_short_games_to_n_rounds(tmp, n_rounds, num_players, wealth_results_or_roll_results = 'wealth'):
    """
    :param tmp: a df of an individual game
    :param n_rounds: the number of rounds in a game -- we will use this to determine how many rows the df should have
    :param wealth_results_or_roll_results: 'wealth' or 'roll'. whether we are looking at the wealth df or the roll df: if we are looking at wealth, len should be n_rounds + 1 rows, if roll results, (n_rounds * n_players) + 1
    :return: that df filled in with 0s and the winning player's wealth to n_rounds
    """
    if wealth_results_or_roll_results == 'wealth':
        expected_len_of_tmp = n_rounds + 1
    elif wealth_results_or_roll_results == 'roll':
        expected_len_of_tmp = (n_rounds * num_players) + 1
    if len(tmp) < expected_len_of_tmp: # if there's a data frame with less than 100 turns (initialize everyone at 0, then 100 turns of play), fill 0s and the final player's wealth to get to 100
        to_concat = pd.DataFrame(np.nan, index=[x for x in range(len(tmp), expected_len_of_tmp)], columns=tmp.columns)
        final = pd.concat([tmp, to_concat]).fillna(method = 'ffill') # carry the values all the way to the end
    else:
        final = tmp

    return final

############################## one game
starting_coins = 15
ante = 1
num_players = 4
n_rounds = 100
num_games = 1000
seed_wealth_of_players = num_games * (starting_coins + 1) # players each seed the pot with 1 coin to start each game

############################## play multiple games
start = datetime.datetime.now()
global_results = execute_multiple_games(starting_coins, ante, num_players, n_rounds, num_games = num_games)
end = datetime.datetime.now()
print(end - start)


############################## some processing
## pull out wealth results df into a big list to concat
# TODO AG: set this up to pull out the roll results, pot size at scale too probably?
list_of_wealth_results = [ global_results[x]['wealth_results_df'] for x in global_results.keys()] ## nice to have: This feels kinda jank/wrong/unperformant
# list_of_num_zero_results = [ global_results[x]['num_zeros_df'] for x in global_results.keys()]
list_of_roll_results = [ global_results[x]['roll_results_df'] for x in global_results.keys()]
full_wealth_df = pd.concat(list_of_wealth_results)
full_roll_results_df = pd.concat(list_of_roll_results) # getting a random
wealth_cols = [x for x in full_wealth_df.columns if 'player' in x]

############################## time to 0
# https://stackoverflow.com/questions/41255215/pandas-find-first-occurrence
times_to_zero = full_wealth_df.groupby('game_num')[wealth_cols].apply(lambda x: x.ne(0).idxmin()).replace(0, np.nan) # returns 0 if the player never gets to 0 in that game, so replace with nan
1 - times_to_zero.isnull().sum() / num_games # p(player goes to 0)
times_to_zero.quantile(np.linspace(.1, 1, 9, 0))#.describe() # if you go to 0, how often does it happen in
times_to_zero.mean()

############################## average game length
# check the length of each df, which will tell you the number of turns
game_lengths = full_wealth_df.groupby('game_num').apply(len) # len() = 101, or n_rounds + 1 because the first rounds initializes everyone with 0
game_lengths.quantile(np.linspace(.1, 1, 9, 0))#.describe()
len(game_lengths[game_lengths != n_rounds + 1])

############################## Some further processing
## fill  in 0s for all games that end earlier (and carry the winning player's wealth forward
full_wealth_df = full_wealth_df.groupby('game_num').apply(fill_short_games_to_n_rounds, n_rounds, num_players)\
                               .drop('game_num', axis = 1)\
                               .reset_index()\
                               .rename(columns = {'level_1':'round_num'})

full_roll_results_df = full_roll_results_df.groupby('game_num')\
                                           .apply(fill_short_games_to_n_rounds, n_rounds, num_players, 'roll')\
                                           .droplevel(0)
full_roll_results_df['round_num'] = full_roll_results_df.index / 4
# full_roll_results_df[full_roll_results_df['game_num'] == 33]

############################## Examine player wealth

## distro of final wealth for each player
final_results_df = full_wealth_df[full_wealth_df['round_num'] == n_rounds]
final_roll_results_df = full_roll_results_df[full_roll_results_df['round_num'] == n_rounds]
final_results_df[wealth_cols].apply(lambda x: x.quantile(np.linspace(.1, 1, 9, 0)))
(final_results_df[wealth_cols] > starting_coins + 1).sum() / num_games # pct of games you end up with more money than when you started -- note everyone sub 50% when house takes what's left in the pot
(final_results_df[wealth_cols] == 0).sum() / num_games # double checking the 0 calc
final_results_df.sum() / seed_wealth_of_players - 1 # long run return, if you played num_games over months let's say
## check that wealth put into system, which is players's starting coins + their seed coins each game == their final money + what's left in the pot after each game
assert (seed_wealth_of_players * num_players) == final_results_df.sum().drop(['game_num', 'round_num']).sum() + final_roll_results_df['current_pot_size'].sum(), "total starting wealth != total ending wealth"
assert final_roll_results_df['game_num'].nunique() == num_games #

## distros
mean_frame = full_wealth_df.groupby('round_num')[wealth_cols].mean()
quantile_frame = full_wealth_df.groupby('round_num')[wealth_cols].quantile([.25, .5, .75])\
                               .reset_index(level = 1)\
                               .rename(columns = {'level_1':'quantile'})


############################## plotting
# mean_frame.plot.line(y = wealth_cols, title = 'Avg wealth each turn')
# quantile_frame.plot.line(y = 'player_1_wealth')
# quantile_frame[quantile_frame['quantile'] == 0.5].plot.line(y = wealth_cols)
# quantile_frame[quantile_frame['quantile'] == 0.75].plot.line(y = wealth_cols)

############################## TODO AG next steps
# verify what's going at the end of the game is correct as well

# and then version where you get pot remainder allocated at the end of the night

# a nice way to plot the distributions/percentiles of player wealth -- .25, .5, .75 for one player on a graph
# what next avenues for research would be
# document/understand logic
# write up in markdown?
## TODO AG sanity checks



############################## QA

## step through a game and see things are going right
# i = 33# i = 2 is where we see not all 64 coins at the end, there's something fishy about that one
# wealth_results_df = global_results[f'game_{i}_info_dict']['wealth_results_df']
# wealth_results_df.iloc[-1].drop('game_num').sum()
# roll_results_df = global_results[f'game_{i}_info_dict']['roll_results_df']
# roll_results_df['round_number'] = roll_results_df.index / num_players # every 4th pot size should be the value of the pot after a full round
# roll_results_df = roll_results_df.set_index('round_number')
# wealth_results_df.head()
# roll_results_df.head(20)
#
# merged = wealth_results_df.merge(roll_results_df.drop('game_num', axis = 1), left_index = True, right_index = True) # modify dropping the game if you do this systematically across the board
# merged['wealth_in_system'] = merged.drop(['game_num', 'dreidel_word'], axis = 1).sum(axis = 1)
# merged[merged['wealth_in_system'] != starting_coins * num_players + 4]

import datetime
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
random.seed(740)
# http://www.slate.com/articles/life/holidays/2014/12/rules_of_dreidel_the_hannukah_game_is_way_too_slow_let_s_speed_it_up.html#lf_comment=249019397
# https://www.google.com/search?q=simulate+dreidel+outcomes&oq=simulate+dreidel+outcomes&aqs=chrome..69i57.5594j1j4&sourceid=chrome&ie=UTF-8
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
        # give player half the pot, round down if odd
        player_wealth = player_wealth + current_pot_size // 2
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

def fill_short_games_to_n_rounds(tmp):
    """
    :param tmp: a df of an individual game
    :return: that df filled in with 0s and the winning player's wealth to n_rounds
    """
    if len(tmp) < 101: # if there's a data frame with less than 100 turns (initialize everyone at 0, then 100 turns of play), fill 0s and the final player's wealth to get to 100
        to_concat = pd.DataFrame(np.nan, index=[x for x in range(len(tmp), n_rounds + 1)], columns=tmp.columns)
        final = pd.concat([tmp, to_concat]).fillna(method = 'ffill') # carry the values all the way to the end
    else:
        final = tmp

    return final

############################## one game
starting_coins = 15
ante = 1
num_players = 4
n_rounds = 100

# results_dict = run_dreidel_game(starting_coins, ante, num_players, n_rounds)
# roll_results_df, wealth_results_df, num_zeros_df = get_results_frames(results_dict)
# wealth_results_df
# wealth_results_df[(wealth_results_df['player_2_wealth'] == 0) & (wealth_results_df['player_3_wealth'] == 0) & (wealth_results_df['player_1_wealth'] == 0)]


############################## play multiple games
start = datetime.datetime.now()
global_results = execute_multiple_games(starting_coins, ante, num_players, n_rounds, num_games = 100)
end = datetime.datetime.now()
print(end - start)


############################## some processing
## pull out wealth results df into a big list to concat

list_of_wealth_results = [ global_results[x]['wealth_results_df'] for x in global_results.keys()] ## nice to have: This feels kinda jank/wrong/unperformant
list_of_num_zero_results = [ global_results[x]['num_zeros_df'] for x in global_results.keys()]

## examining 0s
# full_zeros_df = pd.concat(list_of_num_zero_results)
# full_zeros_df[full_zeros_df['game_num'] == 9]#.tail()

### examining wealth
full_wealth_df = pd.concat(list_of_wealth_results)#.reset_index().rename(columns = {'index':'round_number'}) # nice to have: Can look into perf of just leaving and grouping by index
tmp = full_wealth_df[full_wealth_df['game_num'] == 99]
tmp_series = tmp['player_3_wealth']
tmp_series[tmp_series == 0].index.min()

player_wealth_series = full_wealth_df[['player_1_wealth']
full_wealth_df[['game_num', 'player_1_wealth']].apply(get_time_to_zero)

full_wealth_df[]

def get_time_to_zero(player_wealth_series):

    # tmp = full_wealth_df[full_wealth_df['game_num'] == 99]
    # tmp_series = tmp['player_3_wealth']
    # tmp_series[tmp_series == 0].index.min()

    ## find where 0s occur and then take the smallest index number -- since indices are recording the turns
    return player_wealth_series[player_wealth_series == 0].index.min()

full_wealth_df[full_wealth_df['game_num'] == 98][wealth_cols].apply(get_time_to_zero)

full_wealth_df.groupby('game_num')[wealth_cols].sum()

full_wealth_df

full_wealth_df.groupby()

full_wealth_df[full_wealth_df['game']]

grouped_obj = full_wealth_df.groupby('game_num')
grouped_obj.get_group(list(grouped_obj.groups)[0]) # first value in each group, which is ofc going to be 15


full_wealth_df[full_wealth_df['game_num'] == 0]



############################## average time to 0

############################## average game length
# check the length of each df, which will tell you the number of turns
game_lengths = full_wealth_df.groupby('game_num').apply(len) # len() = 101, or n_rounds + 1 because the first rounds initializes everyone with 0
game_lengths.describe()

############################## chart distribution of wealth over time
## fill  in 0s for all games that end earlier (and carry the winning player's wealth forward
full_wealth_df = full_wealth_df.groupby('game_num').apply(fill_short_games_to_n_rounds)\
                               .drop('game_num', axis = 1)\
                               .reset_index()\
                               .rename(columns = {'level_1':'round_num'})
wealth_cols = [x for x in full_wealth_df.columns if 'player' in x]

## get the actual distros
mean_frame = full_wealth_df.groupby('round_num')[wealth_cols].mean()
quantile_frame = full_wealth_df.groupby('round_num')[wealth_cols].quantile([.25, .5, .75])\
                               .reset_index(level = 1)\
                               .rename(columns = {'level_1':'quantile'})

## plot
mean_frame.plot.line(y = wealth_cols)
quantile_frame[quantile_frame['quantile'] == 0.5].plot.line(y = wealth_cols)
quantile_frame[quantile_frame['quantile'] == 0.75].plot.line(y = wealth_cols)

## distro of final wealth for each player
full_wealth_df[full_wealth_df['round_num'] == 100].quantile([.6, .7, .8, .9])#.describe()

quantile_frame.head()

## TODO AG next steps
# get the average time to 0 for each player
# step through and document/understand logic
# set up the plotting

## TODO AG sanity checks
    # num_zeros shouldn't decrease? Or think about a scenario where it could





## questions
## chart wealth over time
## if you play a bunch of games, how much money can you expect to have at the end of the night?
    ## have to decide --
        # do you get to re-up each game from the bank and you can accumulate debt -- is that the same as allowing negative numbers in one big infinite game
        # once you hit 0 are you done for the night
        # you play til 0, then if you were 0 the previous game we'll say you take a loan of starting wealth from the bank.
    ## in effect this is saying chart wealth across games
    ## how does this change based on pot size, number of players, ante size
## average time to 0?
    ## how does thi changed based on pot size, number of players, ante size
## * if the pot starts off relatively small to the players intial allcoations, does everyone more or less stay close to each other
## * if the pot starts off large relative to player allocations, does teh first gimmel/hey dictate a likely winner early on


# df = pd.DataFrame({'String 1': ['Tom', 'Nick', 'Krish', 'Jack'],
#                    'String 2': ['Jane', 'John', 'Doe', 'Mohan']})
#
#
# # function for prepending 'Geek'
# def prepend_geek(name):
#     return 'Geek ' + name
#
#
# # executing the function
# df[["String 1", "String 2"]] = df[["String 1", "String 2"]].apply(prepend_geek)
import random
import pandas as pd
random.seed(740)
# http://www.slate.com/articles/life/holidays/2014/12/rules_of_dreidel_the_hannukah_game_is_way_too_slow_let_s_speed_it_up.html#lf_comment=249019397
# https://www.google.com/search?q=simulate+dreidel+outcomes&oq=simulate+dreidel+outcomes&aqs=chrome..69i57.5594j1j4&sourceid=chrome&ie=UTF-8
#### simulate one turn for one player


def execute_one_roll(player_wealth, current_pot_size, possibilities, ante, player_number):
    ## if a player doesn't have any coins they're knocked out, return exits the function and next person goes
    if player_wealth <= 0:
        dreidel_word = 'player out, no spin'
        print(dreidel_word)
        return player_wealth, current_pot_size, dreidel_word
    # expend one coin to play
    player_wealth -= ante
    # put said coin in the pot
    current_pot_size += ante
    # roll
    result = random.randint(0,3)
    dreidel_word = possibilities[result]
    if dreidel_word == 'nun':
        print('nun, pass')
    elif dreidel_word == 'gimmel':
        # give player the pot
        player_wealth = player_wealth + current_pot_size
        # 0 out the pot
        current_pot_size = 0
        print('gimmel, whole pot!')
    elif dreidel_word == 'hey':
        # give player half the pot, round down if odd
        player_wealth = player_wealth + current_pot_size // 2
        # make the pot half the size
        current_pot_size = current_pot_size // 2
        print('hey, half pot!')
    elif dreidel_word == 'shin':
        ## check player wealth again, in the case that the ante put them over the edge to 0, so now this shin is them giving $ they don't have
        if player_wealth <= 0:
            dreidel_word = 'player out, no spin'
            return player_wealth, current_pot_size, dreidel_word
        # take one coin from the player
        player_wealth -= ante
        # put that coin in the pot
        current_pot_size += ante
        print('shin, give one sucks to suck')

    print(f'player_{player_number + 1} current_wealth = {player_wealth}; pot size = {current_pot_size}\n\n')
    return player_wealth, current_pot_size, dreidel_word


def run_dreidel_game(starting_coins, ante, num_players, n_turns):
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
    for turn in range(n_turns):
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
            print('got here')
            ## need to check if all players except 1 have 0 wealth, then game over
            if results_dict[f'player_{player_number + 1}_wealth'][-1] == 0: # check the most recent value of the list
                print('got here 2')
                num_zeros += 1
                print(f'num_zeros is {num_zeros}')
                results_dict['num_zeros'].append(num_zeros)
        if num_zeros == num_players - 1:
            print('all players except 1 at 0, exiting game')
            return results_dict
    return results_dict


def get_results_frames(results_dict):
    pd.DataFrame(results_dict['current_pot_size'])
    roll_results_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if key in ['current_pot_size', 'dreidel_word']})
    wealth_results_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if 'player' in key})
    num_zeros_df = pd.DataFrame({key:results_dict[key] for key in results_dict.keys() if 'zeros' in key})

    return roll_results_df, wealth_results_df, num_zeros_df

############################## one game
starting_coins = 15
ante = 1
num_players = 4
n_turns = 100

results_dict = run_dreidel_game(starting_coins, ante, num_players, n_turns)
roll_results_df, wealth_results_df, num_zeros_df = get_results_frames(results_dict)
# wealth_results_df
wealth_results_df[(wealth_results_df['player_2_wealth'] == 0) & (wealth_results_df['player_3_wealth'] == 0) & (wealth_results_df['player_1_wealth'] == 0)]

##############################

############################## multiple games
def execute_multiple_games(starting_coins, ante, num_players, n_turns, num_games):
    global_results = {}
    for i in range(num_games):
        results_dict = run_dreidel_game(starting_coins, ante, num_players, n_turns)
        roll_results_df, wealth_results_df, num_zeros_df = get_results_frames(results_dict)
        global_results[f'game_{i}_info_dict'] = {'roll_results_df' : roll_results_df, 'wealth_results_df' : wealth_results_df, 'num_zeros_df' : num_zeros_df, 'orig_results_dict' : results_dict}

    return global_results

global_results = execute_multiple_games(starting_coins, ante, num_players, n_turns, num_games = 2)

global_results['game_0_info_dict']['wealth_results_df']

global_results['game_1_info_dict']['wealth_results_df']

## TODO AG sanity checks
    # num_zeros shouldn't decrease? Or think about a scenario where it could




## next steps
# set up the running of multiple games and results collection
# step through and document/understand logic
# set up the plotting of 1) 1 player's wealther over many games, all players' wealth over one game, all players' wealthe over many games

## questions
## if you play a bunch of games, how much money can you expect to have at the end of the night?
    ## have to decide --
        # do you get to re-up each game from the bank and you can accumulate debt -- is that the same as allowing negative numbers in one big infinite game
        # once you hit 0 are you done for the night
    ## how does this change based on pot size, number of players, ante size
## average time to 0?
    ## how does thi changed based on pot size, number of players, ante size
## * if the pot starts off relatively small to the players intial allcoations, does everyone more or less stay close to each other
## * if the pot starts off large relative to player allocations, does teh first gimmel/hey dictate a likely winner early on
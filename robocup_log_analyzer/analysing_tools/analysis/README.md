# Analysis
A collection of functions to analyse data inside the datamodel.\
Currently finished but unused functions are $`\textcolor{orange}{\text{orange}}`$. \
Unchecked functions are unfinished or not fully tested

## analyzer.py
Legacy analyses close to the old analyses of the game.
Some need to be reviewed or maybe put into their own class. \
$`\textcolor{red}{\textbf{NO FUNCTIONS SHOULD BE ADDED TO THIS CLASS!!!}}`$ 


- [x] `get_tackle_times`: timesteps when a tackle happened
- [x] `analyze_ball_field_half_ratio`: ball field half ratio (precentage)
- [x] $`\textcolor{orange}{\textbf{count\textunderscore referee\textunderscore decisions:}\text{ counts the number of referee decisions throughout the game}}`$
- [x] `get_referee_decision_timestemps`: all referee decisions with a list of timesteps when they happened
- [x] `analyze_possession_percentage`: ball possession percentage
- [x] $`\textcolor{orange}{\textbf{count\textunderscore passes\textunderscore and\textunderscore missed\textunderscore passes:}\text{ counts successful and unsuccessful pass attempts}}`$
- [x] $`\textcolor{orange}{\textbf{count\textunderscore successful\textunderscore and\textunderscore unsuccessful\textunderscore dribblings:}\text{ counts successful and unsuccessful dribblings}}`$
- [x] `get_goals_per_half_and_timing`: gets goals in first half, second half, after time and their exact timesteps
- [x] `analyse_shot`: ?

## stamina.py
All stamina analyses should be in this class.

- [ ] `stamina_low_percentage`: calculates at what timesteps a players stamina dropped below a certain percentage
- [ ] `dashes_away_from_ball`: calculates the timesteps of dashes that happened when a player was not near the ball

## offside.py
All offside analyses should be in this class.

- [x] $`\textcolor{orange}{\textbf{calc\textunderscore offside\textunderscore x:}\text{ calculates for every timestep the offside line for both teams}}`$

## goals.py
All goal analyses should be in this class.

- [ ] `goal_miss_analysis`: analyses why a goal shot missed

## passes.py
All pass analyses should be in this class.

- [x] `count_passes`: counts all passes in the game according to their team and direction
- [ ] `count_through_passes`:
- [x] `pass_chain`: all pass chains according to their length and team

## dribblings.py
All dribbling analyses should be in this class

- [ ] `count_dribblings`: counts the amount of dribblings of the game according to the teams



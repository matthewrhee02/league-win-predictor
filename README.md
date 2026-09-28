# league-win-predictor
When Is a League of Legends Game Decided?

Predicting Match Outcomes from Early Game Data

Project Description

League of Legends is a competitive 5 vs 5 game where teams gain advantages through gold, experience, kills, objectives, towers, and other in game events. Although players often describe games as being "won" or "lost" early, it is usually not always clear how early the final result actually becomes predictable. 

The goal of this project is to use real League of Legends match data to determine how accurately the winner of a ranked match can be predicted from the state of the game at approximately 5, 10, and 15 minutes.

Using the official Riot Games API, I will collect ranked match histories and timeline data. For each match, I will reconstruct the game state at these three time points and extract features like gold difference, experience differece, lane cs difference, jungle cs difference, kill difference, tower difference, dragon difference, early objective difference, first blood, first tower, first dragon, and role specific gold differences. I will then train machine learning models to predict whether the Blue or Red team eventually wins the game. 

A secondary part of the project will investigate which early game advantages and events are most strongly associated with a team's probability of winning. For example, the analysis might examine whether gold difference is more informative than kill difference, how useful first blood is as a predictor, or whether an early gold lead in one role is more important than a similar lead in another role. 

The project forcuses on 2 main questions:
1. How accurately can the winner of a League of Legends match be predicted at 5, 10, and 15 minutes?
2. Which early game features are most strongly associated with winning?

Motivation

I chose this project because I regularly play League of Legends in my free time and am interested in understanding the game through data instead of relying only on player intuition. I also realized that a League of Legends match can be a useful data science problem because no single statistic completely describes which team is winning. A team could have more kills but less gold, more gold but fewer objectives, or an early advantage that disappears later in game. I've noticed in my own games that I feel like we were winning in the early game but ended up losing the match. 

Project Goals

Primary Goal

The primary goal of the project is to predict the winner of a ranked League of Legends match using only information available at approximately 5, 10, 15 minutes.

I will evaluate the prediction problem separately at each time point. This will allow me to compare questions like:
How accurately can the winner be predicted after only 5 minutes?
How much does prediction improve by 10 minutes?
How predictable is the winner by 15 minutes?
The main measureable result will be the performance of the trained models on matches that were not used during training. 

Secondary Goal

The secondary goal is to determine which early game features and events are most strongly associated with the probability of eventually winning the match. 

Questions I will investigate include:
Is gold difference more predictive than kill difference?
How useful is XP difference?
How strongly is first blood associated with winning?
How important is first tower?
How important is first dragon?
Do early objective advantages improve prediction?
Are gold advantages in some roles more informative than others?
How much does model confidence increase between 5, 10, and 15 minutes?
Because this project uses observational match data, these results will be interpreted as associations rather than proof of causation.

Data collection Plan

Data Source

The primary data source will be the official Riot Games API.
The project will use League of Legends match and timeline data to obtain ranked match IDs, match results, participant information, match timelines, and timestamped in game events.
The timeline also provides events and statistics that can be used to reconstruct the match state, including total gold, XP, minions killed, jungle minions killed, champion kills, first blood, dragons, void grubs, rift herald, towers, baron, and more. 

Dataset

The initial dataset will focus on:
Region: North America
Game Mode: Ranked Solo/Duo
Patch Range: Limited set of recent patches
Target Size: Around 5000-10000 matches

Collection Method

A Python program will be written to automatically collect data from the Riot Games API. The collection process will follow:

Seed Players -> Retrieve PUUIDs -> Retrieve Ranked Match IDs -> Download Match Information -> Download Match Timelines -> Extract Additional Players -> Collect Additional Matches

Each match contains information about the players who participated in it. These players can be used to discover additional ranked matches, allowing the dataset to grow without manually entering thousands of player names. 

Match IDs will be tracked so that duplicate games are not downloaded or processed multiple times. Raw API data will be stored separately from processed data so that the cleaning and feature extraction steps can be reproduced.

Data Cleaning and Feature Extraction

Collected matches will be cleaned before being used for modeling.

Possible cleaning steps will be removing duplicate matches, removing non Ranked Solo/Duo matches, Removing remakes or unusually short matches, removing matches with missing timeline data, removing incomplete or invalid API responses. restricting matches to the selected patch range, and ensuring usable 5, 10, and 15 minute timeline frames exist.

For each valid match, features will then be calculated at approximately 5, 10, and 15 minutes. Many features will be represented as the difference between 2 teams.

For example:
gold_difference = blue_team_gold - red_team_gold

Extracted Features will include:
Gold Difference - Blue team gold minus Red team gold
XP Difference - Blue team XP minus Red team XP
Lane CS Difference - Difference in lane minions killed
Jungle CS Difference - Difference in jungle monsters killed
Kill Difference - Blue kills minus Red kills
Tower Difference - Difference in towers destroyed
Dragon Difference - Difference in Dragons taken
Early Objective Difference - Difference in early neutral objectives
First Blood - Which team earned first blood
First Tower - Which team destroyed the first tower
First Dragon - Which team killed the first dragon
Role Gold Differences - Gold differences between corresponding roles

The prediction target will be: 
blue_win = 1 if Blue wins
blue_win = 0 if Red wins

Preliminary Modeling Plan

The project will begin with a simple baseline before testing more advanced models.

Models will most likely include:
Baseline, Logistic Regression, Random Forest, and Gradient Boosted Trees.

Model Evaluation Plan

The collected matches will be divided into separate training, validation, and testing groups.

The split will look something like this:
70% training
15% Validation
15% Final Testing
The split will occur at the match level, meaning that all observations from the same game must remain in the same partition. For example, the 5, 10, and 15 minute data from one match will never be divided between training and testing. If practical, the split will also be chronological so that models are trained on older matches and evaluated on newer matches. The final test data will not be used while selecting models or features.
The most important comparison will be how prediction performance changes between the 5, 10, and 15 minute models.

Planned Visualizations

Prediction Performance Over Time

A graph of prediction performance over time will compare model performance at 5, 10 and 15 minutes. This will directly help answer the question, when does a League of Legends match become reasonably predictable?

Feature Importance

The project will visualize which features contribute most strongly to predictions, such as gold difference, XP difference, kill difference, tower difference, dragon difference, and first blood.

Match Win Probability Visualization

As an extension, the model will be used to visualize predicted win probability throughout an individual match. Important events such as dragons, towers, first blood, or baron could be marked on the graph to show how the predicted outcome changes throughout the game.

Project Timeline

The project is planned over approximately 8 weeks:
Week 1 - Finalize Proposal
Week 2 - Build automated match and timeline collection scripts
Week 3 - Begin large scale data collection and duplicate handling
Week 4 - Finish primary data collection, clean matches, and build feature extraction
Week 5 - Perform exploratory data analysis, create preliminary visualizations, and train baseline models
Week 6 - Train and compare Logistic Regression, Random Forest, and gradient boosted models
Week 7 - Analyze model performance, feature importance, and win probability visualizations
Week 8 - Final testing, reproducibility checks, and project cleanup

Challenges and Fallback Plan

Possible challenges include Riot API rate limits, incomplete match data, changes between League patches, and the time required to collect thousands of matches. 

If the original project scope becomes too large, the fallback project will focus on the primary research question only.

The minimum successful version of the project will collect several thousand Ranked Solo/Duo matches, extract features at approximately 5, 10, and 15 minutes, train a baseline model and at least 1 machine learning model, compare prediction performance across the 3 timestamps, analyze which early game features are most informative, and create clear visualization of the results.
More advanced analysis, such as continuous win probability graphs or detailed role specific modeling, can be treated as extensions if time allows.

Repository

The project will be maintained using Git and GitHub throughout development. The repository will contain the code needed for data collection, data cleaning, feature extraction, model training, model evaluation, and visualization. The final repository will also include documentation explaining how to install dependencies and reproduce the results. Riot API credentials and other private information will not be committed to GitHub.

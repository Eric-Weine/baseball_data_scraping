# This should all work, but I need to make sure that 
import pandas as pd
import bs4 as bs

# Overview: This code scrapes pitcher vs. batter matchup data from baseball reference.
players_df = pd.read_csv("../data/player_directory_full.csv", encoding='latin-1') # read in for global variable usage

# Description: Function creates the URL for a pitcher's matchups vs. hitters for a year range
# Params: (str) bref_playerID - baseball reference id of player, (str) start_date - first year of scraping as yyyy,
# 		  (str) end_date - last year of scraping as yyyy, (str) bat_hand - hand of opp. batter as "R" or "L",
#		  (str) pitch_hand - hand of pitcher as "R" or "L"
# Return: (str) url that points to the correct player page
def bref_matchups_url(bref_playerID, start_date, end_date, bat_hand, pitch_hand):
	# include switch hitters if applicable
	if bat_hand != pitch_hand:
		bat_hand = bat_hand + "orB"
	url = "https://www.baseball-reference.com/play-index/batter_vs_pitcher.cgi?request=1&submitter=1&pitcher=%s&min_year_game=%s&max_year_game=%s&post=1&bats=%s&c1gtlt=gt&c2gtlt=gt&orderby=PA&orderby_dir=desc&orderby_second=Name&orderby_dir_second=asc" % (bref_playerID, start_date, end_date, bat_hand)
	print(url)
	# NOTE: Just need to handle and exception here for the case where there's no data
	return(url)

# Description: Function scrapes the matchup page on Baseball Reference
# Params: (str) url - Url of pitcher page as created by the brooks_player_url function
# Return: (pandas df) pitches_df - trajectory and movement table as a pandas dataframe
def scrape_table(url):
	dfs = pd.read_html(url, flavor = 'bs4', header = 0) # scrapes all dataframes from url
	matchups_df = dfs[0].dropna(axis=0, thresh=4) # takes first dataframe and cleans it
	matchups_df = matchups_df.rename(columns={'2B': 'doubles', '3B': 'triples'})
	return(matchups_df)

# Description: Function writes Matchup data to a file
# Params: (file) f_obj - file to be written to, 
#         (int) pitcher_mlb_id - mlb id of pitcher, (str) pitcher_hand - Handedness of pitcher, 
#		  (str) batter_hand - Handedness of batter, (pandas df) data - data as scraped in scrape_table
# Return: None
def write_off_data(f_obj, pitcher_mlb_id, pitcher_hand, batter_hand, data):
	data = data.query('Name != "Name"') # Removes bad rows without data
	num_matchups = data.shape[0]
	for i in range(0, num_matchups):
		data_line = data.iloc[i]
		batter_bref_name = data_line.Name
		batter_info = players_df.query('PLAYERNAME == "%s" | MLBNAME == "%s" | FANGRAPHSNAME == "%s" | CBSNAME == "%s"' % (batter_bref_name, batter_bref_name, batter_bref_name, batter_bref_name))
		if not batter_info.empty:
			# Only writes off data for players in the player database
			data_line = "%d, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % (batter_info.iloc[0].MLBID, pitcher_mlb_id, pitcher_hand, batter_hand, data_line.PA, data_line.H, data_line.doubles, data_line.triples, data_line.HR, data_line.BB, data_line.SO, data_line.IBB, data_line.HBP)
			f_obj.write(data_line)

out_file = open("../data/batter_pitcher_matchups_test.csv", "w")
out_file.write("batter_id, pitcher_id, pitcher_hand, batter_hand, appearances, hits, doubles, triples, home_runs, walks, strikeouts, intentional_walks, hit_batters\n")
# Years for the training data for matchups
start_time = "2016"
end_time = "2017"
pitchers_df = players_df.query('POS == "P"')
batter_sides = ["R", "L"]

for index, row in pitchers_df.iterrows():
	for batter_side in batter_sides:
		matchup_url = bref_matchups_url(row.BREFID, start_time, end_time, batter_side, row.THROWS)
		try:
			matchup_data = scrape_table(matchup_url)
			write_off_data(out_file, row.MLBID, row.THROWS, batter_side, matchup_data)
		except:
			# This is just a generic exception for all cases where the url request doesn't go through
			continue

out_file.close()
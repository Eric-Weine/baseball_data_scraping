import pandas as pd
import bs4 as bs

# Overview: This code scrapes pitcher splits from fangraphs

# Description: Function creates the URL for a pitcher's fangraphs splits page
# Params: (str) fg_playerID - fangraphs id of player, (str) year - desired year of splits
# Return: (str) url that points to the correct player page
def fg_player_url(fg_playerID, year):
	url = "http://www.fangraphs.com/statsplits.aspx?playerid=%s&season=%s" % (fg_playerID, year)
	return(url)

# Description: Function scrapes the splits of the specified splits page
# Params: (str) url - Url of pitcher page as created by the fg_player_url function
# Return: (pandas df) Righty and lefty splits as a pandas dataframe
#					OR returns null if the pitcher did not have recorded splits for year in url
def scrape_splits(url):
	print(url)
	try:
		dfs = pd.read_html(url, flavor = 'bs4')
		for df in dfs:
			try:
				x = df.TBF
				df = df.rename(columns={'2B': 'doubles', '3B': 'triples'}) # rename columns that start w/ number for pandas syntax
				return(df)
			except AttributeError:
			# Because of the layout of the website many of the first dfs do not contain actual stats
			# Exceptions are caught until the dataframe with the actual stats is found
				continue
	except:
		# If the pitcher did not exist in the specified year, then an exception will be thrown
		return(None) # Return null value in this case

# Description: Function writes pitcher splits data to a file
# Params: (file) f_obj - file to be written to, (int) mlb_pitcher_id - mlb id of pitcher
#         (pandas df) df - data as scraped in scrape_table, (str) year - year of the splits
# Return: None
def write_off_table(f_obj, mlb_playerID, df, year):
	lefty_df = df.query('Handedness == "vs L"')
	if not lefty_df.empty:
		insert_tuple = (mlb_playerID, year, "L", lefty_df.iloc[0].TBF, lefty_df.iloc[0].H, lefty_df.iloc[0].doubles,\
 				lefty_df.iloc[0].triples, lefty_df.iloc[0].HR, lefty_df.iloc[0].BB, lefty_df.iloc[0].SO, \ 
				lefty_df.iloc[0].IBB, lefty_df.iloc[0].HBP)
		insert_str = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % insert_tuple
		f_obj.write(insert_str)
		print(insert_tuple)
	righty_df = df.query('Handedness == "vs R"')
	if not righty_df.empty:
		insert_tuple = (mlb_playerID, year, "R", righty_df.iloc[0].TBF, righty_df.iloc[0].H, \
				righty_df.iloc[0].doubles, righty_df.iloc[0].triples, righty_df.iloc[0].HR, \
				righty_df.iloc[0].BB, righty_df.iloc[0].SO, righty_df.iloc[0].IBB, righty_df.iloc[0].HBP)
		print(insert_tuple)
		insert_str = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n" % insert_tuple
		f_obj.write(insert_str)

out_file = open("../data/pitcher_splits.csv", "w")
out_file.write("player_id, year, batter_hand, batters_faced, hits, doubles, triples, home_runs, walks, strikeouts, intentional_walks, hit_batters\n") # write column names
pitchers_df = pd.read_csv("../data/player_directory_full.csv", encoding='latin-1').query('POS == "P"')
years = ["2014", "2015"]

for index, row in pitchers_df.iterrows():
	if not pd.isnull(row.IDFANGRAPHS):
		for year in years:
			pitcher_url = fg_player_url(row.IDFANGRAPHS, year)
			pitcher_data = scrape_splits(pitcher_url)
			if pitcher_data is None:
				# case where the exception is thrown because there is no data
				continue
			else:
				write_off_table(out_file, row.MLBID, pitcher_data, year)

out_file.close()

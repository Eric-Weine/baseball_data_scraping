import pandas as pd
import bs4 as bs

# Overview: This code scrapes trajectory and movement data from the Brook's Baseball Website

# Description: Function creates the URL for a pitcher's trajectory and movement page on the brooks baseball website
# Params: (int) mlb_playerID - mlb id of player, (str) start_date - first date of scraping as mm/dd/yyyy,
# 		  (str) end_date - last date of scraping as mm/dd/yyyy, (str) bat_hand - hand of opp. batter as "R" or "L"
# Return: (str) url that points to the correct player page
def brooks_player_url(mlb_playerID, start_date, end_date, bat_hand):
	url = "http://www.brooksbaseball.net/tabs.php?player=%d&p_hand=-1&ppos=-1&cn=200&compType=none&gFilt=&time=month&minmax=ci&var=traj&s_type=2&startDate=%s&endDate=%s&balls=-1&strikes=-1&b_hand=%s" % (mlb_playerID, start_date, end_date, bat_hand)
	return(url)

# Description: Function scrapes the trajectory and movement table on Brook's Baseball
# Params: (str) url - Url of pitcher page as created by the brooks_player_url function
# Return: (pandas df) pitches_df - trajectory and movement table as a pandas dataframe
def scrape_table(url):
	dfs = pd.read_html(url, flavor = 'bs4', header = 0) # scrapes all dataframes from url
	pitches_df = dfs[0].dropna(axis=0, thresh=4) # takes first dataframe and cleans it
	pitches_df.columns = ["pitch_type", "pitch_count", "frequency", "speed", "h_mov", "v_mov", "h_rel", "v_rel"]
	return(pitches_df)

# Description: Function writes trajectory and movement data to a file
# Params: (file) f_obj - file to be written to, 
#         (int) mlb_playerID - mlb id of pitcher, (str) pitcher_hand - Handedness of pitcher, 
#		  (str) batter_hand - Handedness of batter, (pandas df) data - data as scraped in scrape_table
# Return: None
def write_off_data(f_obj, mlb_playerID, pitcher_hand, batter_hand, data):
	num_pitches = data.shape[0]
	for i in range(0, num_pitches):
		data_line = "%d, %s, %s, %s, %d, %f, %f, %f, %f, %f\n" % (mlb_playerID, pitcher_hand, batter_hand, data.pitch_type[i], data.pitch_count[i], data.speed[i], data.h_mov[i], data.v_mov[i], data.h_rel[i], data.v_rel[i])
		f_obj.write(data_line)

out_file = open("../data/brooks_pitcher_info.csv", "w")
out_file.write("player_id, pitcher_hand, batter_hand, pitch_type, count, speed, h_mov, v_mov, h_rel, v_rel\n") # write column names
start_time = "03/21/2015"
end_time = "11/02/2016"
pitchers_df = pd.read_csv("../data/player_directory.csv", encoding='latin-1').query('mlb_pos == "P"')
batter_sides = ["R", "L"]

for index, row in pitchers_df.iterrows():
	for batter_side in batter_sides:
		pitcher_url = brooks_player_url(row.mlb_id, start_time, end_time, batter_side)
		pitcher_data = scrape_table(pitcher_url)
		write_off_data(out_file, row.mlb_id, row.throws, batter_side, pitcher_data)

out_file.close()

# auto_bid
Subpub Bid Automation Project

## Code Structure

As of January 2021, the code is structured into 3 main components:

1. The ruleset.py module. This describes a ruleset object, the default values for which are contained in ruless.csv.

2. The autobid.py module. This contains the basic formulas and logic for generating bids.

3. The app.py module. This contains everything needed to run a flask app which performs the autobid task on a csv upload. The tasks the app does are as follows:

	A. The user can change the rulset parameters from a web form. Otherwise default values are used and sent in a post request. The run_autobid() function runs on           the input csv, which is converted to a pandas dataframe under the hood. The things run_autobid does are as follows:
	
    	i. Once the parameters are set, the data is grouped by geo to calculate baseline bids using the functions in autobid.py. Then the individual subpubs are compared against these baselines using the Ruleset.
		
    	ii. The calculations found in autobid.py are performed on the csv according to some fields selected in the initial request (e.g. bid calculation method) and the result is saved to an S3 bucket. 
		
		iii. The new dataframe is output.
		
	B. The user is redirected to a download page and prompted to login with OAuth if their credentials are not stored in the current session.
	
	C. On the dowload page, a dropdown is populated with all objects in the S3 bucket. The user can download the selected document in the browser.

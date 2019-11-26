# auto_bid
Subpub Bid Automation Project

## Directions for use:

1. Be sure Python3 is installed. You can do so by first installing Homebrew in Terminal. Copy paste the following:

`ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
`brew install python`

Verify this worked by copy-pasting the following:
`python3 -V`

2. Install pandas.
`sudo pip3 install pandas`

3. Run the script. You will need to provide the path of the input file and it will automatically output to the same location as auto_bid.py. You will also need a rulesheet formatted like the example in the repo.
`python3 auto_bid.py -i <path_to_input_csv> -r <rules_csv>`

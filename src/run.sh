# Move to working dir
cd /Users/ldaviesi/Documents/code/TCG-Card-Tracker/src/

# Backup database
cp tcgcardtracker.db ../Backups/tcgcardtracker$(date +%Y-%m-%d).db

# Update prices, pipe to a run log
/Library/Frameworks/Python.framework/Versions/3.9/bin/python3 TCGCardTracker.py update > ../Logs/run_log$(date +%Y-%m-%d).txt

# Delete backups and logs longer than 14 days
find ../Logs/ -type f -mtime +14 -exec rm {} \;
find ../Backups/ -type f -mtime +14 -exec rm {} \;
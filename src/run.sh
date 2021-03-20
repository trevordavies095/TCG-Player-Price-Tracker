cd /Users/ldaviesi/Documents/code/TCG-Card-Tracker/src/
cp tcgcardtracker.db ../Backups/tcgcardtracker$(date +%Y-%m-%d).db
/Library/Frameworks/Python.framework/Versions/3.9/bin/python3 TCGCardTracker.py update > ../Logs/run_log$(date +%Y-%m-%d).txt
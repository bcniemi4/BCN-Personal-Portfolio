##Reddit metadata post aggregator
## BCN 060226

import re
from collections import Counter, defaultdict
import pandas as pd
import praw

#Reddit Credentials

reddit = praw.Reddit(
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    user_agent = "DrugMonitorV0.1 by YOUR_USERNAME"
)

#Settings

SUBREDDIT = "ENTER_SUBREDDIT_HERE"
POST_LIMIT = 500
KNOWN_DRUGS = {
    "fentanyl": ["fentanyl", "fent"]
    "xylazine": ["xylazine, tranq"]
    "medetomidine": ["medetomidine"]
    "methamphetamine": ["meth, methamphetamine"]
    "cocaine": ["cocaine", "crack"]
    "benzodiazepines": ["benzo", "benzodiazepine", "alprazolam", "xanax", "bromazolam"]
    "nitazenes": ["nitazene", "protonitazene", "metonitazene", "etonitazene"]
}

STOPWORDS = {
    "the", "and", "or", "but", "with", "from", "this", "that", 
    "what", "when", "where", "how", "why", "are", "was", "were",
    "have", "has", "had", "for", "you", "your", "about", "into", "over",
    "under", "new", "report", "reports", "found", "try", "tried", "possible", "looking"
}

#List Storage

known_counts = Counter()
unknown_counts = Counter()
all_aliases = {
    alias.lower()
    for aliases in KNOWN_DRUGS.values()
    for alias in aliases
}

#Post reading

subreddit = reddit.subreddit(SUBREDDIT)
for submission in subreddit.new(limit = POST_LIMIT)
    title = submission.title
    text = title.lower()

    #Known Drug Matching

    for drug, aliases in KNOWN_DRUGS.items()
        matched = False
        for alias in aliases:
            pattern = rf"\b {re.escape(alias.lower())}\b"
            if re.search(pattern, text):
                known_counts[drug] +=1
                known_titles[drug].append(title)
                matched = True
                break

    #Unknown Drug Term Discovery

    words = re.findall( 
        r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b",
        text
    )
    for word in words:
        if word in STOPWORDS:
            continue
        if word in all_aliases:
            continue
        if len(word) < 4 :
            continue
        unknown_counts[word] +=1
        unknown_titles[word].append(title)

#Output

print("\nKNOWN DRUG COUNTS")
print("=" * 40)

for drug, count in known_counts.most_common():
    print(f"{drug}: {count}")
print("\nPOSSIBLE NEW TERMS")
print("=" * 40)

for term, count in unknown_counts.most_common(25):
    print(f"{term}: {count}")

#Export

known_df = pd.DataFrame(
    known_counts.items(),
    columns = ["Drug", "Count"]
)
unknown_df = pd.DataFrame(
    unknown_counts.most_common(100),
    columns = ["Possible Drug", "Count"]
)
known_df.to_csv(
    "known_drugs_counts.csv",
    index = False
)
unknown_df.to_csv(
    "possible_drug_counts.csv"
    index = False
)
print("\nCSV files saved:")
print("known_drug_counts.csv")
print("candidate_terms.csv")
import re
from collections import Counter, defaultdict
import pandas as pd
import requests

SUBREDDIT = "drugs"   # no "r/"
POST_LIMIT = 100

KNOWN_DRUGS = {
    "fentanyl": ["fentanyl", "fent"],
    "xylazine": ["xylazine", "tranq"],
    "medetomidine": ["medetomidine"],
    "methamphetamine": ["meth", "methamphetamine"],
    "cocaine": ["cocaine", "crack"],
    "benzodiazepines": ["benzo", "benzodiazepine", "alprazolam", "xanax", "bromazolam"],
    "nitazenes": ["nitazene", "protonitazene", "metonitazene", "etonitazene"],
}

STOPWORDS = {
    "the", "and", "or", "but", "with", "from", "this", "that",
    "what", "when", "where", "how", "why", "are", "was", "were",
    "have", "has", "had", "for", "you", "your", "about", "into",
    "over", "under", "new", "report", "reports", "found", "try",
    "tried", "possible", "looking", "drug", "drugs"
}

url = f"https://old.reddit.com/r/{SUBREDDIT}/new.json?limit={POST_LIMIT}"

headers = {
    "User-Agent": "Windows:DrugMonitor:0.1 by u/CaptNemo4"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

data = response.json()
posts = data["data"]["children"]

known_counts = Counter()
unknown_counts = Counter()
known_titles = defaultdict(list)
unknown_titles = defaultdict(list)

all_aliases = {
    alias.lower()
    for aliases in KNOWN_DRUGS.values()
    for alias in aliases
}

for post in posts:
    title = post["data"]["title"]
    text = title.lower()

    for drug, aliases in KNOWN_DRUGS.items():
        for alias in aliases:
            pattern = rf"\b{re.escape(alias.lower())}\b"
            if re.search(pattern, text):
                known_counts[drug] += 1
                known_titles[drug].append(title)
                break

    words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9-]{2,}\b", text)

    for word in words:
        if word in STOPWORDS:
            continue
        if word in all_aliases:
            continue
        if len(word) < 4:
            continue

        unknown_counts[word] += 1
        unknown_titles[word].append(title)

print("\nKNOWN DRUG COUNTS")
print("=" * 40)

for drug, count in known_counts.most_common():
    print(f"{drug}: {count}")

print("\nPOSSIBLE NEW TERMS")
print("=" * 40)

for term, count in unknown_counts.most_common(25):
    print(f"{term}: {count}")

known_df = pd.DataFrame(
    known_counts.most_common(),
    columns=["Drug", "Count"]
)

unknown_df = pd.DataFrame(
    unknown_counts.most_common(100),
    columns=["Possible Drug", "Count"]
)

known_df.to_csv("known_drug_counts.csv", index=False)
unknown_df.to_csv("possible_drug_counts.csv", index=False)

print("\nCSV files saved:")
print("known_drug_counts.csv")
print("possible_drug_counts.csv")
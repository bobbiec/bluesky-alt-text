
import pandas as pd
import re
import sys
import warnings
warnings.filterwarnings('ignore')

df = None  # global

def initial_analysis(image_posts_path='../image_posts.csv'):
    global df
    # Load the data
    print(f"Loading {image_posts_path}...")
    df = pd.read_csv(image_posts_path)
    print(f"Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"Columns: {list(df.columns)}\n")

    # Display first few rows
    print("First 25 rows:")
    print(df.head(25))
    print()

    # Basic info about the dataset
    print("Raw dataset info:")
    print_basic_info(df)
    return df

def print_basic_info(df):
    print(f"Total posts: {len(df):,}")
    print(f"Unique URIs: {df['at_uri'].nunique():,}")
    print(f"Duplicate URIs: {len(df) - df['at_uri'].nunique():,} ({((len(df) - df['at_uri'].nunique()) / len(df) * 100):.2f}% of total)")
    print(f"Posts with captions: {df['image_caption'].notna().sum():,} ({df['image_caption'].notna().mean()*100:.2f}% of total)")
    print(f"Posts without captions: {df['image_caption'].isna().sum():,} ({df['image_caption'].isna().mean()*100:.2f}% of total)")

    posts_with_captions = df[df['image_caption'].notna()]
    unique_uris_with_captions = posts_with_captions['at_uri'].nunique()
    print(f"Unique URIs for posts with captions: {unique_uris_with_captions:,} ({unique_uris_with_captions / df['at_uri'].nunique() * 100:.2f}% of URIs)")
    print()
    return

bluesky_uri_pattern = re.compile(r'at://(did:plc:[^/]+)/app\.bsky\.feed\.post/([^,]+)')

def parse_at_uri(uri):
    """Parse an AT URI to extract components"""
    try:
        if pd.isna(uri):
            return {'did': None, 'post_id': None, 'is_valid': False}

        # Pattern: at://did:plc:xxxxx/app.bsky.feed.post/xxxxx
        match = bluesky_uri_pattern.match(uri)
        if match:
            return {
                'did': match.group(1),
                'post_id': match.group(2),
                'is_valid': True
            }
        else:
            return {'did': None, 'post_id': None, 'is_valid': False}
    except:
        return {'did': None, 'post_id': None, 'is_valid': False}

def parse_dataset_bluesky_uris():
    global df

    # Parse URIs for full df
    print("Parsing AT URIs to DID and post ID...")
    parsed_uris = df['at_uri'].apply(parse_at_uri)

    # Extract parsed components
    df['did'] = [p['did'] for p in parsed_uris]
    df['is_valid'] = [p['is_valid'] for p in parsed_uris]
    print("Done\n")
    return

def filtered_analysis(bot_info_path='../top_100_users.csv'):
    global df
    print("Filtering out bots")

    # Load and parse top_100_users.csv
    print(f"Loading {bot_info_path}...")
    top_users_df = pd.read_csv(bot_info_path)
    print(f"Loaded {len(top_users_df)} users from {bot_info_path}")
    bot_mask = top_users_df['Clear bot?'].isin(['Yes', 'Likely'])
    bot_dids = set(top_users_df[bot_mask]['DID'])
    print(f"Identified {len(bot_dids)} clear bot DIDs to exclude")

    # Filter out bot DIDs
    filtered_df = df[~df['did'].isin(bot_dids)]
    print(f"Original dataset: {len(df)} posts")
    print(f"Filtered dataset (excluding bots): {len(filtered_df)} posts")
    print(f"Excluded {len(df) - len(filtered_df)} posts from bots\n")

    print("Filtered dataset info (top bots removed):")
    print_basic_info(filtered_df)

def top_users():
    """User analysis (DID distribution)"""
    global df
    print("User analysis:\n")

    valid = df[df['is_valid']]

    did_counts = valid['did'].value_counts()

    print(f"Unique users (DIDs): {len(did_counts):,}")
    print(f"Average posts per user: {did_counts.mean():.2f}")
    print(f"Median posts per user: {did_counts.median():.2f}")
    print(f"Max posts by single user: {did_counts.max():,}")
    print(f"Min posts by single user: {did_counts.min():,}")

    print("\nTop 100 users by post count:")
    print(did_counts.head(100))
    print()

def at_uri_to_bsky_url(at_uri):
    d = parse_at_uri(at_uri)
    return f"https://bsky.app/profile/{d['did']}/post/{d['post_id']}"

if __name__ == '__main__':
    image_posts_path = sys.argv[1]
    bot_info_path = sys.argv[2]
    initial_analysis(image_posts_path)
    parse_dataset_bluesky_uris()
    # top_users()
    filtered_analysis(bot_info_path)

import argparse
from query import query

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str)
    args = parser.parse_args()
    query_text = args.query
    response = query(query_text)

if __name__ == "__main__":
    main()
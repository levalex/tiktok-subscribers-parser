import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a file argument.')
    parser.add_argument('input_filename', type=str, help='The input file.')

    args = parser.parse_args()


    with open(args.input_filename, 'r') as input_file:
        accounts = [x.strip() for x in input_file.readlines()]

        query = "INSERT INTO accounts (username, is_follower, is_queued) VALUES\n"

        accounts_query = []
        for account in accounts:
            accounts_query.append(f"('{account}', TRUE, TRUE)")

        query += ','.join(accounts_query)
        query += "ON CONFLICT (username) DO NOTHING;"

        for account in accounts:
            query += f"UPDATE accounts SET is_follower = TRUE, is_queued = TRUE WHERE username = '{account}';"
    
        print(query)

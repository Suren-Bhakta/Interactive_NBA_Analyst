import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.max_columns', None)

def search_players(name):
    url = f"https://www.basketball-reference.com/search/search.fcgi?search={name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    players = soup.select('.search-item-name a')

    results = []
    for player in players:
        full_name = player.text
        player_url = f"https://www.basketball-reference.com{player['href']}"
        results.append({"Name": full_name, "URL": player_url})

    return results

def get_player_stats(player_url):
    response = requests.get(player_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'per_game'})

    headers = [header.text for header in table.select('thead th')]
    rows = []
    for row in table.select('tbody tr'):
        row_data = [data.text for data in row.select('th, td')]
        rows.append(row_data)

    df = pd.DataFrame(rows, columns=headers)
    df = df[df['Season'].notnull()]
    df = df.rename(columns={'Season': 'Season', 'PTS': 'Points', 'TRB': 'Rebounds', 'AST': 'Assists', 'FG%': 'Field Goal %'})

    df = df.reset_index(drop=True)

    # Convert 'Season' column to numeric
    df['Season'] = df['Season'].apply(lambda x: x.split("-")[0])
    df['Season'] = pd.to_numeric(df['Season'], errors='coerce')

    return df

def analyze_player_stats(player_stats, selected_stats):
    for stat in selected_stats:
        average_stat = calculate_average(player_stats, stat)
        print(f"Career Average {stat}: {average_stat:.2f}")

def visualize_player_stats(player_stats, selected_stats):
    for stat in selected_stats:
        player_stats[stat] = pd.to_numeric(player_stats[stat], errors='coerce')
        player_stats["Season"] = pd.to_numeric(player_stats["Season"], errors='coerce')
        plt.plot(player_stats["Season"], player_stats[stat])
        plt.xlabel("Season")
        plt.ylabel(stat)
        plt.title(f"Player's {stat} Over Seasons")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

def calculate_average(player_stats, column_name):
    player_stats[column_name] = pd.to_numeric(player_stats[column_name], errors='coerce')
    average = player_stats[column_name].mean()
    return average

def main():
    print("Welcome to NBA Player Stats Analyzer!")
    num_players = int(input("Enter the number of players you want to view: "))
    player_stats_list = []

    for _ in range(num_players):
        player_name = input("Enter the name (or partial name) of the player you want to search for: ")
        search_results = search_players(player_name)

        if not search_results:
            print("No players found.")
            continue

        print("Search Results:")
        for i, result in enumerate(search_results):
            print(f"{i+1}. {result['Name']}")

        player_index = int(input("Enter the index of the player you want to analyze: ")) - 1

        if player_index < 0 or player_index >= len(search_results):
            print("Invalid player index.")
            continue

        selected_player = search_results[player_index]
        player_stats = get_player_stats(selected_player["URL"])
        player_stats_list.append({"Name": selected_player["Name"], "Stats": player_stats})
        selected_stats = input("Enter the stats you want to see from this list: MP, FG, FGA, Field Goal %, 3P, 3PA, 3P%, 2P, 2PA, 2P%, eFG%, FT, FTA, FT%, ORB, DRB, Rebounds, Assists, STL, BLK, TOV, PF, Points (separated by commas with no space): ").split(",")
        selected_stats2 = ['Season', 'Age', 'Tm', 'Pos', 'G']
        selected_stats2.extend(selected_stats)
        print("\nPlayer Career Stats:")

        new_df = player_stats[selected_stats2]
        print(new_df)
        analyze_player_stats(player_stats, selected_stats)
        visualize_player_stats(player_stats, selected_stats)

    if len(player_stats_list) > 1:
        compare_players = input("Do you want to compare player statistics? (y/n): ")
        if compare_players.lower() == "y":
            while True:
                print("Player Comparison:")
                for i, player in enumerate(player_stats_list):
                    print(f"{i+1}. {player['Name']}")
                player_indices = input("Enter the indices of the players you want to compare (separated by commas): ").split(",")
                player_indices = [int(idx.strip()) - 1 for idx in player_indices if idx.strip().isdigit()]

                if len(player_indices) < 2 or any(idx < 0 or idx >= len(player_stats_list) for idx in player_indices):
                    print("Invalid player indices. Please try again.")
                    continue

                selected_players = [player_stats_list[idx] for idx in player_indices]
                selected_stats = input("Enter the stats you want to compare (separated by commas with no space): ").split(",")

                print("Player Comparison Results:")
                for stat in selected_stats:
                    print(f"\n{stat} Comparison:")
                    for player in selected_players:
                        #print(player_stats[selected_stats])
                        average_stat = calculate_average(player['Stats'], stat)
                        print(f"{player['Name']}: {average_stat:.2f}")

                break

    print("Thank you for using NBA Player Stats Analyzer!")


if __name__ == "__main__":
    main()

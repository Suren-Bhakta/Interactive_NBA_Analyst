import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt

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
    df = df[['Season', 'PTS', 'TRB', 'AST', 'FG%']]
    df.columns = ['Season', 'Points', 'Rebounds', 'Assists', 'Field Goal %']
    df = df.reset_index(drop=True)

    # Convert 'Season' column to numeric
    df['Season'] = df['Season'].apply(lambda x: x.split("-")[0])
    df['Season'] = pd.to_numeric(df['Season'], errors='coerce')

    return df

def analyze_player_stats(player_stats):
    # Example analysis: Calculate average points per game
    player_stats["Points"] = pd.to_numeric(player_stats["Points"], errors='coerce')
    average_pts = player_stats["Points"].mean()
    print(f"Average Points Per Game: {average_pts}")

def visualize_player_stats(player_stats):
    # Example visualization: Line chart for points per game over the seasons
    player_stats["Points"] = pd.to_numeric(player_stats["Points"], errors='coerce')
    player_stats["Season"] = pd.to_numeric(player_stats["Season"], errors='coerce')
    plt.plot(player_stats["Season"], player_stats["Points"])
    plt.xlabel("Season")
    plt.ylabel("Points Per Game")
    plt.title("Player's Points Per Game Over Seasons")
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent label overlapping
    plt.show()

def analyze_fg_percentage(player_stats):
    # Calculate average field goal percentage
    player_stats["Field Goal %"] = pd.to_numeric(player_stats["Field Goal %"], errors='coerce')
    average_fg_percentage = player_stats["Field Goal %"].mean()
    print(f"Average Field Goal Percentage: {average_fg_percentage}%")

def visualize_fg_percentage(player_stats):
    # Line chart for field goal percentage over the seasons
    player_stats["Field Goal %"] = pd.to_numeric(player_stats["Field Goal %"], errors='coerce')
    player_stats["Season"] = pd.to_numeric(player_stats["Season"], errors='coerce')
    plt.plot(player_stats["Season"], player_stats["Field Goal %"])
    plt.xlabel("Season")
    plt.ylabel("Field Goal Percentage")
    plt.title("Player's Field Goal Percentage Over Seasons")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()


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

        print("\nPlayer Career Stats:")
        print(player_stats)

        analyze_player_stats(player_stats)
        visualize_player_stats(player_stats)
        analyze_fg_percentage(player_stats)
        visualize_fg_percentage(player_stats)

    print("Thank you for using NBA Player Stats Analyzer!")

if __name__ == "__main__":
    main()

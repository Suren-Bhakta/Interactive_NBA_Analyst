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


def select_player(player_names):
    print("Select a player:")
    for i, player in enumerate(player_names):
        print(f"{i+1}. {player['Name']}")

    selection = input("> ")
    try:
        player_index = int(selection) - 1
        selected_player = player_names[player_index]
        return selected_player
    except (ValueError, IndexError):
        print("Invalid input. Please try again.")
        return None


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

    # Update column names for comparison and calculation
    df = df.rename(columns={'PTS': 'Points', 'TRB': 'Rebounds', 'AST': 'Assists', 'FG%': 'Field Goal %'})

    # Convert 'Season' column to numeric
    df['Season'] = df['Season'].apply(lambda x: x.split("-")[0])
    df['Season'] = pd.to_numeric(df['Season'], errors='coerce')

    # Calculate Player Efficiency Rating (PER)
    df['PER'] = ((df['Points'].astype(float) + df['Rebounds'].astype(float) + df['Assists'].astype(float)) / df['Season']) * 100

    return df


def compare_players(player_stats):
    pd.set_option('display.max_columns', None)  # Display all columns in the DataFrame

    print("Enter the numbers corresponding to the players you want to compare (separated by commas):")
    for i, stats in enumerate(player_stats):
        print(f"{i+1}. {stats.columns[0]}")

    player_nums = input("> ").split(",")

    players_to_compare = []
    for num in player_nums:
        try:
            player_index = int(num.strip()) - 1
            players_to_compare.append(player_stats[player_index])
        except (IndexError, ValueError):
            print("Invalid input. Skipping player.")

    if len(players_to_compare) < 2:
        print("Please select at least two players for comparison.")
        return

    # Combine player stats into a single DataFrame
    combined_stats = pd.concat(players_to_compare, keys=[stats.columns[0] for stats in players_to_compare])

    # Display player stats comparison
    print("\nPlayer Stats Comparison:")
    for column in combined_stats.columns:
        print(f"{column:<12}", end="")
        for player in players_to_compare:
            print(f"{player[column][0]:<12}", end="")
        print()

    print()



def analyze_player_stats(player_stats):
    # Example analysis: Calculate average points per game
    player_stats["Points"] = pd.to_numeric(player_stats["Points"], errors='coerce')
    average_pts = player_stats["Points"].mean()
    print(f"Average Points Per Game: {average_pts}")


from tabulate import tabulate

def visualize_player_stats(stats):
    # Format player stats as a table
    table = []
    for column, value in stats.items():
        table.append([column, value])

    # Print player stats table
    print("Player Stats:")
    print(tabulate(table, headers=["Stat", "Value"], tablefmt="fancy_grid"))
    # Example visualization: Line chart for points per game over the seasons
    stats["Points"] = pd.to_numeric(stats["Points"], errors='coerce')
    stats["Season"] = pd.to_numeric(stats["Season"], errors='coerce')
    plt.plot(stats["Season"], stats["Points"])
    plt.xlabel("Season")
    plt.ylabel("Points Per Game")
    plt.title("Player's Points Per Game Over Seasons")
    plt.xticks(rotation=90)  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust layout to prevent label overlapping
    plt.show()



def export_player_stats(player_stats, filename):
    player_stats.to_csv(filename, index=False)
    print(f"Player stats exported to {filename} successfully.")


def main():
    print("NBA Player Comparison Tool")
    print("Enter the number of players you want to compare:")
    num_players = int(input("> "))
    player_stats = []

    for i in range(num_players):
        print(f"Enter the name of player {i+1}:")
        player_name = input("> ")
        player_names = search_players(player_name)

        if len(player_names) > 0:
            selected_player = select_player(player_names)
            if selected_player:
                player_stats.append(get_player_stats(selected_player["URL"]))
        else:
            print(f"No player found with the name {player_name}.")

    if len(player_stats) == 1:
        analyze_player_stats(player_stats[0])
        visualize_player_stats(player_stats[0])
    elif len(player_stats) > 1:
        compare_players(player_stats)
        visualize_player_stats(player_stats)
    else:
        print("Please select at least one player for comparison.")


if __name__ == "__main__":
    main()

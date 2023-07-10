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
        career_average = calculate_average(player_stats, stat)
        print(f"Career Average {stat}: {career_average:.2f}")

        last_season_stat = player_stats[stat].iloc[-1]
        if pd.notnull(last_season_stat):
            print(f"Last Season {stat}: {last_season_stat:.2f}")
        else:
            print("Last Season Stat: Not available")

        print("\n")


def visualize_player_stats(player_stats, selected_stats):
    for stat in selected_stats:
        fig, ax = plt.subplots()  # Create a new figure and axes for each stat

        player_stats[stat] = pd.to_numeric(player_stats[stat], errors='coerce')
        player_stats["Season"] = pd.to_numeric(player_stats["Season"], errors='coerce')
        ax.plot(player_stats["Season"], player_stats[stat], label=stat)

        # Calculate career average
        career_average = calculate_average(player_stats, stat)
        career_average_line = [career_average] * len(player_stats["Season"])
        ax.plot(player_stats["Season"], career_average_line, label=f"Career Avg - {stat}", linestyle='--')

        ax.set_xlabel("Season")
        ax.set_ylabel("Stat Value")
        ax.set_title(f"Player's {stat} Over Seasons")
        ax.legend()
        ax.set_xticklabels(ax.get_xticks(), rotation=90)  # Set the rotation of tick labels
        plt.tight_layout()
        plt.show()




def compare_player_stats(player_stats_list, selected_stats):
    seasons = player_stats_list[0]["Stats"]["Season"]
    plt.figure(figsize=(10, 6))

    for player_stats in player_stats_list:
        player_name = player_stats["Name"]
        stats = player_stats["Stats"]

        for stat in selected_stats:
            stats[stat] = pd.to_numeric(stats[stat], errors='coerce')

            # Create a DataFrame with all seasons and NaN values
            missing_seasons = list(set(seasons) - set(stats["Season"]))
            missing_data = pd.DataFrame(index=missing_seasons, columns=stats.columns)
            missing_data["Season"] = missing_data.index
            stats = pd.concat([stats, missing_data])

            # Sort the stats based on season
            stats = stats.sort_values("Season")

            plt.plot(stats["Season"], stats[stat], label=f"{player_name} - {stat}")

    plt.xlabel("Season")
    plt.ylabel("Stat Value")
    plt.title("Player Comparison")
    plt.legend()
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

        show_graph = input("Do you want to see the graph for this player? (y/n): ")
        if show_graph.lower() == "y":
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

                while True:
                    selected_stat = input("Enter the stat you want to compare (or 'q' to exit): ")
                    if selected_stat.lower() == "q":
                        break

                    print("Player Comparison Results:")
                    print(f"\n{selected_stat} Comparison:")
                    for player in selected_players:
                        average_stat = calculate_average(player['Stats'], selected_stat)
                        career_average = calculate_average(player['Stats'], selected_stat)
                        print(f"{player['Name']}: {average_stat:.2f} (Career Average: {career_average:.2f})")

                        last_season_stat = player['Stats'][selected_stat].iloc[-1]
                        if pd.notnull(last_season_stat):
                            print(f"Last Season {selected_stat}: {last_season_stat:.2f}")
                        else:
                            print("Last Season Stat: Not available")

                        print("\n")

                    compare_player_stats(selected_players, [selected_stat])

                continue_comparison = input("Do you want to continue comparing stats? (y/n): ")
                if continue_comparison.lower() != "y":
                    break



    print("Thank you for using NBA Player Stats Analyzer!")

if __name__ == "__main__":
    main()



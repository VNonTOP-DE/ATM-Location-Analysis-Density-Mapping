import pandas as pd
from sqlalchemy import create_engine
from database_config import MYSQLConfig
import folium
from geopy.distance import great_circle
import numpy as np
from pyproj import Transformer


def get_all_atm_names():
    """Fetch and display all unique ATM names from the database"""
    # Initialize MYSQLConfig
    config = MYSQLConfig(
        host='localhost',
        port=3306,
        user='root',
        password='123',
        table='ATM_DATA',
        database='ATM_DATA'
    )

    # Create SQLAlchemy engine
    url = f"mysql+mysqlconnector://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}"
    engine = create_engine(url)

    # Fetch all unique ATM names with counts
    query = """
    SELECT NAME, COUNT(*) as count 
    FROM ATM_DATA 
    GROUP BY NAME 
    ORDER BY count DESC, NAME
    """
    df = pd.read_sql(query, engine)

    print("Available ATM Names:")
    print("-" * 50)
    for idx, row in df.iterrows():
        print(f"{idx + 1:2d}. {row['NAME']} ({row['count']} locations)")

    return df, engine


def visualize_and_calculate_distances(atm_name, engine):
    """Create map and calculate distances for specified ATM name"""

    # Fetch all ATM data for the specified name
    # Escape single quotes in the name to prevent SQL issues
    escaped_name = atm_name.replace("'", "''")
    query = f"SELECT * FROM ATM_DATA WHERE NAME = '{escaped_name}'"
    df = pd.read_sql(query, engine)

    print(f"\nFound {len(df)} '{atm_name}' ATMs.")

    if len(df) == 0:
        print("No matching ATMs found.")
        return

    # Check coordinate ranges to confirm projection
    print("\nCoordinate ranges before conversion:")
    print(df[['X', 'Y']].describe())

    # Convert coordinates from NAD83 State Plane Maryland FIPS 1900 (EPSG:2893) to WGS84 (EPSG:4326)
    transformer = Transformer.from_crs("EPSG:2893", "EPSG:4326", always_xy=True)
    df['longitude'], df['latitude'] = transformer.transform(df['X'].values, df['Y'].values)

    # Verify converted coordinates
    print("\nConverted coordinate ranges (latitude/longitude):")
    print(df[['latitude', 'longitude']].describe())

    # Check for invalid coordinates
    invalid_coords = df[df['latitude'].isna() | df['longitude'].isna() |
                        (df['latitude'] < -90) | (df['latitude'] > 90) |
                        (df['longitude'] < -180) | (df['longitude'] > 180)]
    if not invalid_coords.empty:
        print(f"Warning: Found {len(invalid_coords)} invalid coordinates:")
        print(invalid_coords[['NAME', 'ADDRESS', 'X', 'Y']])
        # Filter out invalid coordinates
        df = df[df['latitude'].notna() & df['longitude'].notna() &
                (df['latitude'].between(-90, 90)) & (df['longitude'].between(-180, 180))]

    if len(df) < 2:
        print("Not enough valid ATMs to calculate distances.")
        if len(df) == 1:
            print("Creating map with single ATM location...")
        else:
            return

    # Calculate pairwise distances (in km) using Haversine formula
    if len(df) >= 2:
        coords = df[['latitude', 'longitude']].values  # [lat, lon] for great_circle
        distances = []
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                try:
                    dist = great_circle(coords[i], coords[j]).km
                    distances.append(dist)
                except ValueError as e:
                    print(f"Error calculating distance between points {i} and {j}: {e}")
                    continue

        if distances:
            shortest_dist = min(distances)
            farthest_dist = max(distances)
            avg_dist = np.mean(distances)
            print(f"\nDistance Statistics:")
            print(f"Shortest distance between ATMs: {shortest_dist:.2f} km ({shortest_dist * 0.621371:.2f} miles)")
            print(f"Farthest distance between ATMs: {farthest_dist:.2f} km ({farthest_dist * 0.621371:.2f} miles)")
            print(f"Average distance between ATMs: {avg_dist:.2f} km ({avg_dist * 0.621371:.2f} miles)")
        else:
            print("No valid distances calculated.")

    # Create interactive map with folium
    map_center = [df['latitude'].mean(), df['longitude'].mean()]  # Center on mean coordinates

    # Adjust zoom level based on the spread of locations
    lat_range = df['latitude'].max() - df['latitude'].min()
    lon_range = df['longitude'].max() - df['longitude'].min()
    max_range = max(lat_range, lon_range)

    if max_range > 0.1:
        zoom_start = 10
    elif max_range > 0.05:
        zoom_start = 11
    elif max_range > 0.01:
        zoom_start = 12
    else:
        zoom_start = 13

    atm_map = folium.Map(location=map_center, zoom_start=zoom_start)

    # Add markers for each ATM
    for idx, row in df.iterrows():
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"<b>{row['NAME']}</b><br>{row['ADDRESS']}<br>ZIP: {row['ZIPCODE']}<br>Ward: {row['WARD']}",
                icon=folium.Icon(color='blue', icon='university', prefix='fa')
            ).add_to(atm_map)

    # Create filename based on ATM name
    filename = f"{atm_name.replace('/', '_').replace(' ', '_').lower()}_atm_map.html"

    # Save the map to an HTML file
    atm_map.save(filename)
    print(f"\nMap saved as '{filename}'. Open it in a browser to view.")


def main():
    """Main function to run the interactive ATM mapper"""
    try:
        # Get all ATM names
        names_df, engine = get_all_atm_names()

        print("\n" + "=" * 50)

        while True:
            try:
                choice = input("\nEnter the number of the ATM you want to map (or 'q' to quit): ").strip()

                if choice.lower() == 'q':
                    print("Goodbye!")
                    break

                choice_num = int(choice)

                if 1 <= choice_num <= len(names_df):
                    selected_atm = names_df.iloc[choice_num - 1]['NAME']
                    print(f"\nYou selected: {selected_atm}")
                    visualize_and_calculate_distances(selected_atm, engine)

                    # Ask if user wants to continue
                    continue_choice = input("\nDo you want to map another ATM? (y/n): ").strip().lower()
                    if continue_choice != 'y':
                        print("Goodbye!")
                        break
                else:
                    print(f"Please enter a number between 1 and {len(names_df)}")

            except ValueError:
                print("Please enter a valid number or 'q' to quit")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the database connection
        if 'engine' in locals():
            engine.dispose()


if __name__ == "__main__":
    main()
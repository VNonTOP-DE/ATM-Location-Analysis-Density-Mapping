import pandas as pd
from sqlalchemy import create_engine
from database_config import MYSQLConfig
import folium
from folium import plugins
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyproj import Transformer


class ATMDensityAnalyzer:
    def __init__(self):
        """Initialize the ATM Density Analyzer"""
        self.config = MYSQLConfig(
            host='localhost',
            port=3306,
            user='root',
            password='123',
            table='ATM_DATA',
            database='ATM_DATA'
        )

        # Create SQLAlchemy engine
        url = f"mysql+mysqlconnector://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"
        self.engine = create_engine(url)

    def load_data(self):
        """Load ATM data from database"""
        query = "SELECT * FROM ATM_DATA WHERE WARD IS NOT NULL AND ZIPCODE IS NOT NULL"
        self.df = pd.read_sql(query, self.engine)
        print(f"Loaded {len(self.df)} ATM records with valid ward and ZIP code data.")

    def convert_coordinates(self):
        """Convert coordinates from State Plane to WGS84"""
        transformer = Transformer.from_crs("EPSG:2893", "EPSG:4326", always_xy=True)
        self.df['longitude'], self.df['latitude'] = transformer.transform(
            self.df['X'].values, self.df['Y'].values
        )

        # Filter out invalid coordinates
        valid_coords = (
                self.df['latitude'].notna() & self.df['longitude'].notna() &
                (self.df['latitude'].between(-90, 90)) &
                (self.df['longitude'].between(-180, 180))
        )
        self.df = self.df[valid_coords]
        print(f"Valid coordinates for {len(self.df)} ATMs after coordinate conversion.")

    def analyze_ward_density(self):
        """Analyze ATM density by ward"""
        ward_stats = self.df.groupby('WARD').agg({
            'NAME': 'count',
            'latitude': 'mean',
            'longitude': 'mean'
        }).rename(columns={'NAME': 'atm_count'}).reset_index()

        # Calculate density rank
        ward_stats['density_rank'] = ward_stats['atm_count'].rank(ascending=False)
        ward_stats = ward_stats.sort_values('atm_count', ascending=False)

        print("\n" + "=" * 50)
        print("ATM DENSITY BY WARD")
        print("=" * 50)
        print(f"{'Ward':<6} {'ATM Count':<12} {'Density Rank':<14} {'Center Lat':<12} {'Center Lon':<12}")
        print("-" * 68)

        for _, row in ward_stats.iterrows():
            print(f"{int(row['WARD']):<6} {int(row['atm_count']):<12} {int(row['density_rank']):<14} "
                  f"{row['latitude']:.6f} {row['longitude']:.6f}")

        return ward_stats

    def analyze_zip_density(self):
        """Analyze ATM density by ZIP code"""
        zip_stats = self.df.groupby('ZIPCODE').agg({
            'NAME': 'count',
            'latitude': 'mean',
            'longitude': 'mean'
        }).rename(columns={'NAME': 'atm_count'}).reset_index()

        # Calculate density rank
        zip_stats['density_rank'] = zip_stats['atm_count'].rank(ascending=False)
        zip_stats = zip_stats.sort_values('atm_count', ascending=False)

        print("\n" + "=" * 50)
        print("ATM DENSITY BY ZIP CODE")
        print("=" * 50)
        print("Top 15 ZIP codes by ATM count:")
        print(f"{'ZIP Code':<10} {'ATM Count':<12} {'Density Rank':<14} {'Center Lat':<12} {'Center Lon':<12}")
        print("-" * 74)

        for _, row in zip_stats.head(15).iterrows():
            print(f"{int(row['ZIPCODE']):<10} {int(row['atm_count']):<12} {int(row['density_rank']):<14} "
                  f"{row['latitude']:.6f} {row['longitude']:.6f}")

        return zip_stats

    def analyze_atm_types_by_area(self):
        """Analyze ATM types distribution by ward and ZIP"""
        print("\n" + "=" * 50)
        print("ATM TYPES BY WARD")
        print("=" * 50)

        ward_atm_types = self.df.groupby(['WARD', 'NAME']).size().unstack(fill_value=0)
        print(ward_atm_types.head(10))

        print("\n" + "=" * 50)
        print("ATM TYPES BY ZIP CODE (Top 10 ZIPs)")
        print("=" * 50)

        # Get top 10 ZIP codes by ATM count
        top_zips = self.df['ZIPCODE'].value_counts().head(10).index
        zip_atm_types = self.df[self.df['ZIPCODE'].isin(top_zips)].groupby(['ZIPCODE', 'NAME']).size().unstack(
            fill_value=0)
        print(zip_atm_types)

        return ward_atm_types, zip_atm_types

    def create_density_heatmap(self, ward_stats, zip_stats):
        """Create interactive heatmap showing ATM density"""
        # Center map on DC area
        center_lat = self.df['latitude'].mean()
        center_lon = self.df['longitude'].mean()

        # Create base map
        density_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles='OpenStreetMap'
        )

        # Add ATM markers with different colors based on density
        for _, row in self.df.iterrows():
            ward = int(row['WARD'])
            ward_density = ward_stats[ward_stats['WARD'] == ward]['atm_count'].iloc[0]

            # Color coding based on ward density
            if ward_density >= 50:
                color = 'red'
                icon = 'fire'
            elif ward_density >= 30:
                color = 'orange'
                icon = 'star'
            elif ward_density >= 20:
                color = 'yellow'
                icon = 'info-sign'
            elif ward_density >= 10:
                color = 'blue'
                icon = 'ok-sign'
            else:
                color = 'green'
                icon = 'minus-sign'

            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"<b>{row['NAME']}</b><br>"
                      f"Address: {row['ADDRESS']}<br>"
                      f"Ward: {ward} ({ward_density} ATMs)<br>"
                      f"ZIP: {int(row['ZIPCODE'])}",
                icon=folium.Icon(color=color, icon=icon),
                tooltip=f"Ward {ward}: {ward_density} ATMs"
            ).add_to(density_map)

        # Add heat map layer
        heat_data = [[row['latitude'], row['longitude']] for _, row in self.df.iterrows()]
        plugins.HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(density_map)

        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>ATM Density by Ward</b></p>
        <p><i class="fa fa-fire" style="color:red"></i> 50+ ATMs</p>
        <p><i class="fa fa-star" style="color:orange"></i> 30-49 ATMs</p>
        <p><i class="fa fa-info-circle" style="color:gold"></i> 20-29 ATMs</p>
        <p><i class="fa fa-ok-circle" style="color:blue"></i> 10-19 ATMs</p>
        <p><i class="fa fa-minus-circle" style="color:green"></i> <10 ATMs</p>
        </div>
        '''
        density_map.get_root().html.add_child(folium.Element(legend_html))

        # Save the map
        density_map.save('atm_density_heatmap.html')
        print(f"\nDensity heatmap saved as 'atm_density_heatmap.html'")

    def generate_summary_statistics(self, ward_stats, zip_stats):
        """Generate summary statistics"""
        print("\n" + "=" * 50)
        print("SUMMARY STATISTICS")
        print("=" * 50)

        total_atms = len(self.df)
        total_wards = len(ward_stats)
        total_zips = len(zip_stats)

        print(f"Total ATMs: {total_atms}")
        print(f"Total Wards: {total_wards}")
        print(f"Total ZIP Codes: {total_zips}")
        print(f"Average ATMs per Ward: {total_atms / total_wards:.1f}")
        print(f"Average ATMs per ZIP: {total_atms / total_zips:.1f}")

        print(f"\nHighest density Ward: {ward_stats.iloc[0]['WARD']} ({ward_stats.iloc[0]['atm_count']} ATMs)")
        print(f"Lowest density Ward: {ward_stats.iloc[-1]['WARD']} ({ward_stats.iloc[-1]['atm_count']} ATMs)")

        print(f"\nHighest density ZIP: {zip_stats.iloc[0]['ZIPCODE']} ({zip_stats.iloc[0]['atm_count']} ATMs)")
        print(f"Lowest density ZIP: {zip_stats.iloc[-1]['ZIPCODE']} ({zip_stats.iloc[-1]['atm_count']} ATMs)")

    def run_analysis(self):
        """Run complete density analysis"""
        print("Starting ATM Density Analysis...")
        print("=" * 50)

        # Load and prepare data
        self.load_data()
        self.convert_coordinates()

        # Perform analyses
        ward_stats = self.analyze_ward_density()
        zip_stats = self.analyze_zip_density()
        ward_atm_types, zip_atm_types = self.analyze_atm_types_by_area()

        # Generate visualizations
        self.create_density_heatmap(ward_stats, zip_stats)

        # Generate summary
        self.generate_summary_statistics(ward_stats, zip_stats)

        print("\n" + "=" * 50)
        print("Analysis complete! Check the generated files:")
        print("- atm_density_heatmap.html: Interactive density map")
        print("=" * 50)

        # Close database connection
        self.engine.dispose()

        return ward_stats, zip_stats, ward_atm_types, zip_atm_types


def main():
    """Main function to run ATM density analysis"""
    try:
        analyzer = ATMDensityAnalyzer()
        ward_stats, zip_stats, ward_atm_types, zip_atm_types = analyzer.run_analysis()
        return ward_stats, zip_stats, ward_atm_types, zip_atm_types

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return None, None, None, None


if __name__ == "__main__":
    main()
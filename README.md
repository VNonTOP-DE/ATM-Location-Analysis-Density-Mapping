# ATM-Location-Analysis-Density-Mapping
A comprehensive Python-based tool for analyzing and visualizing ATM locations, calculating spatial distributions, and generating interactive density maps. This project processes ATM data from CSV files, stores it in MySQL databases, and provides powerful geospatial analysis capabilities.

🌟 Features
1. Interactive ATM Mapper

Browse all available ATM types in your database
Select specific ATM brands for detailed analysis
Generate interactive maps with location markers
Calculate distance statistics between ATM locations (shortest, farthest, average)
Export maps as standalone HTML files

2. ATM Density Analyzer

Analyze ATM distribution across geographical wards
Calculate ATM density by ZIP code
Generate comprehensive density statistics
Create interactive heatmaps with color-coded density markers
View ATM brand distribution by area
Identify high and low-density zones

3. Geospatial Capabilities

Automatic coordinate transformation (NAD83 State Plane to WGS84)
Haversine distance calculations
Invalid coordinate filtering
Folium-based interactive mapping with heatmap overlays

📊 Sample Outputs

Interactive Maps: Color-coded markers showing ATM locations with detailed popups
Density Heatmaps: Visual representation of ATM concentration across regions
Statistical Reports: Console output with detailed ward and ZIP code analysis
Distance Metrics: Calculate proximity between ATM locations

🚀 Getting Started
Prerequisites

Python 3.8 or higher
MySQL Server
Required Python packages (see requirements.txt)

Installation

Clone the repository:

bashgit clone https://github.com/yourusername/atm-location-analysis.git
cd atm-location-analysis

Install required packages:

bashpip install -r requirements.txt

Set up MySQL database:

bash# Create database (credentials in database_config.py)
mysql -u root -p
CREATE DATABASE ATM_DATA;

Configure database connection:
Edit database_config.py with your MySQL credentials:

pythonhost='localhost'
port=3306
user='root'
password='your_password'
database='ATM_DATA'
Usage
Basic Usage
Run the main script to load data and perform density analysis:
bashpython main.py
Interactive ATM Mapper
To explore specific ATM brands and create custom maps:
bashpython interactive_atm_mapper.py
The interactive mapper will:

Display all available ATM brands with location counts
Prompt you to select an ATM type
Generate an interactive map with distance statistics
Save the map as an HTML file

ATM Density Analysis
To run only the density analysis:
bashpython ATM_analyze.py
This will generate:

Console output with ward and ZIP code statistics
atm_density_heatmap.html - Interactive density visualization

📁 Project Structure
atm-location-analysis/
│
├── main.py                     # Main entry point - loads data and runs analysis
├── ATM_analyze.py              # ATM density analyzer class
├── visualize_atms.py           # Interactive mapping tool for specific ATM types
├── database_config.py          # Database configuration
├── database_connect.py         # Database connection manager
├── schema_manager.py           # Database schema creation
├── schema.sql                  # Sql Schema 
├── ATM_Banking.csv             # Sample ATM data (replace with your data)
└── requirements.txt            # Python dependencies

🗺️ Data Format
The project expects CSV data with the following columns:
<img width="577" height="269" alt="image" src="https://github.com/user-attachments/assets/7d049a36-c890-493e-84fe-641ac10e50e9" />

📈 Analysis Output Examples
Ward Density Analysis
==================================================
ATM DENSITY BY WARD
==================================================
Ward   ATM Count    Density Rank   Center Lat   Center Lon
--------------------------------------------------------------------
2      87           1              38.916234    -77.043567
6      62           2              38.895123    -76.995432
1      54           3              38.932145    -77.056789
...
Distance Statistics
Distance Statistics:
Shortest distance between ATMs: 0.15 km (0.09 miles)
Farthest distance between ATMs: 12.34 km (7.67 miles)
Average distance between ATMs: 2.56 km (1.59 miles)
🛠️ Technologies Used

Python 3.x - Core programming language
Pandas - Data manipulation and analysis
SQLAlchemy - Database ORM and connection management
MySQL - Data storage and querying
Folium - Interactive mapping and visualization
PyProj - Coordinate transformation
Geopy - Distance calculations (Haversine formula)
NumPy - Numerical computations

🎯 Use Cases

Urban Planning: Analyze ATM accessibility across neighborhoods
Financial Services: Identify underserved areas for ATM placement
Market Research: Study competitor ATM distributions
Geographic Analysis: Understand spatial patterns of banking infrastructure
Business Intelligence: Make data-driven decisions for ATM network expansion

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Fork the project
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.
👤 Author
VNonTOP

GitHub: @VNonTOP-DE
Email: tuannguyenworkde@Gmail.com
🙏 Acknowledgments

ATM data source: https://data.gov/
Coordinate system information: EPSG.io
Mapping library: Folium community

📞 Support
If you have any questions or run into issues, please open an issue on GitHub or contact the maintainer.

Happy Mapping! 🗺️📍

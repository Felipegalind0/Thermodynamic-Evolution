# Final script to generate Figure 3 for the Theory of Thermodynamic Evolution

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import adjustText
import warnings

# Suppress potential future warnings from seaborn
warnings.filterwarnings("ignore", "is_categorical_dtype")
warnings.filterwarnings("ignore", "use_inf_as_na")


def create_energy_gdp_plot():
    """
    Fetches data from Our World in Data and generates a scatter plot
    of Energy Use vs. GDP per capita for all countries.
    """
    print("Fetching data from Our World in Data...")
    try:
        # Use a reliable dataset from Our World in Data
        url = 'https://raw.githubusercontent.com/owid/energy-data/refs/heads/master/owid-energy-data.csv'
        df = pd.read_csv(url)
        print("Data fetched successfully.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Please check your internet connection.")
        return

    # --- Data Cleaning and Preparation ---
    # Filter for the most recent year with comprehensive data (e.g., 2021)
    year = 2021
    df_year = df[df['year'] == year].copy()

    # Select the necessary columns and drop rows with missing values
    df_year = df_year[['country', 'iso_code', 'gdp', 'energy_per_capita', 'population']].dropna()

    # Calculate GDP per capita from total GDP and population
    df_year = df_year[df_year['population'] > 0]
    df_year['gdp_per_capita'] = df_year['gdp'] / df_year['population']

    # Filter out countries with very low GDP or energy use for plotting clarity
    df_year = df_year[(df_year['gdp_per_capita'] > 100) & (df_year['energy_per_capita'] > 100)]

    # Clean up column names for easier access
    df_year = df_year.rename(columns={'gdp_per_capita': 'GDP_per_capita', 'energy_per_capita': 'Energy_use_per_capita'})

    # Remove non-country aggregate entries
    aggregates = ['World', 'Asia', 'Africa', 'Europe', 'North America', 'South America', 'Oceania',
                  'Upper-middle-income countries', 'Lower-middle-income countries',
                  'Low-income countries', 'High-income countries']
    df_year = df_year[~df_year['country'].isin(aggregates)]

    # --- Plotting ---
    print("Generating plot...")
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(16, 10))

    # Create the scatter plot with bubble size proportional to population
    # and color mapped to GDP per capita
    sns.scatterplot(data=df_year, x='GDP_per_capita', y='Energy_use_per_capita',
                    ax=ax, alpha=0.7, s=np.sqrt(df_year['population']) / 15,
                    hue=np.log10(df_year['GDP_per_capita']),
                    palette='viridis', legend=None)

    # Set scales to logarithmic for clarity
    ax.set_xscale('log')
    ax.set_yscale('log')

    # Set titles, labels, and grid for a professional look
    ax.set_title(f'Figure 3: The Energy-Economy Correlation ({year})', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('GDP per Capita (constant 2017 international $) - Logarithmic Scale', fontsize=14)
    ax.set_ylabel('Energy Use per Capita (kWh) - Logarithmic Scale', fontsize=14)
    ax.grid(True, which="both", ls="--", linewidth=0.5)

    # --- Annotations ---
    countries_to_label = [
        'USA', 'CHN', 'DEU', 'JPN', 'IND', 'NGA', 'QAT', 
        'NOR', 'CHE', 'SGP', 'ETH', 'RUS', 'BRA', 'ZAF'
    ]

    texts = []
    for country_code in countries_to_label:
        if country_code in df_year['iso_code'].values:
            country_data = df_year[df_year['iso_code'] == country_code].iloc[0]
            x = country_data['GDP_per_capita']
            y = country_data['Energy_use_per_capita']
            texts.append(ax.text(x, y, country_data['country'], fontsize=11))

    if texts:
        adjustText.adjust_text(texts, arrowprops=dict(arrowstyle='->', color='black', lw=0.5))

    # --- Finalization ---
    plt.tight_layout()
    output_filename = 'Figure_3_Energy_Economy_Correlation.png'
    plt.savefig(output_filename, format='png', dpi=300)
    print(f"Plot successfully saved as '{output_filename}'")
    # plt.show()  # Uncomment to display the plot when running interactively


if __name__ == '__main__':
    create_energy_gdp_plot()

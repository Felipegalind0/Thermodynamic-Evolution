# Final, data-driven script to generate Figure 4 for the Theory of Thermodynamic Evolution

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def create_wealth_footprint_plot_data_driven():
    """
    Downloads, processes, and plots carbon footprint data by income percentile
    from the World Inequality Database (WID.world).
    """
    print("Fetching data from the World Inequality Database (WID.world)...")
    
    # --- Data Fetching ---
    try:
        # URL for per-capita carbon footprint data by percentile
        emissions_url = 'https://wid.world/data/export-full/emissg_p_i_ZS/all/all/all/all/all/all/all/all/all/all/2019/all/all/all/all/all/all/all/?separator=csv&decimal=point'
        
        # Download the data. We use a more robust method with headers.
        headers = {'User-Agent': 'Mozilla/5.0'}
        import requests
        from io import StringIO
        
        req = requests.get(emissions_url, headers=headers)
        req.raise_for_status() # Will raise an error if the download fails
        
        # The WID data has some descriptive text at the top we need to skip
        # Find the line where the actual data starts
        lines = req.text.splitlines()
        data_start_line = 0
        for i, line in enumerate(lines):
            if line.startswith('"Country"'):
                data_start_line = i
                break
        
        # Read the data into pandas
        df_emissions = pd.read_csv(StringIO('\n'.join(lines[data_start_line:])), sep=';')
        
        print("Data fetched successfully.")

    except Exception as e:
        print(f"Error fetching data: {e}")
        print("Could not retrieve data from the URL. Please check your internet connection and the link's validity.")
        return

    # --- Data Processing ---
    print("Processing data...")
    
    # Filter for the 'World' data
    df_world = df_emissions[df_emissions['Country'] == 'World'].copy()

    # The 'Percentile' column is like 'p0p50', 'p90p100', etc.
    # The 'Value' column is the tonnes of CO2e per capita
    
    # We need to find the values for the percentiles we care about.
    # WID provides data in ranges (e.g., p0p50 is the bottom 50%).
    data_map = {
        'Bottom 50%': 'p0p50',
        'Middle 40%': 'p50p90',
        'Top 10%': 'p90p100',
        'Top 1%': 'p99p100',
    }

    results = {}
    for label, code in data_map.items():
        value = df_world[df_world['Percentile'] == code]['Value'].iloc[0]
        results[label] = float(value)

    # WID does not provide finer percentiles directly in this dataset,
    # so we will use the highly-cited Oxfam/SEI data for the top brackets for rigor.
    # This combines the strengths of both sources.
    results['Top 0.1%'] = 467 # Source: Oxfam/SEI report "Carbon Billionaires"
    results['Top 0.01%'] = 2531 # Source: Oxfam/SEI report "Carbon Billionaires"

    # Re-order for plotting
    categories = list(results.keys())[::-1]
    values = list(results.values())[::-1]

    # --- Plotting ---
    print("Generating plot...")
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(16, 10))

    colors = plt.cm.plasma(np.linspace(0.3, 0.9, len(categories)))
    bars = ax.barh(categories, values, color=colors, log=True)
    
    ax.set_xscale('log')
    ax.set_yticks([])

    for i, bar in enumerate(bars):
        width = bar.get_width()
        category = bar.get_y() + bar.get_height() / 2
        ax.text(0.5, category, f' {categories[i]}', va='center', ha='left', fontsize=14, fontweight='bold')
        ax.text(width * 1.1, category, f'{width:,.1f}', va='center', ha='left', fontsize=14)

    ax.set_title('Figure 4: The Dissipative Footprint of Wealth (Global Consumption Emissions)', fontsize=20, fontweight='bold', pad=20)
    ax.set_xlabel('Average Annual Carbon Footprint per Capita (Tonnes CO₂e) - Logarithmic Scale', fontsize=14)
    ax.set_ylabel('Global Income Group', fontsize=14)

    from matplotlib.ticker import LogFormatter, LogLocator
    ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
    ax.xaxis.set_major_formatter(LogFormatter(base=10.0, labelOnlyBase=False))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    caption = (
        "Figure 4 illustrates the disparity in commanded dissipation across global income groups. \n"
        "Data is sourced from the World Inequality Database (WID.world, 2019) and supplemented with data for top emitters from Oxfam/SEI reports. \n"
        "The values represent average per-capita consumption-based emissions, a proxy for an individual's total dissipative footprint within the global economy."
    )
    fig.text(0.5, 0.01, caption, ha='center', fontsize=12, style='italic', wrap=True)

    plt.tight_layout(rect=[0, 0.1, 1, 0.95])
    
    output_filename = 'Figure_4_Dissipative_Footprint_of_Wealth.pdf'
    plt.savefig(output_filename, format='pdf', dpi=300)
    
    print(f"Plot successfully saved as '{output_filename}'")

if __name__ == '__main__':
    create_wealth_footprint_plot_data_driven()
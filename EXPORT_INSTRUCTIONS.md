# Investment Selection Tool - Export Instructions

## Files to Copy to New Replit Project

### Core Application Files
- `Home.py` - Main application entry point
- `app.py` - Alternative entry point (if needed)
- `pyproject.toml` - Project dependencies
- `replit.md` - Project documentation and preferences

### Application Pages
- `pages/1_Data_Import.py` - Data import functionality
- `pages/3_HUB24_Filter.py` - HUB24 platform filtering
- `pages/4_Formula_Filtering.py` - Custom formula filtering
- `pages/5_Data_Analysis.py` - Data analysis and visualization
- `pages/6_Recommended_Portfolio.py` - Portfolio management

### Utility Modules
- `utils/__init__.py` - Package initialization
- `utils/data_processor.py` - Data processing functions
- `utils/data_storage.py` - Session state management
- `utils/formula_engine.py` - Formula evaluation engine
- `utils/hub24_filter.py` - HUB24 filtering utilities
- `utils/visualization.py` - Chart and visualization functions

### Sample Data (Optional)
- `sample_data/example_format.csv` - Example data format
- `sample_data/investment_data_sample.csv` - Sample investment data

## Setup Instructions for New Replit Project

1. **Create New Replit Project**
   - Create a new Python project in Replit
   - Choose Python 3.11 as the runtime

2. **Copy Files**
   - Copy all files listed above to the new project
   - Maintain the same directory structure

3. **Install Dependencies**
   - The dependencies are already listed in `pyproject.toml`
   - Replit should automatically install them, or you can run:
     ```bash
     pip install streamlit pandas numpy plotly pypdf2 scipy trafilatura pickledb
     ```

4. **Configure Streamlit**
   - Create `.streamlit/config.toml` with the following content:
     ```toml
     [server]
     headless = true
     address = "0.0.0.0"
     port = 5000
     ```

5. **Set Up Run Command**
   - Configure the run command in Replit to:
     ```bash
     streamlit run Home.py --server.port 5000
     ```

## Key Features

- **Multi-page Streamlit interface** with flexible navigation
- **CSV data import and validation** with robust processing
- **HUB24 platform filtering** via PDF APIR code extraction
- **Custom formula engine** for investment filtering
- **Interactive data analysis** with category-based comparisons
- **Portfolio management** with selection and export capabilities
- **Comprehensive visualizations** including risk-return analysis

## Recent Improvements

- Fixed category averages to use filtered data instead of full dataset
- Improved comparison columns accuracy
- Enhanced data processing for missing values
- Updated visualization charts to reflect filtered data

## Notes

- The app is designed to work with investment data CSV files
- Ensure uploaded CSV files have the required columns (see example format)
- The app uses session state for data persistence within sessions
- All data processing excludes funds without 3-year performance data from averages
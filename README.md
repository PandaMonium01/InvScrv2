# Investment Selection Tool

A comprehensive Streamlit-based investment analysis and portfolio selection tool designed for financial advisors and investment professionals.

## Features

- **Multi-file CSV Data Import** - Import and combine multiple investment data files
- **HUB24 Platform Filtering** - Filter investments by platform availability via PDF processing
- **Custom Formula Engine** - Apply complex mathematical formulas for investment screening
- **Interactive Data Analysis** - Comprehensive analysis with category-based comparisons
- **Portfolio Management** - Build and manage recommended investment portfolios
- **Risk-Return Analysis** - Advanced visualizations and performance metrics
- **Export Capabilities** - Download filtered data and analysis results

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install streamlit pandas numpy plotly pypdf2 scipy trafilatura pickledb
   ```

2. **Run the Application**
   ```bash
   streamlit run Home.py --server.port 5000
   ```

3. **Access the Application**
   - Open your browser to `http://localhost:5000`
   - Navigate through the pages using the sidebar

## Application Pages

1. **Home** - Overview and navigation
2. **Data Import** - Upload and process CSV investment data
3. **HUB24 Filter** - Filter by platform availability
4. **Formula Filtering** - Apply custom investment screening formulas
5. **Data Analysis** - Analyze filtered data with visualizations
6. **Recommended Portfolio** - Build and manage investment portfolios

## Data Requirements

Investment data CSV files should include these columns:
- Name
- APIR Code
- Morningstar Category
- 3 Years Annualised (%)
- Investment Management Fee(%)
- Equity StyleBox™
- Morningstar Rating
- 3 Year Beta
- 3 Year Standard Deviation
- 3 Year Sharpe Ratio

## Key Improvements

- Category averages calculated from filtered data for accurate comparisons
- Robust data processing with proper handling of missing values
- Enhanced visualization charts reflecting current filtered dataset
- Comprehensive portfolio management with export capabilities

## Technical Architecture

- **Frontend**: Streamlit with multi-page navigation
- **Data Processing**: Pandas with custom validation and cleaning
- **Visualization**: Plotly for interactive charts
- **Formula Engine**: Secure expression evaluation for investment screening
- **State Management**: Streamlit session state for data persistence

## License

This project is configured for professional use in investment analysis and portfolio management.
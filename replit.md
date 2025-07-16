# Investment Selection Tool

## Overview

This is a Streamlit-based investment selection tool that helps users analyze and select investments based on custom criteria. The application provides a multi-page interface for importing investment data, filtering by platform availability (HUB24), applying custom formulas, analyzing data, and building recommended portfolios.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit - chosen for rapid prototyping and interactive data applications
- **Multi-page Structure**: Uses Streamlit's native page system with a main `Home.py` and multiple pages in the `pages/` directory
- **State Management**: Heavy reliance on Streamlit's session state for data persistence across pages
- **Interactive Components**: Forms, file uploads, data tables, and interactive charts

### Backend Architecture
- **Processing Logic**: Modular utility functions in the `utils/` package
- **Data Flow**: Pipeline-based processing from CSV import → filtering → analysis → portfolio creation
- **Formula Engine**: Custom expression evaluator for investment filtering
- **PDF Processing**: APIR code extraction from HUB24 platform documentation

## Key Components

### 1. Data Import System (`pages/1_Data_Import.py`)
- **Purpose**: Handle CSV file uploads and validation
- **Features**: Multi-file upload support, data validation, automatic combination of datasets
- **Requirements**: Expects specific columns including Name, APIR Code, Morningstar Category, performance metrics

### 2. HUB24 Platform Filter (`pages/3_HUB24_Filter.py`)
- **Purpose**: Filter investments available on the HUB24 platform
- **Method**: PDF parsing to extract APIR codes using regex patterns
- **Integration**: Cross-references extracted codes with imported investment data

### 3. Formula Filtering Engine (`pages/4_Formula_Filtering.py`)
- **Purpose**: Apply custom mathematical formulas to filter investments
- **Features**: 
  - Support for complex expressions using pandas operations
  - Variable aliasing (e.g., `return` for `3 Years Annualised (%)`)
  - Real-time formula validation and application
- **Safety**: Controlled execution environment for formula evaluation

### 4. Data Analysis (`pages/5_Data_Analysis.py`)
- **Purpose**: Visualize and analyze filtered investment data
- **Features**: Asset class charts, risk-return scatter plots, performance metrics
- **Portfolio Integration**: Allows adding investments to recommended portfolio

### 5. Portfolio Management (`pages/6_Recommended_Portfolio.py`)
- **Purpose**: Manage and export selected investment portfolios
- **Features**: Portfolio editing, comments, CSV export functionality

### 6. Assumptions (`pages/7_Assumptions.py`)
- **Purpose**: Document methodology and provide configurable strategic asset allocation settings
- **Features**: 
  - Interactive Strategic Asset Allocation table with 6 risk profiles and editable default values
  - **NEW**: Morningstar Category to Asset Class mapping table with dropdown selections
  - Configurable category mappings that serve as system defaults for portfolio allocation analysis

## Data Flow

1. **Data Import**: CSV files → validation → processing → session state storage
2. **HUB24 Filtering**: PDF upload → APIR code extraction → data filtering → filtered dataset
3. **Formula Filtering**: Custom formula → expression evaluation → further filtered dataset
4. **Analysis**: Filtered data → visualizations → individual investment selection
5. **Portfolio**: Selected investments → portfolio management → export capabilities

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations
- **PyPDF2**: PDF text extraction for APIR codes
- **Scipy**: Statistical calculations

### Data Storage
- **Session State**: Primary storage mechanism using Streamlit's session state
- **Pickle**: Serialization for larger datasets in session state
- **CSV**: Primary data import/export format

## Deployment Strategy

### Current Architecture
- **Platform**: Designed for Streamlit deployment (streamlit.io, local, or cloud)
- **State Management**: In-memory session state (non-persistent across sessions)
- **File Handling**: Temporary file processing, no permanent storage

### Scaling Considerations
- **Data Persistence**: Currently session-based, could benefit from database integration
- **Performance**: Large datasets handled through pickle serialization
- **Multi-user**: Each session is isolated, no shared state between users

### Key Architectural Decisions

1. **Streamlit Choice**: Selected for rapid development and built-in data handling capabilities
   - **Pros**: Fast development, built-in widgets, easy deployment
   - **Cons**: Limited customization, session-based state management

2. **Session State Storage**: Used for data persistence across pages
   - **Pros**: Simple implementation, no external dependencies
   - **Cons**: Data lost on session end, memory intensive for large datasets

3. **Modular Utilities**: Separated business logic into utility modules
   - **Pros**: Maintainable, testable, reusable code
   - **Cons**: Additional complexity for simple operations

4. **PDF Processing for APIR Codes**: Direct PDF parsing instead of manual entry
   - **Pros**: Automated, accurate, handles large lists
   - **Cons**: Dependent on PDF format consistency

5. **Formula Engine**: Custom expression evaluator for flexible filtering
   - **Pros**: Powerful, flexible, user-friendly
   - **Cons**: Security considerations, complexity in error handling

The application follows a traditional web application pattern with a focus on data processing workflows, making it suitable for financial analysis and investment selection tasks.
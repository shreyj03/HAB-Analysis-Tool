# HAB Analysis Tool

A command-line tool for tracking and analyzing Harmful Algal Blooms (HABs) using satellite imagery and machine learning.

## Overview

This tool uses [CyFi](https://cyfi.drivendata.org/) (Cyanobacteria Finder) to analyze Sentinel-2 satellite imagery and detect harmful algal blooms in small, inland water bodies. It provides automated detection, severity classification, and trend analysis to help water quality managers make informed decisions about public health warnings and resource allocation.

## Features

- **Satellite-based Analysis**: Uses Sentinel-2 imagery via CyFi's machine learning models
- **Automated Detection**: Identifies cyanobacteria blooms with density estimates (cells/mL)
- **WHO-based Severity Classification**: Low, moderate, and high risk levels
- **Trend Analysis**: Tracks bloom progression over time
- **Visualizations**: Creates charts showing bloom timeline and severity
- **Batch Processing**: Analyze multiple dates with a single command

## Quick Start

### Installation

**Prerequisites:**
- Python 3.10 or higher
- conda or pip package manager

**Step 1: Create Environment (Recommended)**
```bash
# Create a clean conda environment
conda create -n hab_analysis python=3.10 -y
conda activate hab_analysis
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

### Basic Usage

```bash
python hab_analysis.py \
  --lat 40.17988 \
  --lon -120.60624 \
  --start 2023-08-01 \
  --end 2023-08-31
```

**Output:**
```
======================================================================
HAB ANALYSIS
======================================================================
Location: (40.17988, -120.60624)
Period: 2023-08-01 to 2023-08-31
Interval: 7 days
Output directory: hab_analysis_20241201_143022

CYANOBACTERIA DENSITY (cells/mL)
----------------------------------------------------------------------
  Maximum:       87,543
  Mean:          23,456
  Minimum:        1,234

BLOOM ANALYSIS
----------------------------------------------------------------------
  ⚠️  MODERATE BLOOM DETECTED
      Peak: 87,543 cells/mL on 2023-08-15
```

## Command-Line Arguments

### Required Arguments
- `--lat` - Latitude of the water body (decimal degrees)
- `--lon` - Longitude of the water body (decimal degrees)
- `--start` - Start date in YYYY-MM-DD format
- `--end` - End date in YYYY-MM-DD format

### Optional Arguments
- `--interval` - Days between samples (default: 7)
  - Lower values = more detail but slower
  - Higher values = less detail but faster
- `--output` - Custom output directory (default: auto-generated timestamp)
- `--no-viz` - Skip chart generation

## Usage Examples

### Example 1: Weekly Analysis (Default)
```bash
python hab_analysis.py \
  --lat 42.5 \
  --lon -73.2 \
  --start 2023-06-01 \
  --end 2023-08-31
```

### Example 2: High-Resolution Analysis (Every 3 Days)
```bash
python hab_analysis.py \
  --lat 36.95959 \
  --lon -121.77068 \
  --start 2023-07-01 \
  --end 2023-08-31 \
  --interval 3
```

## Understanding the Output

### Severity Levels (WHO Guidelines)

| Level | Density (cells/mL) | Indicator | Risk |
|-------|-------------------|-----------|------|
| 🟢 Low | < 20,000 | Safe | Generally safe for recreation |
| 🟡 Moderate | 20,000 - 100,000 | Caution | May cause skin irritation, avoid swallowing water |
| 🔴 High | > 100,000 | Danger | Health risk, avoid all contact |

### Output Files

Each run creates a timestamped directory containing:

```
hab_analysis_20241201_143022/
├── input.csv              # Input coordinates and dates
├── preds.csv             # Predictions with density and severity
├── sentinel_metadata.csv # Satellite image metadata
└── analysis.png          # Visualization chart
```

## How It Works

1. **Date Generation**: Creates sample points at specified intervals
2. **Satellite Retrieval**: CyFi downloads Sentinel-2 imagery for each date/location
3. **ML Analysis**: Machine learning model predicts cyanobacteria density
4. **Classification**: Assigns severity levels based on WHO thresholds
5. **Trend Analysis**: Identifies increasing, decreasing, or stable patterns
6. **Visualization**: Generates charts showing bloom progression

## Troubleshooting

### "CyFi not found"
```bash
# Solution: Install CyFi
conda install -c conda-forge cyfi -y
# or
pip install cyfi
```

### "No valid satellite data found"
**Causes:**
- Too much cloud cover (> 5%)
- Recent dates without processed imagery
- Limited Sentinel-2 coverage

**Solutions:**
- Use 2023 or 2024 dates
- Expand date range
- Try different time periods

### Slow Performance
**Solutions:**
- Increase `--interval` (e.g., 10 or 14 days)
- Reduce date range
- First run is always slower (downloads data)

### Import Errors / Dependency Conflicts
**Solution:** Use a clean conda environment
```bash
conda create -n hab_analysis python=3.10 -y
conda activate hab_analysis
conda install -c conda-forge cyfi -y
pip install matplotlib
```

## Acknowledgments

This tool was built as a project for the **Justice Media Computational Journalism Co-Lab** (HUB XC 473) at Boston University under the guidance of **Professor Brooke Williams** and **Professor Anthony Chamberas**.

## References

### CyFi
- **Documentation**: https://cyfi.drivendata.org/
- **GitHub**: https://github.com/drivendataorg/cyfi
- **Paper**: Dorne, E., Wetstone, K., Cerquera, T. B., & Gupta, S. (2024). Cyanobacteria detection in small, inland water bodies with CyFi. *Proceedings of the 23rd Python in Science Conference*, 154–173. https://doi.org/10.25080/pdhk7238

### Sentinel-2
- **Mission Info**: https://sentinel.esa.int/web/sentinel/missions/sentinel-2

### WHO Guidelines
- **HAB Guidelines**: https://www.who.int/water_sanitation_health/bathing/algae.pdf

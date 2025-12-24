#!/usr/bin/env python3
"""
Simple HAB Analysis CLI using CyFi
Analyze harmful algal blooms for a location over a time period using CyFi
"""
import argparse
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys

def parse_date(date_str):
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print(f"Error: Invalid date format '{date_str}'. Use YYYY-MM-DD")
        sys.exit(1)

def generate_dates(start_date, end_date, interval_days):
    """Generate list of dates between start and end."""
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=interval_days)
    
    # Always include end date
    if dates[-1] != end_date:
        dates.append(end_date)
    
    return dates

def create_input_csv(lat, lon, dates, output_dir):
    """Create CyFi input CSV file."""
    data = {
        'latitude': [lat] * len(dates),
        'longitude': [lon] * len(dates),
        'date': [d.strftime('%Y-%m-%d') for d in dates]
    }
    df = pd.DataFrame(data)
    
    input_file = Path(output_dir) / 'input.csv'
    df.to_csv(input_file, index=False)
    
    print(f"Created input with {len(dates)} sample points")
    print(f"  From: {dates[0].strftime('%Y-%m-%d')}")
    print(f"  To:   {dates[-1].strftime('%Y-%m-%d')}")
    print(f"  Interval: {interval_days} days\n")
    
    return input_file

def run_cyfi(input_csv, output_dir):
    """Run CyFi predictions."""
    print("Running CyFi predictions...")
    print("(This may take a few minutes)\n")
    
    cmd = [
        'cyfi', 'predict',
        str(input_csv),
        '--keep-metadata',
        '-d', str(output_dir)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✓ CyFi completed successfully\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ CyFi failed:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("✗ CyFi not installed")
        print("\nInstall with:")
        print("  pip install cyfi")
        print("or")
        print("  conda install -c conda-forge cyfi")
        return False

def analyze_results(output_dir):
    """Analyze and display CyFi results."""
    preds_file = Path(output_dir) / 'preds.csv'
    
    if not preds_file.exists():
        print(f"Error: Predictions file not found")
        return None
    
    df = pd.read_csv(preds_file)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    print()
    
    # Basic info
    print(f"Location: ({df['latitude'].iloc[0]}, {df['longitude'].iloc[0]})")
    print(f"Period: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"Total samples: {len(df)}")
    print()
    
    # Density statistics
    print("CYANOBACTERIA DENSITY (cells/mL)")
    print("-" * 70)
    print(f"  Maximum:  {df['density_cells_per_ml'].max():>12,.0f}")
    print(f"  Mean:     {df['density_cells_per_ml'].mean():>12,.0f}")
    print(f"  Minimum:  {df['density_cells_per_ml'].min():>12,.0f}")
    print()
    
    # Severity distribution
    print("SEVERITY DISTRIBUTION")
    print("-" * 70)
    severity_counts = df['severity'].value_counts()
    total = len(df)
    
    for severity in ['low', 'moderate', 'high']:
        if severity in severity_counts:
            count = severity_counts[severity]
            pct = (count / total) * 100
            print(f"  {severity.capitalize():10} {count:3d} samples ({pct:5.1f}%)")
        else:
            print(f"  {severity.capitalize():10}   0 samples (  0.0%)")
    print()
    
    # Bloom detection
    print("BLOOM ANALYSIS")
    print("-" * 70)
    
    # Thresholds (WHO guidelines)
    moderate_threshold = 20000
    high_threshold = 100000
    
    moderate_blooms = df[df['density_cells_per_ml'] >= moderate_threshold]
    high_blooms = df[df['density_cells_per_ml'] >= high_threshold]
    
    if len(high_blooms) > 0:
        print(f"  ⚠️  HIGH RISK BLOOM DETECTED")
        print(f"      {len(high_blooms)} samples exceeded 100,000 cells/mL")
        peak = df.loc[df['density_cells_per_ml'].idxmax()]
        print(f"      Peak: {peak['density_cells_per_ml']:,.0f} cells/mL on {peak['date'].strftime('%Y-%m-%d')}")
    elif len(moderate_blooms) > 0:
        print(f"  ⚠️  MODERATE BLOOM DETECTED")
        print(f"      {len(moderate_blooms)} samples exceeded 20,000 cells/mL")
        peak = df.loc[df['density_cells_per_ml'].idxmax()]
        print(f"      Peak: {peak['density_cells_per_ml']:,.0f} cells/mL on {peak['date'].strftime('%Y-%m-%d')}")
    else:
        print(f"  ✓ No significant blooms detected")
        print(f"    All samples below 20,000 cells/mL threshold")
    print()
    
    # Timeline
    print("TIMELINE")
    print("-" * 70)
    for _, row in df.iterrows():
        date_str = row['date'].strftime('%Y-%m-%d')
        density = row['density_cells_per_ml']
        severity = row['severity']
        
        # Visual indicator
        if severity == 'low':
            indicator = '🟢'
        elif severity == 'moderate':
            indicator = '🟡'
        elif severity == 'high':
            indicator = '🔴'
        else:
            indicator = '⚪'
        
        print(f"  {date_str}  {indicator}  {severity:>10}  {density:>12,.0f} cells/mL")
    
    print()
    print("=" * 70)
    
    # Trend analysis
    print("\nTREND ANALYSIS")
    print("-" * 70)
    
    if len(df) >= 3:
        first_half = df.iloc[:len(df)//2]['density_cells_per_ml'].mean()
        second_half = df.iloc[len(df)//2:]['density_cells_per_ml'].mean()
        
        if second_half > first_half * 1.5:
            print("  📈 INCREASING TREND - Density rising over time period")
        elif second_half < first_half * 0.67:
            print("  📉 DECREASING TREND - Density declining over time period")
        else:
            print("  ➡️  STABLE - No strong trend detected")
    
    # Duration analysis
    if len(moderate_blooms) > 0:
        bloom_start = moderate_blooms.iloc[0]['date']
        bloom_end = moderate_blooms.iloc[-1]['date']
        duration = (bloom_end - bloom_start).days
        print(f"\nBLOOM DURATION")
        print(f"  Start: {bloom_start.strftime('%Y-%m-%d')}")
        print(f"  End:   {bloom_end.strftime('%Y-%m-%d')}")
        print(f"  Duration: {duration} days")
    
    print()
    
    return df

def create_simple_viz(df, output_dir):
    """Create a simple visualization."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
    except ImportError:
        return
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot density
    ax.plot(df['date'], df['density_cells_per_ml'], 
            marker='o', linewidth=2, markersize=8, color='#2E86AB')
    
    # Add threshold lines
    ax.axhline(y=20000, color='orange', linestyle='--', 
               linewidth=1.5, alpha=0.7, label='Moderate threshold (20k)')
    ax.axhline(y=100000, color='red', linestyle='--', 
               linewidth=1.5, alpha=0.7, label='High threshold (100k)')
    
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cyanobacteria Density (cells/mL)', fontsize=12, fontweight='bold')
    ax.set_title('Harmful Algal Bloom Analysis', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper right')
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    viz_file = Path(output_dir) / 'analysis.png'
    plt.savefig(viz_file, dpi=300, bbox_inches='tight')
    print(f"Visualization saved: {viz_file}")
    
    try:
        plt.show()
    except:
        pass

def main():
    parser = argparse.ArgumentParser(
        description='Analyze harmful algal blooms using satellite imagery',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python %(prog)s --lat 42.5 --lon -73.2 --start 2023-06-01 --end 2023-08-31
  
  This will:
    1. Generate predictions for the location every 7 days
    2. Run CyFi to analyze satellite imagery
    3. Display analysis of cyanobacteria density over time
    4. Create a visualization chart
        """
    )
    
    parser.add_argument('--lat', type=float, required=True,
                       help='Latitude of location')
    parser.add_argument('--lon', type=float, required=True,
                       help='Longitude of location')
    parser.add_argument('--start', required=True,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', required=True,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--interval', type=int, default=7,
                       help='Days between samples (default: 7)')
    parser.add_argument('--output', default=None,
                       help='Output directory (default: ./hab_analysis)')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization')
    
    args = parser.parse_args()
    
    # Parse dates
    start_date = parse_date(args.start)
    end_date = parse_date(args.end)
    
    if end_date < start_date:
        print("Error: End date must be after start date")
        sys.exit(1)
    
    # Create output directory with timestamp
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(f'./hab_analysis_{timestamp}')
    else:
        output_dir = Path(args.output)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("HAB ANALYSIS")
    print("=" * 70)
    print(f"Location: ({args.lat}, {args.lon})")
    print(f"Period: {args.start} to {args.end}")
    print(f"Interval: {args.interval} days")
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate dates
    global interval_days
    interval_days = args.interval
    dates = generate_dates(start_date, end_date, args.interval)
    
    # Create input
    input_csv = create_input_csv(args.lat, args.lon, dates, output_dir)
    
    # Run CyFi
    if not run_cyfi(input_csv, output_dir):
        sys.exit(1)
    
    # Analyze
    df = analyze_results(output_dir)
    
    # Visualize
    if df is not None and not args.no_viz:
        create_simple_viz(df, output_dir)
    
    print(f"\nResults saved to: {output_dir}")
    print(f"  - Predictions: preds.csv")
    print(f"  - Metadata: sentinel_metadata.csv")
    if not args.no_viz:
        print(f"  - Chart: analysis.png")
    print()

if __name__ == '__main__':
    main()

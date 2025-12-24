#!/usr/bin/env python3
"""
Demo showing what hab_analysis.py produces
"""
import pandas as pd
from datetime import datetime, timedelta
import random

print("=" * 70)
print("HAB ANALYSIS CLI - DEMO")
print("=" * 70)
print()

# Simulate command
print("Example command:")
print("  python hab_analysis.py --lat 42.5 --lon -73.2 --start 2023-06-01 --end 2023-08-31")
print()
print("=" * 70)
print("HAB ANALYSIS")
print("=" * 70)
print("Location: (42.5, -73.2)")
print("Period: 2023-06-01 to 2023-08-31")
print("Interval: 7 days")
print()

print("Created input with 14 sample points")
print("  From: 2023-06-01")
print("  To:   2023-08-31")
print("  Interval: 7 days")
print()

print("Running CyFi predictions...")
print("(This may take a few minutes)")
print()
print("✓ CyFi completed successfully")
print()

# Generate sample data
random.seed(42)
dates = []
start = datetime(2023, 6, 1)
for i in range(14):
    dates.append(start + timedelta(days=i*7))

densities = []
severities = []

for i, date in enumerate(dates):
    # Simulate bloom progression
    if i < 3:
        density = random.randint(1000, 5000)
        severity = 'low'
    elif i < 5:
        density = random.randint(15000, 25000)
        severity = 'moderate'
    elif i < 8:
        density = random.randint(50000, 90000)
        severity = 'moderate'
    elif i == 8:
        density = random.randint(80000, 120000)
        severity = 'high'
    elif i < 11:
        density = random.randint(30000, 50000)
        severity = 'moderate'
    else:
        density = random.randint(5000, 15000)
        severity = 'low'
    
    densities.append(density)
    severities.append(severity)

df = pd.DataFrame({
    'date': dates,
    'density_cells_per_ml': densities,
    'severity': severities
})

print("=" * 70)
print("ANALYSIS RESULTS")
print("=" * 70)
print()

print(f"Location: (42.5, -73.2)")
print(f"Period: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
print(f"Total samples: {len(df)}")
print()

print("CYANOBACTERIA DENSITY (cells/mL)")
print("-" * 70)
print(f"  Maximum:  {df['density_cells_per_ml'].max():>12,.0f}")
print(f"  Mean:     {df['density_cells_per_ml'].mean():>12,.0f}")
print(f"  Minimum:  {df['density_cells_per_ml'].min():>12,.0f}")
print()

print("SEVERITY DISTRIBUTION")
print("-" * 70)
severity_counts = df['severity'].value_counts()
total = len(df)

for severity in ['low', 'moderate', 'high']:
    if severity in severity_counts.index:
        count = severity_counts[severity]
        pct = (count / total) * 100
        print(f"  {severity.capitalize():10} {count:3d} samples ({pct:5.1f}%)")
    else:
        print(f"  {severity.capitalize():10}   0 samples (  0.0%)")
print()

print("BLOOM ANALYSIS")
print("-" * 70)

moderate_blooms = df[df['density_cells_per_ml'] >= 20000]
high_blooms = df[df['density_cells_per_ml'] >= 100000]

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

print("TIMELINE")
print("-" * 70)
for _, row in df.iterrows():
    date_str = row['date'].strftime('%Y-%m-%d')
    density = row['density_cells_per_ml']
    severity = row['severity']
    
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

print()
print("TREND ANALYSIS")
print("-" * 70)

first_half = df.iloc[:len(df)//2]['density_cells_per_ml'].mean()
second_half = df.iloc[len(df)//2:]['density_cells_per_ml'].mean()

if second_half > first_half * 1.5:
    print("  📈 INCREASING TREND - Density rising over time period")
elif second_half < first_half * 0.67:
    print("  📉 DECREASING TREND - Density declining over time period")
else:
    print("  ➡️  STABLE - No strong trend detected")

if len(moderate_blooms) > 0:
    bloom_start = moderate_blooms.iloc[0]['date']
    bloom_end = moderate_blooms.iloc[-1]['date']
    duration = (bloom_end - bloom_start).days
    print(f"\nBLOOM DURATION")
    print(f"  Start: {bloom_start.strftime('%Y-%m-%d')}")
    print(f"  End:   {bloom_end.strftime('%Y-%m-%d')}")
    print(f"  Duration: {duration} days")

print()
print()
print("Results saved to: ./hab_analysis")
print("  - Predictions: preds.csv")
print("  - Metadata: sentinel_metadata.csv")
print("  - Chart: analysis.png")
print()

print("=" * 70)
print("This is what the real tool will produce!")
print("=" * 70)
print()
print("To run with actual satellite data:")
print("  1. Install: pip install cyfi pandas matplotlib")
print("  2. Run: python hab_analysis.py --lat 42.5 --lon -73.2 \\")
print("              --start 2023-06-01 --end 2023-08-31")

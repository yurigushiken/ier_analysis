import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import numpy as np

def analyze_no_signal_per_condition():
    # specific path as requested
    path = "data/csvs_human_verified_vv/child/*.csv"
    files = glob.glob(path)
    
    print(f"Found {len(files)} participant files.")
    
    # Dictionary to store total frames and no-signal frames per event type
    # Structure: {'event_type': {'total_frames': 0, 'no_signal_frames': 0}}
    event_stats = {}
    
    for f in files:
        try:
            # Read necessary columns
            # We need frame-by-frame data now, not just trial summaries
            df = pd.read_csv(f, usecols=['event_verified', 'What', 'Where'])
            
            if df.empty:
                continue
                
            # Identify no-signal frames
            # Condition: What == 'no' AND Where == 'signal'
            df['is_no_signal'] = (df['What'] == 'no') & (df['Where'] == 'signal')
            
            # Group by event type
            grouped = df.groupby('event_verified')
            
            for event, group in grouped:
                total_frames = len(group)
                no_signal_frames = group['is_no_signal'].sum()
                
                if event not in event_stats:
                    event_stats[event] = {'total_frames': 0, 'no_signal_frames': 0}
                
                event_stats[event]['total_frames'] += total_frames
                event_stats[event]['no_signal_frames'] += no_signal_frames
                
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if not event_stats:
        print("No data collected.")
        return

    # Calculate percentages
    results = []
    for event, stats in event_stats.items():
        total = stats['total_frames']
        no_signal = stats['no_signal_frames']
        percent = (no_signal / total * 100) if total > 0 else 0
        
        results.append({
            'Event': event,
            'Total_Frames': total,
            'No_Signal_Frames': no_signal,
            'Percent_No_Signal': percent
        })
    
    # Create DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by percentage descending
    results_df = results_df.sort_values('Percent_No_Signal', ascending=False)
    
    print("\n--- Analysis Results: Average Percentage of 'No Signal' Data per Condition ---")
    print(results_df.to_string(index=False))
    
    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Create bars
    bars = plt.bar(results_df['Event'], results_df['Percent_No_Signal'], color='teal', edgecolor='black')
    
    # Add labels and title
    plt.title('Data Quality by Condition: Percentage of "No Signal" Frames', fontsize=16)
    plt.xlabel('Event Condition', fontsize=12)
    plt.ylabel('Percentage of Frames with No Signal (%)', fontsize=12)
    
    # Add grid lines
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add percentage labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{height:.1f}%',
                 ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save plot
    output_path = 'temp_analysis/no_signal_by_condition.png'
    plt.savefig(output_path, dpi=300)
    print(f"\nPlot saved to {output_path}")
    
    # Save CSV
    csv_path = 'temp_analysis/no_signal_by_condition.csv'
    results_df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")

if __name__ == "__main__":
    analyze_no_signal_per_condition()


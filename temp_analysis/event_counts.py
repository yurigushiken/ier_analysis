import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import seaborn as sns
import math

def analyze_event_distribution():
    # Path to data
    path = "data/csvs_human_verified_vv/child/*.csv"
    files = glob.glob(path)
    
    print(f"Found {len(files)} participant files.")
    
    # List to store data
    all_data = []
    
    for f in files:
        try:
            participant_id = os.path.basename(f).replace('.csv', '')
            
            # Read only necessary columns to save memory/time
            # event_verified is the column with 'gw', 'gwo', etc.
            # trial_number_global identifies the unique trial
            df = pd.read_csv(f, usecols=['trial_number_global', 'event_verified'])
            
            if df.empty:
                print(f"Warning: {participant_id} file is empty.")
                continue
                
            # Drop duplicates to get one row per unique trial
            # We identify a trial by the combination of event type and trial number
            trials = df.drop_duplicates(subset=['event_verified', 'trial_number_global'])
            
            # Count events
            counts = trials['event_verified'].value_counts().reset_index()
            counts.columns = ['Event', 'Count']
            counts['Participant'] = participant_id
            
            all_data.append(counts)
            
        except Exception as e:
            print(f"Error processing {f}: {e}")

    if not all_data:
        print("No data found.")
        return

    # Combine all data
    full_df = pd.concat(all_data, ignore_index=True)
    
    # Get unique events
    unique_events = full_df['Event'].unique()
    unique_events.sort()
    
    print(f"\nIdentified Event Types: {unique_events}")
    
    # Set plot style
    plt.style.use('ggplot')
    
    # Generate a plot for each event type
    for event in unique_events:
        event_data = full_df[full_df['Event'] == event].sort_values('Participant')
        
        if event_data.empty:
            continue
            
        # Calculate figure size based on number of participants
        n_participants = len(event_data)
        width = max(10, n_participants * 0.3)
        
        plt.figure(figsize=(width, 6))
        
        # Create bar plot
        bars = plt.bar(event_data['Participant'], event_data['Count'], color='skyblue', edgecolor='navy')
        
        # Customize plot
        plt.title(f'Number of "{event}" Trials per Participant')
        plt.xlabel('Participant')
        plt.ylabel('Count of Trials')
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(range(0, int(event_data['Count'].max()) + 2))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                     f'{int(height)}',
                     ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        # Save plot
        filename = f"temp_analysis/event_count_{event}.png"
        plt.savefig(filename)
        plt.close()
        print(f"Saved plot for {event} to {filename}")

    # Also print a summary table
    print("\n--- Summary of Event Counts ---")
    pivot_table = full_df.pivot_table(index='Participant', columns='Event', values='Count', fill_value=0)
    print(pivot_table.to_string())
    
    # Save summary CSV
    pivot_table.to_csv("temp_analysis/event_counts_summary.csv")
    print("\nSummary saved to temp_analysis/event_counts_summary.csv")

if __name__ == "__main__":
    analyze_event_distribution()


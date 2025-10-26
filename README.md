Always connect to the environment
conda activate ier_analysis

Source of data: https://drive.google.com/drive/u/0/folders/1fZQjgI5_J19K9s54ciDbHXmunB_SDHAt
put into data\raw

1. Project Background and Scientific Goals

Our research is focused on one of the most fundamental questions in cognitive science: How do infants begin to understand the structure of events and language before they can speak?

When we describe an action like "The woman gives the toy to the man," we are using a "verb-argument structure." The verb is 'gives', and it requires three arguments to make sense: a giver (the woman), a recipient (the man), and an object being given (the toy). A different action, like 'hugging', only requires two arguments: a hugger and someone being hugged.

The central hypothesis of our work, inspired by the foundational studies of Dr. Peter Gordon (e.g., Gordon, 2003), is that infants have a pre-linguistic understanding of this argument structure. We believe they can distinguish between elements that are essential to an event's meaning (like the toy in 'giving') and elements that are merely incidental (like a toy being held during a 'hugging' event).

While earlier studies relied on overall looking time to infer this understanding, our project takes a significant step forward. We use high-resolution eye-tracking data that gives us a frame-by-frame record of exactly where an infant is looking. This allows us to move beyond if they looked, to understand how they looked—their scanning strategies, their focus, and their potential anticipation of the event's outcome.

Your work will be crucial in helping us transform this rich dataset into scientific insights.
2. The Raw Data: Our Ground Truth

All the data for this project is stored in the /data/raw/ directory. You will notice it is separated into two subdirectories:

    data/raw/child/: Contains the eye-tracking data for all our infant participants.

        Example: C:\CascadeProjects\ier_analysis\data\raw\child\Eight-months-0101-947.csv

    data/raw/adult/: Contains eye-tracking data for adult participants, which serves as a control or comparison group.

        Example: C:\CascadeProjects\ier_analysis\data\raw\adult\FiftySix-years-0501-1673.csv

Each CSV file represents a single session for a single participant. The filename itself contains useful metadata, such as the participant's age group and a unique identifier.
3. Decoding the Raw Data Columns

When you open one of these CSV files, you will see a table with many columns. It can look intimidating at first, but each column has a specific purpose. Let's break them down.

Here is an example row:
Eight-0101-947,00:00:05:8667,no,signal,5.8667,5.9,,gw,176,1,1,1,1,1,approach,1,infant,8,0.7

    Participant: A unique identifier for the participant in the trial (e.g., Eight-0101-947).

    Time: A human-readable timestamp in HH:MM:SS:MS format.

    What & Where: These are "pairs" so don't think of them as independent columns.
    "screen" "other" means that they were looking at the screen but not at particular AOI.
    "no" "signal" means there was no looking happening.
    "man" "face" means the blue dot was over the man's face.
    "woman" "body" means blue dot was over the woman's body.
    etc.
    "toy" "other" means subject was looking at the toy. This should only occur in trials that are "with" or "with toy"
    "toy2" "other"  means subject was looking where the toy would be had there been a toy there, had it been the 'with' version. This only occurs during 'wo' or 'without' trials/events.
So, the only "what" "where" pair combinations are as follows (with counts):
no, signal -> 147,577
screen, other -> 62,152
woman, face -> 35,784
man, face -> 33,450
toy, other -> 29,269
man, body -> 19,114
toy2, other -> 16,959
woman, body -> 15,595
man, hands -> 4,258
woman, hands -> 2,001

    Onset & Offset: These are the precise start and end times for the event on this line, measured in seconds from the start of the trial video. This is the primary time measurement we will use for calculations.

    Blue Dot Center: Where the participant is looking at that frame. This is the coordinates of the blue dot, which is like the gaze marker or looking marker from the TOBII machine. 

    event: the name of the event.
    gw give with toy
    gwo give without
    hw hug with toy
    hwo hug without toy
    ugw upsidown give with toy
    uhw upsidown hug with toyy
    ugwo upsidown give without toy
    uhwo upsidown hug without toy
    sw show with toy
    swo show without toy
    f toy is floating

    session_frame:
    the frame number of the whole participant session

    trial_block_cumulative_order
    the nth trial block in participant's session

    trial_block_frame
    the frame number of the trial block

    trial_block_trial
    the nth trial of the trial block

    trial_frame
    the frame number of the trial

    trial_cumulative_by_event
    of the whole session, the nth trial of that particular event (gw, gwo, hw, etc) 

    segment: This is context for the gaze data by labeling the phase of the action in the video. The segments are:

        approach: The actors are walking towards the center of the screen, before the main action.

        interaction: The core event (giving, hugging, showing) is taking place.

        departure: The actors are moving away after the interaction.

    segment_frame: A frame counter that resets for each new segment.

    participant_type: The category of the participant (e.g., 'infant', 'adult').

    participant_age_months & participant_age_years: The participant's age.


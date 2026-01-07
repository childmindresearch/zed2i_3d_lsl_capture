import pyzed.sl as sl
import os
import pandas as pd
from datetime import datetime
import pathlib as pl
import openpyxl
from settings import OUTPUT_DIR


def record_svo(participant_ID, sequence, zed, lsl_outlet):
    """This fucntion initiates an svo recording to be saved upon pipeline completion.

    Change the directory or filenaming scheme below to match your desired preferences.

    Args:
        participant_ID: str containing user-input ID number.
        sequence: int representing the sequence number.
        zed: zed camera object.
        lsl_outlet: pylsl object to stream markers.
    """
    output_dir = pl.Path(OUTPUT_DIR) / "zed2i_SVO_files"
    os.makedirs(output_dir, exist_ok=True)
    output_svo_file = (
        output_dir
        / f"{participant_ID}_seq{sequence}_{datetime.now().strftime('%Y-%m-%d.%f')}.svo2"
    )

    lsl_outlet.push_sample([
        f"SVO_recording_path: {output_svo_file}",
    ])
    recording_param = sl.RecordingParameters()
    recording_param.compression_mode = sl.SVO_COMPRESSION_MODE.H264
    recording_param.video_filename = str(output_svo_file)

    err = zed.enable_recording(recording_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Recording ZED : ", err)
        svo_start_time = datetime.now()

        lsl_outlet.push_sample([
            f"svo_recording_err: {svo_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}",
        ])
        exit(1)

    # Start Recording
    svo_start_time = datetime.now()

    lsl_outlet.push_sample([
        f"SVO_recording_start: {svo_start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}",
    ])
    sl.RuntimeParameters()


def save_sequence(participant_ID, sequence, dataframe):
    # Specify the file path and sheet name
    output_dir = pl.Path(OUTPUT_DIR) / "zed2i_xlsx_files"
    os.makedirs(output_dir, exist_ok=True)
    file_path = (
        output_dir 
        / f"{participant_ID}.xlsx"
    )
    sheet_name = f"seq{sequence}"

    # Try to load the existing file and add a new sheet
    try:
        with pd.ExcelFile(file_path) as xls:
            # Check if the sheet already exists
            if sheet_name in xls.sheet_names:
                print(f"Sheet '{sheet_name}' already exists. No new sheet created.")
                return  # Exit if the sheet already exists

        # Write to the Excel file, creating a new sheet
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a") as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    except FileNotFoundError:
        # If the file doesn't exist, create a new one
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"Data saved to '{sheet_name}' in '{file_path}'.")
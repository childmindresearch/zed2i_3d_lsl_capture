import pyzed.sl as sl

from datetime import datetime
from pylsl import StreamInfo, StreamOutlet

from core import zed_parameters
from core import export

from without_stimulus import processing

from settings import ZED_DEVICE


def run(participant_ID, sequence):
    print(f"Beginning Sequence {sequence}")

    zed = sl.Camera()

    # Create new stream info for lsl, stream camera_open, change source_id from "zed2i-harlem" to appropriate device, ex: "zed2i-midtown"
    info = StreamInfo("MotionTracking", "Markers", 1, 0, "string", ZED_DEVICE)
    outlet = StreamOutlet(info)

    while True:
        key = input(
            "Press 'c' to continue after starting lsl stream in LabRecorder: "
        ).strip()
        if key == "c":
            break

    # Create camera object, initialize camera parameters, open camera
    zed_parameters.initialize_zed_parameters(zed)

    start_time = datetime.now()
    outlet.push_sample([f"camera_open: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')}"])

    # start recording svo file
    export.record_svo(participant_ID, sequence, zed, outlet)

    # main processing
    ordered_df = processing.body_tracking(zed, outlet)

    if ordered_df is None:
        print(
            f"Manual Quit... ZED Body tracking for Participant: {participant_ID} Sequence: {sequence} INCOMPLETED."
        )
        return

    # save data
    export.save_sequence(participant_ID, sequence, ordered_df)

    print(
        f"ZED Body tracking for Participant: {participant_ID} Sequence: {sequence} is complete"
    )

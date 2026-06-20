import subprocess
from pathlib import Path
from services.roi_encoder import build_roi_filter


def generate_dash_stream(lab_id):

    ## path to the test video
    input_video = (
        Path(__file__).parent.parent/ "media"/ "test_video.mp4"
    )

    output_dir = ( Path(__file__).parent.parent/ "dash_server" )
    segments_dir = output_dir / "segments"

    # Create base + segments folder
    output_dir.mkdir( parents=True, exist_ok=True )
    segments_dir.mkdir(parents=True, exist_ok=True)


    # the fourth folder is for the audio
    for i in range(3):
        (segments_dir / str(i)).mkdir( exist_ok=True )


    manifest = "manifest.mpd"

    roi_filter = build_roi_filter(lab_id)

    command = [

        "ffmpeg",

        "-i",
        str(input_video),

        "-filter_complex",

        (
           ## "[0:v]split=3[v1][v2][v3];"
            f"[0:v]{roi_filter},split=3[v1][v2][v3];"
            "[v1]scale=640:360[out1];"
            "[v2]scale=854:480, setdar=16/9[out2];"
            "[v3]scale=1280:720[out3]"
        ),

        # Map video outputs
        "-map", "[out1]",
        "-map", "[out2]",
        "-map", "[out3]",

        # Audio mapping
        #"-map", "0:a",

        # Audio encoder
        #"-c:a", "aac",
        #"-b:a", "128k",
        
        # Video encoders + bitrates
        "-c:v:0", "libx264",
        "-c:v:1", "libx264",
        "-c:v:2", "libx264",

        "-b:v:0", "300k",
        "-b:v:1", "800k",
        "-b:v:2", "1500k",

        # DASH options
        "-use_template", "1",
        "-use_timeline", "1",

        "-adaptation_sets",
        "id=0,streams=v",
        #id=1,streams=a",

        # Segment naming — each representation in its own folder
        "-init_seg_name",
        "segments/$RepresentationID$/init-stream$RepresentationID$.m4s",

        "-media_seg_name",
        "segments/$RepresentationID$/chunk-stream$RepresentationID$-$Number%05d$.m4s",

        "-f",
        "dash",

        manifest

    ]

    result = subprocess.run(
        command,
        cwd=output_dir,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)




""" 
    command = [

        "ffmpeg",

        "-i",
        str(input_video),

        "-map",
        "0:v",

        "-c:v",
        "libx264",

        "-b:v",
        "1500k",

        "-init_seg_name",
        "dash_server/segments/init-stream$RepresentationID$.m4s",

        "-media_seg_name",
        "dash_server/segments/chunk-stream$RepresentationID$-$Number%05d$.m4s",
        
        "-f",
        "dash",

        str(manifest)

    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)
"""

    


""" 
    subprocess.run(command)
"""
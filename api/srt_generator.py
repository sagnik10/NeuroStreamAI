from .utils import convert_to_srt

def format_time(seconds):
    hrs=int(seconds//3600)
    mins=int((seconds%3600)//60)
    secs=int(seconds%60)
    millis=int((seconds-int(seconds))*1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def create_srt(blocks,output_path):
    entries=convert_to_srt(blocks)
    with open(output_path,"w",encoding="utf-8") as f:
        for e in entries:
            f.write(f"{e['index']}\n")
            f.write(f"{format_time(e['start'])} --> {format_time(e['end'])}\n")
            f.write(f"{e['text']}\n\n")
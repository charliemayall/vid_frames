# ffmpeg -i example.mp4 -vf "select=eq(pict_type\,I)" -vsync vfr output_dir/keyframe_%04d.png

import itertools
import json
import xml.etree.ElementTree as E
import regex as re
from pathlib import Path
from bs4 import BeautifulSoup

import subprocess
import yt_dlp
from typing import List

from use_api import filter_subtitles

from structs import FilteredSubtitle


ROOT = Path(__file__).parent
VIDS = ROOT / "videos"
VIDS_NEW = VIDS / "new"
KEYFRAMES = ROOT / "keyframes"
SPEC_FRAMES = ROOT / "specific_frames"
VIDS_NEW.mkdir(parents=True, exist_ok=True)
SPEC_FRAMES.mkdir(exist_ok=True)
KEYFRAMES.mkdir(exist_ok=True)


def download(url: str, output_path="."):
    ydl_opts = {
        "outtmpl": f"{VIDS_NEW}/%(title)s.%(ext)s",
        "format": "bestvideo+bestaudio/best",  # Choose the best video and audio format available
        "noplaylist": True,  # Download only the single video, not a playlist
        "writeautomaticsub": True,
        "subtitleslangs": ["en.*"],
        "subtitlesformat": "ttml",  # USE SRV1 OR TTML
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            print(f"Downloaded: {url}")
    except Exception as e:
        print(f"Error: {e}")


def get_captions_soup(file: Path):
    soup = BeautifulSoup(file.read_text(), "xml")

    ents = soup.find_all("p", {"begin": True, "end": True})
    res = []
    for ent in ents:
        cap = [child.text for child in ent.children]
        cap_clean = "".join(cap).replace("\n", "")
        res.append({**ent.attrs, "text": cap_clean})
    return res


def get_captions(file: Path):
    with open(file) as q:
        text = q.read()
    pos = re.split(r"<[\/]?body.*>", text)
    if len(pos) == 3:
        tree = E.fromstring(pos[1])
        dict_list = [{**d.attrib, "text": d.text} for d in tree.getchildren()]
        # new_path = file.with_suffix(".json")
        # new_path.write_text(json.dumps(dict_list))

        return dict_list
    return None


def frame_at(ts, vid_path, out_path):
    # TS in format "00:00:10.000" , out_path .../..../x.png
    cmd = f"ffmpeg -ss {ts} -i {vid_path} -vframes 1 {out_path}"
    subprocess.run(cmd.split(" "))


def extract_frames_at_timestamps(
    filts: List[FilteredSubtitle], vid_path: Path, folder_name: str
):
    out_path = SPEC_FRAMES / folder_name
    out_path.mkdir(parents=True, exist_ok=True)
    for item in filts:
        out_path = SPEC_FRAMES / folder_name / f"{item.rating}_{item.begin}.png"
        frame_at(item.begin, vid_path, out_path)


# routine("https://www.youtube.com/watch?v=e38WMm62TdI&ab_channel=Diseaseunderthemicroscope")


def routine(url: str) -> List[dict]:

    download(url)
    new_vids = VIDS_NEW.iterdir()
    pairs = []
    for vid_path in new_vids:
        if vid_path.suffix == ".ttml":
            continue
        if not vid_path.suffix in [".mp4", ".webm", ".mkv"]:
            continue
        sub_paths = list(VIDS_NEW.glob(f"{vid_path.stem}*.ttml"))
        vid_path = vid_path.rename(VIDS / vid_path.name.replace(" ", "_"))
        if len(sub_paths) > 0:
            sub_path = sub_paths[0]
            sub_path = sub_path.rename(VIDS / sub_path.name.replace(" ", "_"))
            pairs.append({"vid": vid_path, "sub": sub_path})
    return pairs


def run_link(link: str, topic: str, threshold: float = 0.5):
    assert 0 <= threshold <= 1
    pairs = routine(link)
    # pairs = [
    #     {
    #         "sub": "videos/Mi-28_Hit_by_a_Drone!_Another_45_Russians_Captured_in_Kursk_District.en-orig.ttml",
    #         "vid": "videos/Mi-28_Hit_by_a_Drone!_Another_45_Russians_Captured_in_Kursk_District.webm",
    #     }
    # ]
    for pair in pairs:
        vid_path = Path(pair["vid"])
        sub_path = Path(pair["sub"])
        print(f"Processing {vid_path}")
        captions = get_captions_soup(sub_path)
        captions = [x for x in captions if x["text"] != "\n"]
        if captions is None:
            continue
        filts = []

        x = 0
        c_size = 20
        n_chunk = len(captions) // c_size
        for slice in range(0, len(captions), c_size):
            print(f"Chunk {x//c_size}/{n_chunk}")
            slice = captions[x : x + c_size]
            res = filter_subtitles(slice, topic)
            if res is not None:
                filts.extend(res)
            x += c_size

        folder = SPEC_FRAMES / vid_path.stem
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "filtered.json").write_text(json.dumps(filts))

        extract_frames_at_timestamps(
            [x for x in filts if x.rating >= threshold],
            vid_path,
            vid_path.stem,
        )


run_link("https://www.youtube.com/watch?v=2guSfoUoIs8", "ukraine", 0.3)

# filts = json.loads(
#     Path("/Users/CharlieMayall/Desktop/SpecPath/result_new.json").read_text()
# )

# items = filts["result"]["subtitles"]
# extract_frames_at_timestamps(
#     [FilteredSubtitle.from_dict(item) for item in items],
#     "/Users/CharlieMayall/Desktop/SpecPath/keyframes/videos/Ukrainian_Drones_Hit_Tuapse_Oil_Refinery_and_Morozovsk_Air_Base!.webm",
#     "test",
# )

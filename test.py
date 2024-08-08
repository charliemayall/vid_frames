from bs4 import BeautifulSoup
from pathlib import Path


def get_captions_soup(file: Path):
    soup = BeautifulSoup(file.read_text(), "xml")

    ents = soup.find_all("p", {"begin": True, "end": True})
    res = []
    for ent in ents:
        cap = [child.text for child in ent.children]
        cap_clean = "".join(cap).replace("\n", "")
        res.append({**ent.attrs, "text": cap_clean})
    return res


print(
    get_captions_soup(
        Path(
            "/Users/CharlieMayall/Desktop/SpecPath/keyframes/Peptic_Duodenitis,_Celiac_Disease,_Duodenal_Adenoma_｜_Pathology_101｜_GI_Pathology.en.ttml"
        )
    )
)

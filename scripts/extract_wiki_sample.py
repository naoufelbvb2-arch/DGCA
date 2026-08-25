import json
import sys

sys.path.insert(0, ".")
import pyarrow.parquet as pq

from dgca.encoding.english.normalize import normalize_text

pf = pq.ParquetFile("data/simplewiki_20231101.parquet")
rg = pf.read_row_group(0, columns=["text"])
texts = rg["text"].to_pylist()

sentences = []
for art in texts:
    if not art:
        continue
    norm_res = normalize_text(art)
    for s_start, s_end in norm_res.sentence_spans:
        s_text = art[s_start:s_end].strip()
        if 20 <= len(s_text) <= 120 and "\n" not in s_text:
            sentences.append(s_text)
        if len(sentences) >= 200:
            break
    if len(sentences) >= 200:
        break

print(f"Extracted {len(sentences)} sentences")
with open("tests/data_simplewiki_sample_200.json", "w", encoding="utf-8") as f:
    json.dump(sentences, f, indent=2, ensure_ascii=False)

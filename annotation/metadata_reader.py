import csv

def csv_reader(metadata_path):
    with metadata_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            sentence_display = row["sentence_display"]
            sentence_annotation = row["sentence_annotation"]
            
    return sentence_display, sentence_annotation
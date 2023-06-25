from git import Repo
import os
import json
from bs4 import BeautifulSoup


OUTPUT_CSV_PATH = "cpr.csv"
CPR_DIR = "./open-data"

# Chunking the text in p paragraphs.
def get_data(filename: str) -> tuple:
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
        country_code = data["document_country_code"]
        date = data["document_date"]

        
        name = data["document_name"] if data["document_name"] else ''
        url = data["document_url"]
        
        description = BeautifulSoup(data['document_description'], "html.parser").get_text()
        description = (
            description.strip().replace("\n", " ").encode("ascii", "ignore").decode()
        )

        lang = data["document_language"]
        keywords = data["document_keyword"]

        paragraphs = {}

        # Some policies don't have the full text available
        if len(data["text_blocks"]) > 0:
            for item in data["text_blocks"]:
                p_value = item["text_block_id"].split("_")[0]
                text = item["text"]
                soup = BeautifulSoup(text, "html.parser")
                text_no_tags = soup.get_text()

                if p_value in paragraphs:
                    paragraphs[p_value] += (
                        " "
                        + text_no_tags.strip()
                        .replace("\n", " ")
                        .encode("ascii", "ignore")
                        .decode()
                    )
                else:
                    paragraphs[p_value] = (
                        text_no_tags.strip()
                        .replace("\n", " ")
                        .encode("ascii", "ignore")
                        .decode()
                    )
    return (
        country_code,
        date,
        "fulltext_" + name,
        url,
        description,
        list(paragraphs.values()),
        lang,
        keywords,
    )


def main():
    # This will fail on windows due  to ':' in some filenames
    Repo.clone_from(
        "https://github.com/climatepolicyradar/open-data.git", "./open-data"
    )

    samples = []
    data_path = os.path.join(CPR_DIR, 'data')

    for dir_name in os.listdir(data_path):
        folder_path = os.path.join(data_path, dir_name)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                filename_path = os.path.join(folder_path, file_name)

                (
                    country_code,
                    date,
                    name,
                    url,
                    description,
                    full_text,
                    lang,
                    keywords,
                ) = get_data(filename_path)

                # Do whatever with the data
                # e.g. could throw it into pandas for analysis/filtering
                # just saving and dumping it to csv for now
                for text in full_text:
                    samples.append(text)


    # Saving the samples
    with open(OUTPUT_CSV_PATH, "w", encoding="utf-8") as f:
        f.write('"id","text"\n')
        for counter, sample in enumerate(samples):
            sample = (
                sample.replace('"', '""').replace("\n", "\\n") + '"\n'
            )  # To not mess the CSV format
            f.write(f'"{counter}","' + sample)  # Important! " as quotechar


if __name__ == "__main__":
    main()

import arxiv
import os
import tarfile
import re

# in order to run this program you have to install pandoc
# I installed it via stack (https://github.com/jgm/pandoc/blob/main/INSTALL.md)


def download():
    tex_dir = "data_tex"
    if not os.path.exists(tex_dir):
        os.mkdir(tex_dir)

    search = arxiv.Search(
        query="climate" and "climate change" and "global warming",
        max_results=1000,
        sort_by=arxiv.SortCriterion.Relevance
    )

    for paper in search.results():
        # downloading a file and removing special characters
        paper.title = re.sub('[^A-Za-z0-9]+', '', paper.title)

        if len(paper.title) > 70:
            paper.title = paper.title[:69]

        paper_filename = paper.title + ".tar.gz"
        paper.download_source(dirpath="./data_tex", filename=paper_filename)

        new_dir = os.path.join('data_tex', paper.title)

        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        else:
            os.remove(os.path.join('data_tex', paper_filename))
            continue
        # tar.gz archive is inaccessible to pandoc, so the archive has to be extracted
        file = tarfile.open(os.path.join('data_tex', paper_filename))
        file.extractall(new_dir)
        file.close()
        os.remove(os.path.join('data_tex', paper_filename))


def convert():
    plain_dir = "data_plain"
    if not os.path.exists(plain_dir):
        os.mkdir(plain_dir)

    # converting to plain if possible
    n = 0   # number of file if there are several tex files
    for folder_name in os.listdir("data_tex"):
        for file_name in os.listdir(os.path.join("data_tex", folder_name)):
            if file_name.endswith('.tex'):
                n += 1

                plain_path = "data_plain\\" + folder_name + str(n) + '.text'
                cmd = "pandoc -o " + plain_path + " " + "data_tex\\" + folder_name + "\\" + file_name
                print(cmd)

                if os.path.exists(os.path.join("data_plain", plain_path)):
                    break
                os.system(cmd)


def main():
    download()
    convert()


if __name__ == "__main__":
    main()

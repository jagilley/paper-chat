import requests
from subprocess import call
import os
from pylatexenc.latex2text import LatexNodes2Text

def get_paper(paper_url):
    if 'abs' in paper_url:
        eprint_url = paper_url.replace("https://arxiv.org/abs/", "https://arxiv.org/e-print/")
    elif 'pdf' in paper_url:
        eprint_url = paper_url.replace("https://arxiv.org/pdf/", "https://arxiv.org/e-print/")
    else:
        raise ValueError("Invalid arXiv URL")

    suffix = 'paper-dir/' + eprint_url.replace("https://arxiv.org/e-print/", "")

    # check if the directory exists
    if os.path.exists(suffix):
        print("Paper already downloaded, skipping download")
    else:
        print("Downloading paper")
        r = requests.get(eprint_url)

        with open("paper", "wb") as f:
            f.write(r.content)

        # unzip gzipped tar file to new directory
        call(["mkdir", suffix])
        call(["tar", "-xzf", "paper", "-C", suffix])

    # get the list of all .tex files in the directory
    tex_files = [f for f in os.listdir(suffix) if f.endswith('.tex')]
    # remove math_commands.tex from tex_files if it exists
    if 'math_commands.tex' in tex_files:
        tex_files.remove('math_commands.tex')
    if len(tex_files) == 1:
        # read the main tex file
        with open(f'{suffix}/{tex_files[0]}', 'r') as f:
            paper_tex = f.read()
    elif len(tex_files) == 0:
        raise ValueError("No .tex files found in the paper")
    else:
        raise ValueError("More than one .tex file found in the paper")
    
    # convert latex to text
    paper_text = LatexNodes2Text().latex_to_text(paper_tex)

    with open(f"{suffix}/main.txt", 'w') as f:
        f.write(paper_text)
    
    return paper_text

if __name__=="__main__":
    paper_url = "https://arxiv.org/abs/2206.08896"
    paper_text = get_paper(paper_url)
    print(paper_text)
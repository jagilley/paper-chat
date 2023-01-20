import requests
from subprocess import call

paper_url = "https://arxiv.org/abs/2206.08896"

def get_paper(paper_url):
    if 'abs' in paper_url:
        eprint_url = paper_url.replace("https://arxiv.org/abs/", "https://arxiv.org/e-print/")
    elif 'pdf' in paper_url:
        eprint_url = paper_url.replace("https://arxiv.org/pdf/", "https://arxiv.org/e-print/")
    else:
        raise ValueError("Invalid arXiv URL")

    r = requests.get(eprint_url)

    with open("paper", "wb") as f:
        f.write(r.content)

    # unzip gzipped tar file to new directory
    call(["mkdir", "paper-dir"])
    call(["tar", "-xzf", "paper", "-C", "paper-dir"])

    # latex to text
    call(["latex2text", "paper-dir/main.tex", ">", "paper-dir/main.txt"])

    with open("paper-dir/main.txt") as f:
        paper_text = f.read()
    
    return paper_text

if __name__=="__main__":
    paper_text = get_paper(paper_url)
    print(paper_text)
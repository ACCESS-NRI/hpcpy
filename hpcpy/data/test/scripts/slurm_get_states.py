"""Quick script to download the slurm states for development."""

from bs4 import BeautifulSoup
import requests

url = "https://slurm.schedmd.com/job_state_codes.html"


if __name__ == "__main__":

    html = requests.get(url).content

    soup = BeautifulSoup(html, "html.parser")

    # Get the state codes
    state_tbl = soup.find_all("table")[0]

    statuses = dict()

    for tr in state_tbl.find_all("tr")[1:]:
        code, description = tr.find_all("td")
        # Remove newlines and tabs etc.
        description = " ".join([s.strip() for s in description.text.splitlines()])
        statuses[code.text] = description

    print(statuses)

    flag_tbl = soup.find_all("table")[1]
    flags = dict()

    for tr in flag_tbl.find_all("tr")[1:]:
        code, description = tr.find_all("td")
        # Remove newlines and tabs etc.
        description = " ".join([s.strip() for s in description.text.splitlines()])
        flags[code.text] = description

    print(flags)

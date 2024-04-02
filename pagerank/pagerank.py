import os
import random
import re
import sys
import numpy as np
import pandas as pd

DAMPING = 0.85
SAMPLES = 10000
#SAMPLES = 30


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    ranks = dict()

    # Define transition model
    totpages = len(corpus)
    nbrlinks = len(corpus[page])
    if nbrlinks > 0:
        randprob = (1 - damping_factor) / totpages
        problinks = damping_factor / nbrlinks 

        ranks[page] = randprob
        for link in corpus:
            if link in corpus[page]:
                ranks[link] = problinks + randprob
            else:
                ranks[link] = randprob
    else:
        problinks = 1 / totpages 
        for link in corpus:
            ranks[link] = problinks 

    return ranks


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # First, pick a random page in the corpus for our starting point.
    ranks = {}
    page = random.sample(list(corpus.keys()), 1)
    weights = transition_model(corpus, page[0], DAMPING)
    ranks[page.pop()] = 1

    # Gather n random samples by simulating a users navigation through 
    # the corpus.
    for snbr in range(n-1):
        pages = list(weights.keys())
        pageweights = list(weights.values())
        page = np.random.choice(pages, p=pageweights)
        if page in ranks.keys():
            ranks[page] += 1
        else:
            ranks[page] = 1

        weights = transition_model(corpus, page, DAMPING)

    # Convert the page counts to percentages
    for page in ranks:
        ranks[page] = ranks[page] / n

    return ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    totalpages = len(corpus)
    currentranks = {page: (1 / totalpages) for page in corpus}
    newranks = {page: None for page in corpus}

    while True:
        for page in corpus:
            newrank = 0
            for link in corpus:
                # If page has links
                if page in corpus[link]:
                    newrank += currentranks[link] / len(corpus[link])
                # If page has no links
                if len(corpus[link]) == 0:
                    newrank += currentranks[link] / totalpages

            newrank *= damping_factor
            newrank += (1 - damping_factor) / totalpages

            newranks[page] = newrank

        # If the max difference for all of the pages < .001, we have converged
        currvals = np.array(list(currentranks.values()))
        newvals = np.array(list(newranks.values()))
        if np.max(np.abs(newvals-currvals)) < .001:
            break
        else:
            currentranks = newranks.copy()

    return currentranks


if __name__ == "__main__":
    main()

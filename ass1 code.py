# task 1
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import unicodedata
import re
import matplotlib.pyplot as plt
import numpy as np
import csv
import json

# Opening JSON file
f = open('rugby.json')

# returns JSON object as
# a dictionary
data = json.load(f)
team_names = []
for team in data['teams']:
    team_names.append(team['name'])
# Closing file
f.close()
page_limit = 1000

# intialize new team for teams that have 2 words
new_team = []
for team in team_names:
    res = bool(re.search(r"\s", team))
    if res:
        names = team.split()
        names.append(team)
        new_team.append(names)


# function to find the index largest score in list of scores
def find_maxindex(lst):
    new_lst = []
    for str in lst:
        sum = 0
        count = 0
        new_str = str.split('-')
        for num in (new_str):
            number = int(num.strip().rstrip(',.'))
            sum = number + sum
            count += 1
            if count == 2:
                new_lst.append(sum)

    ind = np.argmax(new_lst)

    return ind


# Specify the initial page to crawl
base_url = 'http://comp20008-jh.eng.unimelb.edu.au:9889/main/'
seed_item = 'index.html'

seed_url = base_url + seed_item
page = requests.get(seed_url)
soup = BeautifulSoup(page.text, 'html.parser')

visited = {};
visited[seed_url] = True
pages_visited = 1

# Remove index.html
links = soup.findAll('a')
seed_link = soup.findAll('a', href=re.compile("^index.html"))
# to_visit_relative = list(set(links) - set(seed_link))
to_visit_relative = [l for l in links if l not in seed_link]

# intialize list
titles = []
to_visit = []
urls = []
first_team = []
match_score = []
end_score = []

# Resolve to absolute urls
for link in to_visit_relative:
    to_visit.append(urljoin(seed_url, link['href']))

# Find all outbound links on succsesor pages and explore each one
while (to_visit):

    # Impose a limit to avoid breaking the site
    if pages_visited == page_limit:
        break

    # consume the list of urls
    link = to_visit.pop(0)

    # append the links to a list
    urls.append(link)

    # need to concat with base_url, an example item <a href="catalogue/sharp-objects_997/index.html">
    page = requests.get(link)

    # scarping code goes here
    soup = BeautifulSoup(page.text, 'html.parser')

    # mark the item as visited, i.e., add to visited list, remove from to_visit
    visited[link] = True
    to_visit
    new_links = soup.findAll('a')

    # find all headers and append to list
    header = soup.findAll('h1')
    for head in header:
        title = (head.text)
        titles.append(title)

    # regex pattern

    # find the first team that appears that is in the json file
    text = soup.findAll("div", {"id": "main_article"})

    for paragraph in text:
        count = 0

        # find all matches in the paragraph
        match = re.findall(' \d{1,2}-\d{1,2}[, .?:;\|]', paragraph.text)
        match_score.append(match)

        # check each word in paragraph if it's a match
        for word in paragraph.text.split():
            new_word = word.strip('."?!,')
            if new_word in team_names and count == 0:
                first_team.append(new_word)
                count += 1
            for i in range(len(new_team)):
                if new_word == new_team[i][0] and count == 0:
                    first_team.append(new_team[i][2])
                    count += 1
        if new_word not in team_names and count == 0:
            first_team.append(None)

    for new_link in new_links:
        new_item = new_link['href']
        new_url = urljoin(link, new_item)

        if new_url not in visited and new_url not in to_visit:
            to_visit.append(new_url)

# go through the list in match_score and append largest score to new list end_score
for lst in match_score:
    if len(lst) == 0:
        end_score.append(None)
    else:
        index = find_maxindex(lst)

        end_score.append(lst[index].rstrip('.,'))

# create empty list called game difference

game_diff = []

# find the difference in absolute values of the match_scores
for values in end_score:
    if values != None:
        numbers = (values.strip().rstrip('.,').split('-'))
        change = abs(int(numbers[0]) - int(numbers[1]))
        game_diff.append(change)
    else:
        game_diff.append(None)

# appending the team and game difference if there is not any None types
double_lst = []
for i in range(len(game_diff)):
    if first_team[i] != None and game_diff[i] != None:
        double_lst.append([first_team[i], game_diff[i]])

# finding the average sum
average_sum = []
for country in team_names:

    count = 0
    sum = 0
    for lst in double_lst:
        if lst[0] == country:
            count += 1
            sum += lst[1]
    if count != 0:
        average_sum.append(sum / count)
    else:
        average_sum.append(0)

# put the information into a data frame and store as csv file
df = pd.DataFrame({'urls': urls, 'headline': titles})

df.dropna(
    axis=0,
    how='any',
    thresh=None,
    subset=None,
    inplace=True
)
df.to_csv('task1.csv', index=False)

df2 = pd.DataFrame({'urls': urls, 'headline': titles, 'team': first_team, 'score': end_score})

df2.dropna(
    axis=0,
    how='any',
    thresh=None,
    subset=None,
    inplace=True
)
df2.to_csv('task2.csv', index=False)

df3 = pd.DataFrame({'team': team_names, 'avg game difference': average_sum})
df3.to_csv('task3.csv', index=False)

df4 = pd.DataFrame({'teams': first_team, 'score': end_score})

df4.dropna(
    axis=0,
    how='any',
    thresh=None,
    subset=None,
    inplace=True
)
# finding the number of times article has been written
counts = df4.teams.value_counts()

# plotting the bar graph
counts[0:5].plot.bar(rot=30, title="Number of articles written about the top 5 teams");
plt.ylabel('Frequency')
plt.xlabel('Rugby Teams')
plt.tight_layout()
plt.savefig('task4.png')
plt.close()

# res is a dictionary for team name and average sum that follows
res = {team_names[i]: average_sum[i] for i in range(len(team_names))}
df5 = pd.DataFrame({'no of articles': counts, 'avg game difference': res})

# sort in ascending order
df5 = df5.sort_values('no of articles')

# plot the bar graph
df5.plot.bar(rot=30, title="Avg game diff and No of articles written about teams ");
plt.ylabel('Frequency')
plt.xlabel('Rugby Teams')
plt.tight_layout()
plt.savefig('task5.png')
plt.close()
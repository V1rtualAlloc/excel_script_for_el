# extract clubs info
import requests
from openpyxl import Workbook
from bs4 import BeautifulSoup

url = 'http://www.euroleague.net/competition/teams'
r = requests.get(url)

soup = BeautifulSoup(r.text, "html.parser")
tables = soup.find_all('ul', class_='nav-teams nav-teams-16')

teamsData = {
    'teams': [],
    'urls': []
}
for table in tables:
    lis = table.find_all('li')
    for li in lis:
        anchor_tag = li.a
        teamsData['teams'].append(anchor_tag["title"])
        teamsData['urls'].append('http://www.euroleague.net' + str(anchor_tag["href"]))

# write 'Teams' sheet in xlsx file
wb = Workbook()
ws = wb.active
ws.title = 'Teams'
ws.cell(row=1, column=1).value = 'Team'
for cell in range(0, len(teamsData['teams'])):
    ws.cell(row=cell + 2, column=1).value = teamsData['teams'][cell]
    ws.cell(row=cell + 2, column=1).hyperlink = teamsData['teams'][cell]

for team in teamsData['teams']:
    wb.create_sheet(team)
    index = teamsData['teams'].index(team)
    r = requests.get(str(teamsData['urls'][index]))
    soup = BeautifulSoup(r.text, "html.parser")
    divs = soup.find_all('div', class_='item player')

    playerStats = ['Name', 'Jersey Number', 'Position', 'Country', 'Year of Birth', 'Height',
                   'G', 'GS', 'MIN', 'PT', '2FGM', '2FGA', '3FGM', '3FGA', 'FTM', 'FTA',
                   'ORB', 'DRB', 'TRB', 'ASS', 'STL', 'TO', 'BF', 'BA', 'FC', 'FR', 'PIR', 'PER']

    for item in range(len(playerStats)):
        wb[team].cell(row=1, column=item + 1).value = playerStats[item]

    row = 2
    print('Processing ' + team),
    for div in divs:
        name = div.find('div', class_='name').a
        playerName = name.string
        playerUrl = 'http://www.euroleague.net' + name['href']
        wb[team].cell(row=row, column=1).value = playerName
        wb[team].cell(row=row, column=1).hyperlink = playerUrl
        data = div.find('div', class_='data')
        wb[team].cell(row=row, column=2, value=data.find('span', class_='dorsal').string)
        wb[team].cell(row=row, column=3, value=data.find('span', class_='position').string)
        wb[team].cell(row=row, column=4, value=data.find('span', class_='country').string)
        wb[team].cell(row=row, column=5, value=data.find('span', class_='birth').string)
        wb[team].cell(row=row, column=6, value=data.find('span', class_='height').string[-4:])
        column = 7
        playerReq = requests.get(playerUrl)
        playerHtml = BeautifulSoup(playerReq.text, "html.parser")
        tds = playerHtml.find_all('td', class_='PlayerTitleColumn')
        for td in tds:
            if td.string == 'Totals':
                otherStats = td.parent
                statList = []
                for stat in otherStats:
                    if stat.string == 'Totals':
                        continue
                    elif stat.string.find(':') != -1:
                        statList.append(stat.string[:stat.string.find(':')])
                    elif stat.string.find('/') != -1:
                        statList.append(stat.string[:stat.string.find('/')])
                        statList.append(stat.string[stat.string.find('/') + 1:])
                    else:
                        statList.append(stat.string)
                statList = filter(lambda glyph: glyph != u'\n', statList)
                for i in range(len(statList) - 1 + column, column - 1, -1):
                    wb[team].cell(row=row, column=i, value=int(statList.pop()))
        print('.'),
        row += 1
    print('Done')
wb.save('data.xlsx')

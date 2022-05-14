import requests
from bs4 import BeautifulSoup
import sqlite3
import os

db = sqlite3.connect("C:\\Users\\USer\\Desktop\\rides.db")
sql = db.cursor()
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0',
           'accept': '*/*'}


def get_content(url):
    answer = requests.get(url=url, headers=HEADERS)
    return answer


# Info about models what will be parsed:


def get_times():
    html = get_content('https://www.attheraces.com/racecard/Sedgefield/19-April-2022/1305').text
    return html


HTML = get_times()


# https://www.attheraces.com/racecards/Sedgefield/19-April-2022
# Competition: uid // Cx{counter}, name_competition, date_and_time, distance, requirements, winner
def get_competitions():
    soup = BeautifulSoup(HTML, 'html.parser')
    competitions = []
    c = soup.find("ul", class_="race-header__times hidden visible--tablet-wide").find_all("a")
    counter = 0
    for compet in c:
        time = ''.join(ch for ch in compet.text if ch.isalnum())
        if (time == 'ViewAllRaces'):
            break
        url = f'https://www.attheraces.com/racecard/Sedgefield/19-April-2022/{time}'
        html = get_content(url).text
        s = BeautifulSoup(html, 'html.parser')
        temp = s.find("div", class_="race-header__content js-race-header__content")
        # date and time
        t_date = temp.find("h2", class_="h4 flush").text
        t_date = t_date.replace('Sedgefield', '')
        t_date.split()
        date = ' '.join(t_date.split())
        # uid
        uid = f'Cx{counter}'
        counter += 1
        # competition_name
        t_name = temp.find("h2", class_="h4 flush").text
        t_name.split()
        name = ' '.join(t_name.split())
        # distance
        t_dist = s.find("div", class_="p--large font-weight--semibold").text
        t_dist.split()
        dist = ' '.join(t_dist.split())
        # requirements
        t_req_and_winner = s.find("div", class_="race-header__details race-header__details--primary").find_all("p")
        t_req = t_req_and_winner[1].text
        t_req.split()
        req = ' '.join(t_req.split())
        # winner
        t_winner = t_req_and_winner[2].text
        t_winner.split()
        winner = ' '.join(t_winner.split())
        winner = winner.replace('Winner', '')
        competitions.append({
            'UID': uid,
            'Name': name,
            'Date': date,
            'Distance': dist,
            'Requirements': req,
            'Winner': winner
        })
    return competitions


# Result: uid // Rx{counter}, place, horse_name, jockey, trainer, SP, Age/Wt, competition_id
def get_results(jockeys_hrefs, trainer_hrefs, horses_hrefs):
    soup = BeautifulSoup(HTML, 'html.parser')
    results = []
    c = soup.find("ul", class_="race-header__times hidden visible--tablet-wide").find_all("a")
    counter = 0
    c_uid = 0
    for compet in c:
        time = ''.join(ch for ch in compet.text if ch.isalnum())
        if time == 'ViewAllRaces':
            break
        url = f'https://www.attheraces.com/racecard/Sedgefield/19-April-2022/{time}'
        html = get_content(url).text
        s = BeautifulSoup(html, 'html.parser')
        runner_cards = s.find_all("div", class_="card-entry")
        for card in runner_cards:
            position = card.find("span", class_="p--large font-weight--semibold")
            if position:
                # Horse Name
                t_horse_name = card.find("h2", class_="h6 flush").text
                hrefh = card.find("h2", class_="h6 flush").find('a')['href']
                t_horse_name.split()
                horse_name = ' '.join(t_horse_name.split())
                horses_hrefs.append({
                    'href': hrefh,
                    'name': horse_name
                })
                # Position in race
                pos = position.text
                # Uid result statement
                uid = f'Rx{counter}'
                counter += 1
                # Competition uid
                competition_id = f'Cx{c_uid}'
                # Jockey & trainer
                t_trainer_and_jockey = card.find("div", class_="card-cell card-cell--jockey-trainer unpadded-sides")
                if t_trainer_and_jockey:
                    t_trainer_and_jockey = t_trainer_and_jockey.find_all("a")
                trainer = 'None'
                jockey = 'None'
                if t_trainer_and_jockey:
                    for person in t_trainer_and_jockey:
                        if 'trainer' in person['href']:
                            trainer_hrefs.append(person['href'])
                            t_trainer = person.text
                            t_trainer.split()
                            trainer = ' '.join(t_trainer.split())
                        if 'jockey' in person['href']:
                            jockeys_hrefs.append(person['href'])
                            t_jockey = person.text
                            t_jockey.split()
                            jockey = ' '.join(t_jockey.split())
                # SP
                t_sp = card.find("div", class_="card-cell card-cell--odds unpadded")
                sp = 'None'
                if t_sp:
                    t_sp = t_sp.text
                    t_sp.split()
                    sp = " ".join(t_sp.split())
                # Age/Wt
                t_age_wt = card.find("div", class_="card-cell card-cell--stats unpadded")
                age_wt = 'None'
                if t_age_wt:
                    t_age_wt = t_age_wt.text
                    t_age_wt.split()
                    age_wt = ' '.join(t_age_wt.split())

                results.append({
                    'Horse Name': horse_name,
                    'Pos': pos,
                    'UID': uid,
                    'Competition ID': competition_id,
                    'Jockey': jockey,
                    'Trainer': trainer,
                    'SP': sp,
                    'Age/Wt': age_wt
                })
        c_uid += 1
    return results


# Jockey: uid // Jx{counter}, name, rides, wins, places, win_prize
def get_jockeys(hrefs):
    counter = 0
    jockeys = []
    for href in hrefs:
        url = f'https://www.attheraces.com{href}'
        html = get_content(url).text
        soup = BeautifulSoup(html, 'html.parser')
        # uid
        uid = f'Jx{counter}'
        # name
        t_name = soup.find("h1", class_='h3').text
        t_name.split();
        name = ' '.join(t_name.split())
        stats = soup.find('tbody').find_all('td')
        c = 0
        rides = 'NONE'
        wins = 'NONE'
        places = 'NONE'
        win_prize = 'NONE'
        for stat in stats:
            if c == 5:
                break
            # win prize
            if c == 4:
                ñ = 5
                win_prize = stat.text
                continue
            # places
            if c == 3:
                c = 4
                places = stat.text
                continue
            # wins
            if c == 2:
                c = 3
                wins = stat.text
                #print(wins)
                continue
            # rides
            if c == 1:
                c = 2
                rides = stat.text
                #print(rides)
                continue
            if 'TOTAL' in stat.text:
                c = 1
                continue
        #print(rides)
        jockeys.append({
            'UID': uid,
            'Name': name,
            'Rides': rides,
            'Wins': wins,
            'Places': places,
            'WinPrize': win_prize,
        })
        counter += 1
    return jockeys


# Trainer: uid // Tx{counter}, name, rides, wins, places
def get_trainers(hrefs):
    counter = 0
    trainers = []
    for href in hrefs:
        url = f'https://www.attheraces.com{href}'
        html = get_content(url).text
        soup = BeautifulSoup(html, 'html.parser')
        # uid
        uid = f'Tx{counter}'
        test = soup.find('h1')
        if test:
            counter += 1
            # name
            name = test.text
            # print(name)
            stats = soup.find('tbody').find_all('td')
            c = 0
            rides = 'NONE'
            wins = 'NONE'
            places = 'NONE'
            win_prize = 'NONE'
            for stat in stats:
                # win prize
                if c == 4:
                    win_prize = stat.text
                    #print(win_prize)
                    break
                # places
                if c == 3:
                    c = 4
                    places = stat.text
                    continue
                # wins
                if c == 2:
                    c = 3
                    wins = stat.text
                    #print(wins)
                    continue
                # rides
                if c == 1:
                    c = 2
                    rides = stat.text
                    # print(rides)
                    continue
                if 'TOTAL' in stat.text:
                    c = 1
                    continue
            #print(name)
            trainers.append({
                'UID': uid,
                'Name': name,
                'Rides': rides,
                'Wins': wins,
                'Places': places,
                'WinPrize': win_prize
            })
    return trainers


# Horse: uid // 'Hx{counter}', Name, Trainer, Owner, Sire, Dam, Dam's Sire
def get_horses(hrefs):
    counter = 0
    horses = []
    for href in hrefs:
        url = f'https://www.attheraces.com{href["href"]}'
        # uid
        uid = f'Hx{counter}'
        counter += 1
        # name
        name = href['name']
        html = get_content(url).text
        soup = BeautifulSoup(html, 'html.parser')
        trainer = 'NONE'
        owner = 'NONE'
        tr_and_own = soup.find("div", class_='column width--tablet-12').find_all("a")
        for t in tr_and_own:
            if 'trainer' in t['href']:
                # trainer
                trainer = t.text
            if 'owner' in t['href']:
                # owner
                owner = t.text
        sire_dam_damsire = soup.find_all("div", class_="column width--tablet-12")
        if not sire_dam_damsire:
            continue
        if not sire_dam_damsire[1]:
            continue
        sire_dam_damsire = sire_dam_damsire[1]
        if not sire_dam_damsire.find("li"):
            continue
        sire_dam_damsire.find_all("li")
        sire = 'NONE'
        dam = 'NONE'
        damsire = 'NONE'
        for a in sire_dam_damsire:
            # Sire
            if 'Sire:' in a.text:
                t_a = a.text.split()
                t_a = ' '.join(a.text.split())
                c = t_a.find('Sire') + 6
                sire = ''
                while c < len(t_a):
                    sire += t_a[c]
                    c += 1
                    if t_a[c] == '(':
                        break
                #print(sire)
            if 'Dam:' in a.text:
                t_a = a.text.split()
                t_a = ' '.join(a.text.split())
                c = t_a.find('Dam') + 5
                dam = ''
                while c < len(t_a):
                    dam += t_a[c]
                    c += 1
                    if t_a[c] == '(':
                        break
                #print(dam)
            if "Dam’s Sire:" in a.text:
                t_a = a.text.split()
                t_a = ' '.join(a.text.split())
                c = t_a.find("Dam’s Sire") + len("Dam's Sire") + 1
                damsire = ''
                while c < len(t_a):
                    damsire += t_a[c]
                    c += 1
                    if t_a[c] == '(':
                        break
                #print(damsire)
        horses.append({
            'UID': uid,
            'Name': name,
            'Trainer': trainer,
            'Owner': owner,
            'Sire': sire,
            'Dam': dam,
            'DamSire': damsire
        })
    return horses


# Competition: uid // Cx{counter}, name_competition, date_and_time, distance, requirements, winner
def put_compets_into_db(competitions):
    # competitions
    sql.execute(f"""CREATE TABLE IF NOT EXISTS Competitions (
            uid TEXT,
            Name TEXT,
            Date TEXT,
            Distance TEXT,
            Requirements TEXT,
            Winner TEXT
    )""")
    db.commit()
    for competition in competitions:
        try:
            sql.execute(f"SELECT uid from Competitions")
            sql.execute(f"INSERT INTO Competitions VALUES(?, ?, ?, ?, ?, ?)", (
                competition['UID'],
                competition['Name'],
                competition['Date'],
                competition['Distance'],
                competition['Requirements'],
                competition['Winner']
            ))
        except sqlite3.IntegrityError:
            continue
    db.commit()


# Result: uid // Rx{counter}, place, horse_name, jockey, trainer, SP, Age/Wt, competition_id
def put_results_into_db(results):
    sql.execute(f"""CREATE TABLE IF NOT EXISTS Results (
        uid TEXT,
        Place TEXT,
        HorseName TEXT,
        Jockey TEXT,
        Trainer TEXT, 
        SP TEXT,
        Age_Wt TEXT,
        Compet_ID TEXT
    )""")
    db.commit()
    for result in results:
        sql.execute("SELECT uid FROM Results")
        sql.execute("INSERT INTO Results VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
            result['UID'],
            result['Pos'],
            result['Horse Name'],
            result['Jockey'],
            result['Trainer'],
            result['SP'],
            result['Age/Wt'],
            result['Competition ID']
        ))
    db.commit()


# Jockey: uid // Jx{counter}, name, rides, wins, places, win_prize
def put_jockeys_into_db(jockeys):
    sql.execute("""CREATE TABLE IF NOT EXISTS Jockeys (
        uid TEXT,
        Name TEXT,
        Rides TEXT,
        Wins TEXT,
        Places TEXT,
        WinPrize TEXT
    )""")
    db.commit()
    for jockey in jockeys:
        sql.execute("SELECT uid FROM Jockeys")
        sql.execute("INSERT INTO Jockeys VALUES (?, ?, ?, ?, ?, ?)", (
            jockey['UID'],
            jockey['Name'],
            jockey['Rides'],
            jockey['Wins'],
            jockey['Places'],
            jockey['WinPrize']
        ))
    db.commit()


# Trainer: uid // Tx{counter}, name, rides, wins, places
def put_trainers_into_db(trainers):
    sql.execute("""CREATE TABLE IF NOT EXISTS Trainers (
        uid TEXT,
        Name TEXT,
        Rides TEXT,
        Wins TEXT,
        Places TEXT
    )""")
    db.commit()
    for trainer in trainers:
        sql.execute("SELECT uid FROM Trainers")
        sql.execute("INSERT INTO Trainers VALUES (?, ?, ?, ?, ?)", (
            trainer['UID'],
            trainer['Name'],
            trainer['Rides'],
            trainer['Wins'],
            trainer['Places']
        ))
    db.commit()


# Horse: uid // 'Hx{counter}', Name, Trainer, Owner, Sire, Dam, Dam's Sire
def put_horses_into_db(horses):
    sql.execute("""CREATE TABLE IF NOT EXISTS Horses (
        uid TEXT,
        Name TEXT,
        Trainer TEXT,
        Owner TEXT,
        Sire TEXT,
        Dam TEXT, 
        DamSire TEXT
    )""")
    db.commit()
    for horse in horses:
        sql.execute("SELECT uid FROM Horses")
        sql.execute("INSERT INTO Horses VALUES (?, ?, ?, ?, ?, ?, ?)", (
            horse['UID'],
            horse['Name'],
            horse['Trainer'],
            horse['Owner'],
            horse['Sire'],
            horse['Dam'],
            horse['DamSire']
        ))
    db.commit()


def put_info_into_db(comp, res, jock, tr, h):
    put_horses_into_db(h)
    put_jockeys_into_db(jock)
    put_trainers_into_db(tr)
    put_results_into_db(res)
    put_compets_into_db(comp)
    db.commit()


def parse():
    competitions = []
    results = []
    jockeys = []
    trainers = []
    horses = []
    t_hrefs = []
    j_hrefs = []
    h_hrefs = []
    competitions = get_competitions()
    results = get_results(j_hrefs, t_hrefs, h_hrefs)
    jockeys = get_jockeys(j_hrefs)
    trainers = get_trainers(t_hrefs)
    horses = get_horses(h_hrefs)
    while os.stat('C:\\Users\\USer\\Desktop\\rides.db').st_size / (1024 * 1024) <= 1:
        put_info_into_db(competitions, results, jockeys, trainers, horses)
    db.close()


if __name__ == '__main__':
    parse()
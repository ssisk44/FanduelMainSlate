import datetime
import itertools
import random

import pandas as pd
import numpy as np

file_c = 'DFSFiles/Contest/12262021.csv'
file_e = 'DFSFiles/Edited/12262021_e.csv'

def main():
    split_players_by_position()
    cleanlineups_salarycheck(createLineups())
    cleanlineups_teamcheck()
    numbertonames()
    namestoentry()
    randomselectnames()

def split_players_by_position():
    df = pd.read_csv(file_e)
    df.sort_values(['Position','Salary'], ascending=[True,False]).to_csv(file_e, index=False)

    def write_to_csv(df, type):
        df.to_csv('ContestPositionOutput/' + str(type) + 's.csv')

    df_qb = df[df['Position'] == 'QB']
    write_to_csv(df_qb, 'QB')

    df_rb = df[df['Position'] == 'RB']
    write_to_csv(df_rb, 'RB')

    df_wr = df[df['Position'] == 'WR']
    write_to_csv(df_wr, 'WR')

    df_te = df[df['Position'] == 'TE']
    write_to_csv(df_te, 'TE')

    flex = [df_rb, df_wr, df_te]
    df_flex = pd.concat(flex)
    write_to_csv(df_flex, 'FLEX')

    df_def =  df[df['Position'] == 'D']
    write_to_csv(df_def, 'D')

def createLineups():
    QB = pd.read_csv('ContestPositionOutput/QBs.csv').to_numpy()
    RB = pd.read_csv('ContestPositionOutput/RBs.csv').to_numpy()
    WR = pd.read_csv('ContestPositionOutput/WRs.csv').to_numpy()
    TE = pd.read_csv('ContestPositionOutput/TEs.csv').to_numpy()
    FLEX = pd.read_csv('ContestPositionOutput/FLEXs.csv').to_numpy()
    D = pd.read_csv('ContestPositionOutput/Ds.csv').to_numpy()

    qbs = []
    for i in QB:
        qbs.append(i[0])

    rbs = []
    for i in RB:
        rbs.append(i[0])
    rbs2 = list(itertools.combinations(rbs, 2))
    rbs3 = list(itertools.combinations(rbs, 3))

    wrs = []
    for i in WR:
        wrs.append(i[0])
    wrs3 = list(itertools.combinations(wrs, 3))
    wrs4 = list(itertools.combinations(wrs, 4))

    tes = []
    for i in TE:
        tes.append(i[0])

    ds = []
    for i in D:
        ds.append(i[0])

    f1 = list(itertools.product(qbs, rbs2, wrs4, tes, ds))
    f2 = list(itertools.product(qbs, rbs3, wrs3, tes, ds))

    def clean_data(list):
        collection = []
        for l in range(0, len(list)):
            this = []
            for i in list[l]:
                if type(i) == int:
                    this.append(i)

                else:
                    for j in i:
                        this.append(j)
            collection.append(this)
        return collection

    final = clean_data(f1) + clean_data(f2)
    print('Length of Combinations: ', len(final))
    return final

def cleanlineups_salarycheck(list):
    # not over salary limit
    p = pd.read_csv(file_e).to_numpy()
    master = []
    def checkSalary(l):
        total = 0
        for i in l:
            total += int(p[i][7])
            if total > 60000:
                break
        if total <= 60000:
            master.append(l)

    for i in list:
        checkSalary(i)

    print('Length of combinations after salary pruning: ', len(master))
    pd.DataFrame(master).to_csv('XD.csv', index=False)

def cleanlineups_teamcheck():
    #no more than 4 from a team in lineup
    x = pd.read_csv(file_e).to_numpy()
    master = []

    def checkTeams(l):
        teams = []
        for i in l:
            teams.append(x[i][9])
        if teams.count('DAL') == 4 and teams.count('WAS') <= 3 and teams.count('MIA') <= 3 and teams.count('NO') <= 2: ####CHI should be 4 but i dont like them for this with 4
            master.append(l)

    p = pd.read_csv('XD.csv').to_numpy()
    for i in p:
        checkTeams(i)

    print('Length of combinations after team pruning: ', len(master))
    pd.DataFrame(master).to_csv('XD2.csv', index=False)

def numbertonames():
    x = pd.read_csv('XD2.csv').to_numpy()
    p = pd.read_csv(file_e).to_numpy()

    names = []
    for i in x:
        list = []
        for j in i:
            list.append(p[j][4])
        names.append(list)
    final = []

    t3 = ['Ingram II', 'Seals-Jones', 'Parker', 'Callaway', 'Smith', 'Wilson', 'Humphrey', 'Carter', 'Humpries', 'Sims','Pollard']
    def count_tier(tier_list, roster):
        count = 0
        for i in roster:
            if i in tier_list:
                count += 1
        return count

    for list in names:
        if 'Waddle' not in list or 'Lamb' not in list:
            continue

        #must have Cowboys RB
        if 'Pollard' not in list and 'Elliott' not in list:
            continue

        #one washington secnodary reciever
        if list.count('Carter') + list.count('Sims') + list.count('Humpries') > 1:
            continue

        #no two doplhins rbs
        if 'Gaskin' in list and 'Johnson' in list:
            continue

        #no two washington rbs
        if 'Gibson' in list and 'Patterson' in list:
            continue

        # no two washington rbs
        if 'Ingram II' in list and 'Kamara' in list:
            continue

        if count_tier(t3, list) > 2:
            continue


        final.append(list)

    print('Length of combinations after situational game script pruning: ', len(final))
    pd.DataFrame(final).to_csv('names.csv',  index=False)

def namestoentry():
    x = pd.read_csv('names.csv') #.to_numpy()
    p = pd.read_csv(file_e).to_numpy()
    x['9'] = x['8']
    x['8'] = x['3']
    x = x.drop('3', 1)
    x = x.to_numpy()


    def get_player_id(name):
        for i in p:
            if i[4] == name:
                return i[0]

    master = []
    for l in x:
        list = []
        for i in l:
            list.append(get_player_id(i))
        master.append(list)

    pd.DataFrame(master).to_csv('entrynumbers.csv', index=False)

def randomselectnames():
    x = pd.read_csv('entrynumbers.csv').to_numpy()

    list = random.sample(range(len(x)), 150)

    master = []
    for i in list:
        master.append(x[i])

    pd.DataFrame(master).to_csv('selectedentrynumbers.csv', index=False)

main()
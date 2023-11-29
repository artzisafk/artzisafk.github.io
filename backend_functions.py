import json
import os
USERCACHE = "D:\\MultiMC\\instances\\AchieveToDo-1.2\\.minecraft\\usercache.json"
WORLD = "D:\\MultiMC\\instances\\AchieveToDo-1.2\\.minecraft\\saves\\uhc #2"
USERCACHE = "usercache.json"
WORLD = "world"
DATA_FOLDER = 'data\\'
total_adv = 0
hidden_adv = 0
first_adv = 0
hidden_first_adv = 0
players = {}


class Player:
    def __init__(self, uuid, name):
        self.uuid = uuid
        self.name = name
        self.completed = 0
        self.first = 0
        self.completed_hidden = 0
        self.first_hidden = 0
        self.tabs = {}
        self.cheater = False


class Tab:
    def __init__(self, name):
        self.progress = 0
        self.completed = False
        self.advancements = {}
        self.name = name


class Advancement:
    def __init__(self, name, description, criteria, tab, requirements, total, hidden):
        if requirements is None:
            self.requirements = [[i] for i in criteria]
        else:
            self.requirements = requirements
        self.progress = 0
        self.completed = False
        self.time = 'uncompleted'
        self.name = name
        self.description = description
        self.criteria = criteria
        self.hidden = hidden
        self.tab = tab
        self.total = total
        self.progress_list = [False for _ in self.requirements]
        self.first = False

    def copy(self):
        return Advancement(self.name, self.description, self.criteria.copy(), self.tab,
        self.requirements.copy(), self.total, self.hidden)


def get_uuids(path):
    uuids = {}
    with open(path, 'r') as file:
        for player in json.load(file):
            uuids[player['uuid']] = player['name']
    return uuids


def load_advancements():
    global total_adv
    global hidden_adv
    advancements = {}
    paths = ['blazeandcave\\advancements\\adventure',
             'blazeandcave\\advancements\\animal',
             'blazeandcave\\advancements\\bacap',
             'blazeandcave\\advancements\\biomes',
             'blazeandcave\\advancements\\building',
             'blazeandcave\\advancements\\challenges',
             'blazeandcave\\advancements\\enchanting',
             'blazeandcave\\advancements\\end',
             'blazeandcave\\advancements\\farming',
             'blazeandcave\\advancements\\mining',
             'blazeandcave\\advancements\\monsters',
             'blazeandcave\\advancements\\nether',
             'blazeandcave\\advancements\\potion',
             'blazeandcave\\advancements\\redstone',
             'blazeandcave\\advancements\\statistics',
             'blazeandcave\\advancements\\weaponry',
             'minecraft\\advancements\\adventure',
             'minecraft\\advancements\\end',
             'minecraft\\advancements\\husbandry',
             'minecraft\\advancements\\nether',
             'minecraft\\advancements\\story']
    exceptions = [DATA_FOLDER + 'minecraft\\advancements\\husbandry\\obtain_netherite_hoe.json']
    for path in paths:
        _ = (DATA_FOLDER + path).split('\\')
        namespace = f'{_[1]}:{_[3]}/'
        files = os.listdir(DATA_FOLDER + path)
        for file in files:
            filepath = DATA_FOLDER + path + '\\' + file
            if filepath in exceptions:
                continue
            content = json.load(open(filepath, 'r'))
            criteria = content['criteria']
            requirements = None
            total = 1
            if 'requirements' in content:
                requirements = content['requirements']
                total = len(requirements)
            hidden = False
            if 'hidden' in content['display']:
                if content['display']['hidden'] == 'true':
                    hidden = True
                    hidden_adv += 1
                else:
                    total_adv += 1
            else:
                total_adv += 1
            name = content['display']['title']['translate']
            if name == '65':
                name = '65 hours of walking'
            description = content['display']['description']['translate']
            tab = content['rewards']['function'].split(':')[1].split('/')[0]
            data_name = namespace + file[:-5]
            advancements[data_name] = Advancement(name, description, criteria, tab, requirements, total, hidden)
    return advancements


def generate_players(uuids):
    for uuid in uuids:
        if uuid + '.json' in os.listdir(WORLD + '\\advancements'):
            players[uuid] = Player(uuid, uuids[uuid])


def generate_advancement(key, advancement):
    progress_list = advancement_list[key].progress_list.copy()
    for i in range(len(progress_list)):
        for j in advancement_list[key].requirements[i]:
            if j in advancement['criteria']:
                progress_list[i] = True
    return progress_list, progress_list.count(True)


def get_player_advancements(uuid):
    advancements = {}
    normal_count = 0
    hidden_count = 0
    filepath = WORLD + '\\advancements\\' + uuid + '.json'
    player_adv = json.load(open(filepath, 'r'))
    for key in advancement_list:
        if key in player_adv:
            if key in ['blazeandcave:technical/big_cheater', 'blazeandcave:technical/you_are_a_big_cheater',
                       'blazeandcave:technical/cheater3', 'blazeandcave:technical/cheater2']:
                players[uuid].cheater = True
                continue
            advancement = advancement_list[key].copy()
            tab = advancement_list[key].tab
            if player_adv[key]['done']:
                if advancement_list[key].hidden:
                    hidden_count += 1
                else:
                    normal_count += 1
                advancement.completed = True
                advancement.progress = advancement.total
                advancement.time = get_advancement_time(player_adv[key])
                advancement.progress_list = [True for _ in range(len(advancement.requirements))]
            else:
                progress_list, progress = generate_advancement(key, player_adv[key])
                advancement.progress_list = progress_list.copy()
                advancement.progress = progress

            if tab not in advancements:
                advancements[tab] = {}
            advancements[tab][key] = advancement
        else:
            advancement = advancement_list[key].copy()
            tab = advancement_list[key].tab
            if tab not in advancements:
                advancements[tab] = {}
            advancements[tab][key] = advancement
    players[uuid].completed = normal_count
    players[uuid].completed_hidden = hidden_count
    players[uuid].tabs = advancements


def assert_first_advancements():
    first_advancements = {}
    for key in advancement_list:
        ans_uuid = 0
        time = 'uncompleted'
        for uuid in players:
            time_player = players[uuid].tabs[advancement_list[key].tab][key].time
            if time_player < time:
                time = time_player
                ans_uuid = uuid
        if ans_uuid:
            players[ans_uuid].tabs[advancement_list[key].tab][key].first = True
            players[ans_uuid].first += not players[ans_uuid].tabs[advancement_list[key].tab][key].hidden
            players[ans_uuid].first_hidden += players[ans_uuid].tabs[advancement_list[key].tab][key].hidden
        first_advancements[key] = (ans_uuid, time, advancement_list[key].hidden)
    return first_advancements


def get_advancement_time(advancement):
    global advancement_list
    time = max([advancement['criteria'][i] for i in advancement['criteria']])
    return time


advancement_list = load_advancements()
generate_players(get_uuids(USERCACHE))
for uuid in players:
    get_player_advancements(uuid)
first_advancements = assert_first_advancements()

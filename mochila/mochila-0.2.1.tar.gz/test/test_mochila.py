import csv

class Agent:
    def __init__(self, code, first_name, last_name, rank, active, peer, *args):
        """
        An agent that is used for declarative operations      
        :param code: The agent id
        :param first_name: first name
        :param last_name: last name
        :param rank: rank in the system
        :param active: is the agent active
        :param peer: peer agents
        :param args: countries where the agent can be active
        """
        self.code = code
        self.first_name = first_name
        self.last_name = last_name
        self.rank = int(rank)
        self.active = True if active.strip() == 'TRUE' else False
        if peer:
            self.peers = peer.split('~')
        else:
            self.peers = []
        self.visited = list(args)

    def __str__(self):
        return self.code

    def __repr__(self):
        return self.code

people_csv = [
    "730-46-0957,Cass,      Lamba,       91,  TRUE,         ,Sweden,Switzerland,China,Georgia,",
    "186-01-5810,Barbara,   Rosewell,   487,  TRUE,         ,Indonesia,Poland,Albania,Portugal,",
    "424-16-0664,Elnore,    Dillestone,  95,  TRUE,730-46-0957,Ireland,Russia,Philippines,Japan,",
    "694-68-6118,Brig,      Derham,     367, FALSE,186-01-5810,Pakistan,Russia,China,Papua New Guinea,",
    "212-70-6483,Adelbert,  Michelet,   166, FALSE,186-01-5810~424-16-0664,Honduras,Spain,Brazil,Sierra Leone,",
    "824-34-4142,Aldon,     Craske,     437, FALSE,,Italy,Poland,Philippines,Argentina,",
    "539-35-1184,Valentine, Woolvin,     13, FALSE,694-68-6118,Spain,Bulgaria,Indonesia,,",
    "861-26-2185,Godard,    Gadie,       99, FALSE,212-70-6483,Portugal,Brazil,Thailand,China,",
    "368-95-4835,Etan,      Bumphries,  291, FALSE,         ,Tunisia,France,Mexico,Armenia,",
    "859-05-6244,Sutherlan, McElwee,    434,  TRUE,824-34-4142,China,Russia,Bosnia and Herzegovina,China,"]

agents = dict()
agentreader = csv.reader(people_csv, delimiter=',')
for row in agentreader:
    p = Agent(*row)
    agents[p.code] = p

agents_get = agents.get
for k, v in agents.items():
    v.peers = [x for x in [agents_get(p) for p in v.peers] if x is not None]


class MochilaTest:

    def test_aggregate(self):
        def get_name(p):
            return "{} {}".format(p.first_name, p.last_name)

        def get_code(p):
            return p.code

        mochila = self.type2test(agents.values())
        d = mochila.aggregate(get_code, get_name)
        for code, p in agents.items():
            name = d[code]
            self.assertIn(p.first_name, name)
            self.assertIn(p.last_name, name)

    def test_closure(self):
        def get_peer(agent):
            return agent.peers

        mochila = self.type2test(agents.values())
        cl = mochila.closure(get_peer)
        self.assertEqual(10, len(cl))

        def flatten(iterable):
            if isinstance(iterable, Agent):
                yield iterable.code
            else:
                for x in iterable:
                    if isinstance(x, Agent):
                        yield x.code
                    elif x:
                        for x2 in x:
                            yield from flatten(x2)

        result = []
        for peerh in cl:
            agent_peers = list(flatten(peerh))
            if agent_peers:
                result.append(agent_peers)
        self.assertEqual(6, len(result))
        # FIXME Can we do more proper tests?

    def test_collect(self):

        def get_countries(agent):
            return [c for c in agent.visited if len(c) > 0]  # Ignore empty

        mochila = self.type2test(agents.values())
        a_countries = mochila.collect(get_countries).flatten()
        countries = {"Sweden", "Switzerland", "China", "Georgia", "Indonesia", "Poland", "Albania", "Portugal",
                     "Ireland", "Russia" "Philippines", "Japan", "Pakistan", "Russia", "China", "Papua New Guinea",
                     "Honduras", "Spain", "Brazil", "Sierra Leone", "Italy", "Poland", "Philippines", "Argentina",
                     "Spain", "Bulgaria", "Indonesia", "Portugal", "Brazil", "Thailand", "China", "Tunisia", "France",
                     "Mexico", "Armenia", "China", "Russia", "Bosnia and Herzegovina", "China"}
        for ac in a_countries:
            self.assertIn(ac, countries)

        # oc = a_countries.asOrderedSet()
        # import pprint
        # pprint.pprint(oc)

    def test_exists(self):

        def high_rank(agent):
            return agent.rank <= 50

        mochila = self.type2test(agents.values())
        self.assertTrue(mochila.exists(high_rank))

    def test_for_all(self):

        def at_least_one_country(agent):
            return len(agent.visited) > 0

        mochila = self.type2test(agents.values())
        self.assertTrue(mochila.for_all(at_least_one_country))

    def test_one(self):

        def find_539_35_1184(agent):
            return agent.code == "539-35-1184"

        mochila = self.type2test(agents.values())
        self.assertTrue(mochila.one(find_539_35_1184))

    def test_rejet(self):

        def active(agent):
            return agent.active

        mochila = self.type2test(agents.values())
        inactive = mochila.reject(active)
        inactive_codes = {"694-68-6118", "212-70-6483", "824-34-4142", "539-35-1184", "861-26-2185", "368-95-4835"}
        for ic in inactive_codes:
            agent = agents[ic]
            self.assertIn(agent, inactive)
        self.assertEqual(6, len(inactive))

    def test_select(self):

        def active(agent):
            return agent.active

        mochila = self.type2test(agents.values())
        active = mochila.select(active)
        active_codes = {"730-46-0957", "186-01-5810", "424-16-0664", "859-05-6244"}
        for ic in active_codes:
            agent = agents[ic]
            self.assertIn(agent, active)
        self.assertEqual(4, len(active))

    def test_select_one(self):

        def active(agent):
            return agent.active

        mochila = self.type2test(agents.values())
        active = mochila.select_one(active)
        active_codes = {"730-46-0957", "186-01-5810", "424-16-0664", "859-05-6244"}
        self.assertIn(active, [agents[code] for code in active_codes])

    def test_sort_by(self):

        def by_rank(agent):
            return agent.rank

        mochila = self.type2test(agents.values())
        sorted = mochila.sort_by(by_rank)
        ordered_ranks = ["539-35-1184", "730-46-0957", "424-16-0664", "861-26-2185", "212-70-6483", "368-95-4835",
                         "694-68-6118", "859-05-6244", "824-34-4142", "186-01-5810", ]
        for i, code in enumerate(ordered_ranks):
            agent = agents[code]
            self.assertEqual(agent, sorted[i])

from pyranda import Jmenos, Prijmenis

j = pyranda.Jmenos()
p = pyranda.Prijmenis()
for a in range(1, 10):
    jmeno = j.GetRandomJmeno(pohlavi=1)
    prijmeni = p.GetRandomPrijmeni(pohlavi=1)

    print(jmeno + " " + prijmeni)

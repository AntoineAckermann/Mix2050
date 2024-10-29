import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pyomo.environ import ConcreteModel, Var, Objective, Constraint, Reals, NonNegativeReals, Suffix, Set, ConstraintList, value
from pyomo.opt import SolverFactory

df = pd.read_pickle("dataRTE.pkl")
parc = pd.read_pickle("parcRTE.pkl")


#df = df.resample("H").mean()

nb_pas = len(df.index)
pas = (24*365)/nb_pas
pas_par_mois = int(nb_pas/12)


disp_solaire = df["Solaire normalisé"].to_list()
disp_eolien = df["Eolien normalisé"].to_list()
disp = [disp_solaire, disp_eolien]

max_mensuel_hydro = (pas*df["Hydraulique"]).resample("M").sum().to_list()
max_mensuel_nucleaire = (pas*df["Nucléaire"]).resample("M").sum().to_list()

#PARAMETRES

T = [t for t in range(nb_pas)]
G = ["Parc solaire", "Parc eolien", "Parc hydraulique", "Parc nucleaire", "Parc gaz", "Parc charbon", "Parc fioul"]
cap = parc.loc[2019, G].to_list()
cout_marginal = [0, 0, 0, 30, 70, 86, 162] # €/MWh_el
#CO2 = [55, 7, 6, 418, 1060, 730, 6] #tC02/MWh_el
N = [n for n in range(len(G))]
d = df["Consommation"].to_list()

m = ConcreteModel()

m.N = Set(initialize=N) #capacité solaire, éolien, pilotables
m.Np = Set(initialize=N[2:]) #technologies pilotables
m.T = Set(initialize=T) #pas temporels

# VARIABLES

m.g = Var(m.N, domain=NonNegativeReals) #capacité installée pour chaque techno
m.x = Var(m.Np, m.T, domain=NonNegativeReals) #pilotage

# CONTRAINTES

m.demande = Constraint(m.T, rule=lambda m, t: m.g[0]*disp_solaire[t]+m.g[1]*disp_eolien[t]
                                              +sum(m.x[n,t] for n in N[2:]) == d[t])

m.cap = Constraint(m.Np, m.T, rule=lambda m, n, t: m.x[n, t] <= m.g[n]) #aucune source ne peut dépasser sa capacité installée
min_nucleaire = 0.3
#m.start_up_nucleaire = Constraint(m.T, rule=lambda m, t: m.x[3, t] >= min_nucleaire*m.g[3])

m.cap_max = Constraint(m.N, rule=lambda m, n: m.g[n] == cap[n]) #capacité installée = capacité 2019

#Contraintes sur l'énergie mensuelle max

m.max_energie_hydro = ConstraintList()
m.max_energie_nucleaire = ConstraintList()

for j in range(12):
    m.max_energie_hydro.add(expr=sum(m.x[2, t] for t in range(j*pas_par_mois, (j+1)*pas_par_mois))*pas
                                 <= max_mensuel_hydro[j])
    #m.max_energie_nucleaire.add(expr=sum(m.x[3, t] for t in range(j*pas_par_mois, (j+1) * pas_par_mois))*pas
                                # <= max_mensuel_nucleaire[j])

#Contraintes de ramp-up
ramp_up_nuc= 0.2*60*pas #cf thèse C.Cany: toutes les variations sont inférieures à 0,2%P_nom/min
ramp_up_hydro = 0.2*60*pas


#m.ramp_up_hydro_max = Constraint(T[:-1], rule=lambda m, t: m.x[2, t+1]-m.x[2, t] >= (-ramp_up_hydro/100)*m.g[2])
#m.ramp_up_hydro_min = Constraint(T[:-1], rule=lambda m, t: m.x[2, t+1]-m.x[2, t] <= (ramp_up_hydro/100)*m.g[2])

m.ramp_up_nucleaire_max = Constraint(T[:-1], rule=lambda m, t: m.x[3, t+1]-m.x[3, t] >= (-ramp_up_nuc/100)*m.g[3])
m.ramp_up_nucleaire_min = Constraint(T[:-1], rule=lambda m, t: m.x[3, t+1]-m.x[3, t] <= (ramp_up_nuc/100)*m.g[3])


# OBJECTIF

m.objectif = Objective(expr=sum(m.x[n, t]*cout_marginal[n]*pas for t in T for n in N[2:])
                        + sum(m.g[n]*disp[n][t]*cout_marginal[n]*pas for t in T for n in N[:2]))

print("init probleme ok")

opt = SolverFactory("cplex")
solve = opt.solve(m)

print("optimisation ok")

print(solve)


result = pd.DataFrame(index=df.index)

result["Solaire simulé"] = m.g[0].value*df["Solaire normalisé"]
result["Eolien simulé"] = m.g[1].value * df["Eolien normalisé"]
result["Production simulée"] = result["Solaire simulé"] + result["Eolien simulé"]
result["Consommation"] = df["Consommation"]

gens = ["Solaire simulé", "Eolien simulé", "Hydraulique simulé", "Nucleaire simulé", "Gaz simulé",
        "Charbon simulé", "Fioul simulé"]

for n, gen in enumerate(gens[2:]):
    result["{}".format(gen)] = [m.x[n + 2, t].value for t in range(nb_pas)]
    result["Production simulée"] += result["{}".format(gen)]

result.to_pickle("resultats_2019.pkl")

for i, gen in enumerate(G):
    print("{} = {}GW".format(gen, m.g[i].value/1000))
for g in gens:
    print("{} : {}TWh".format(g, sum(result[g])*pas/1000000))

print("Coût total = {}M€".format(value(m.objectif)/1e6))

ax = (result.loc["2019", gens]/1000).plot.area()
ax.set_ylabel("GW")

ax1 = ax.twinx()
#(result.loc["2019", ["Consommation"]]/1000).plot(ax=ax1,color="pink")
(result.loc["2019", ["Consommation"]]/1000).plot(color="pink")

plt.show()


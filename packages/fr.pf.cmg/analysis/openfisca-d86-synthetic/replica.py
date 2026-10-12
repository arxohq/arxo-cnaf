from openfisca_france import FranceTaxBenefitSystem
from openfisca_core.simulations import SimulationBuilder
system=FranceTaxBenefitSystem()
base={
 'familles': {'f': {'parents':['p'],'enfants':['e'], 'ass_mat':{'2024':True},
                    'prestations_familiales_base_ressources':{'2024-04':31261,'2024-06':31261,'2024-09':31261}}},
 'foyers_fiscaux': {'ff': {'declarants':['p'],'personnes_a_charge':['e']}},
 'menages': {'m': {'personne_de_reference':['p'],'enfants':['e']}},
 'individus': {'p': {'date_naissance':{'2024':'1980-01-01'},'activite':{'2024':'actif'}},
               'e': {'date_naissance':{'2024':'2020-01-01'}}}}
for resources,dob in [(31261,'2020-01-01'),(80000,'2021-01-01')]:
 base['individus']['e']['date_naissance']['2024']=dob
 for m in ['2024-04','2024-06','2024-09']: base['familles']['f']['prestations_familiales_base_ressources'][m]=resources
 for month in ['2024-04','2024-06','2024-09']:
  builder=SimulationBuilder();builder.set_default_period('2024')
  try:
   sim=builder.build_from_dict(system,base)
   print(resources,dob,month,sim.calculate('paje_cmg',month),sim.calculate('prestations_familiales_base_ressources',month),sim.calculate('age',month))
  except Exception as e:print(type(e).__name__,str(e)[:400]);raise

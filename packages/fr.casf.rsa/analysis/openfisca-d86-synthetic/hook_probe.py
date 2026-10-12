import importlib.util
from pathlib import Path
path=Path('corpus/laws/fr/rsa/tools/openfisca_hook.py')
spec=importlib.util.spec_from_file_location('rsa_hook_private',path)
hook=importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)
class Ctx:
    class Skip(Exception): pass
    def __init__(self, parents, children, births, major):
        self.parents=parents;self.children=children;self.births=births;self.major=major
        self.people={k:{} for k in parents+children}
        self.item={'name':'d86-synthetic', 'input':{'famille':{'parents':parents,'enfants':children},
                   'individus':self.people,'familles':{'famille_n_1':{}}},'output':{'rsa':0}}
        self.period='2024-06'
    def value(self,var,period=None,index=0):
        if var=='rsa_enfant_a_charge': return True
        if var=='rsa_nb_enfants': return len(self.children)
        if var=='rsa_majore_eligibilite': return self.major
        if var=='date_naissance': return self.births[index]
        if var=='rsa_eligibilite': return True
        if var=='statut_occupation_logement': return 'locataire_vide'
        return 0
c=Ctx(['p1','p2'],['c1','c2','c3','c4'],['1990-01-01','1990-01-01']+['2018-01-01']*4,False)
f=hook.facts(c)
print('six_person_facts',len([x for x in f if x.startswith('foyer_membre_rang')]),len([x for x in f if x.startswith('foyer_enfant_charge')]))
assert len([x for x in f if x.startswith('foyer_membre_rang')])==6
assert len([x for x in f if x.startswith('foyer_enfant_charge')])==4
assert not any(x.startswith(('foyer_sup_taux40','foyer_sup_taux30')) for x in f)
c=Ctx(['p1'],['c1'],['1990-01-01','2023-05-15'],True)
f=hook.facts(c)
print('under3_isolation', 'isolement_constate({main})' in f)
assert 'isolement_constate({main})' in f
assert any(x.startswith('foyer_naissance') and '@2023-05-15' in x for x in f)
assert not any(x.startswith('majore_debut_mois') for x in f)
c=Ctx(['p1'],[],['1990-01-01'],True)
try: hook.facts(c)
except Ctx.Skip as e:
 print('pregnancy_skip',str(e))
 assert 'date de déclaration de grossesse' in str(e)
else: raise AssertionError('pregnancy without date must skip')

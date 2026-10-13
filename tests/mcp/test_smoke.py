import importlib.util
from pathlib import Path
import unittest
import json
import hashlib
import tempfile
import io
import tarfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('mcp_smoke', Path(__file__).parents[2]/'tools/mcp_smoke.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def docker_archive(path, config=b'{"architecture":"amd64","os":"linux"}'):
    digest=hashlib.sha256(config).hexdigest();name='blobs/sha256/'+digest
    with tarfile.open(path,'w') as archive:
        for filename,raw in [('manifest.json',json.dumps([{'Config':name,'RepoTags':None,'Layers':[]}]).encode()),(name,config)]:
            member=tarfile.TarInfo(filename);member.size=len(raw);archive.addfile(member,io.BytesIO(raw))
    return 'sha256:'+digest


def policy(image):
    return {'Image':image,'Mounts':[],'Config':{'User':'65532:65532'},'HostConfig':{'NetworkMode':'none','ReadonlyRootfs':True,'Privileged':False,'CapDrop':['ALL'],'CapAdd':None,'SecurityOpt':['no-new-privileges'],'Tmpfs':{'/state':'rw,noexec,nosuid,nodev,size=64m,mode=0700,uid=65532,gid=65532','/tmp':'rw,noexec,nosuid,nodev,size=8m'},'Memory':512*1024*1024,'PidsLimit':128,'NanoCpus':1000000000}}


class SmokeAssertionTests(unittest.TestCase):
    def test_missing_facts_must_be_neither_and_date_preserved(self):
        case={'legalTime':'2024-03-15','expect':{'truthStatus':'NEITHER','evaluationStatus':'COMPUTED'}}
        response={'result':{'structuredContent':{'answer':{'truthStatus':'NEITHER','evaluationStatus':'COMPUTED'},'provenance':{'legalTime':'2024-03-15'}}}}
        smoke.assert_case(case,response)
        response['result']['structuredContent']['answer']['truthStatus']='FALSE_ONLY'
        with self.assertRaises(AssertionError):smoke.assert_case(case,response)

    def test_inferred_result_needs_actual_rule_proof(self):
        case={'legalTime':'2021-06-15','expect':{'truthStatus':'TRUE_ONLY','evaluationStatus':'COMPUTED','proof':True}}
        response={'result':{'structuredContent':{'answer':{'truthStatus':'TRUE_ONLY','evaluationStatus':'COMPUTED'},'provenance':{'legalTime':'2021-06-15'},'evaluation':{'proofGraph':{'nodes':[{'kind':'query_evaluation'}]}}}}}
        with self.assertRaises(AssertionError):smoke.assert_case(case,response)
        response['result']['structuredContent']['evaluation']['proofGraph']['nodes'].append({'kind':'rule_application'})
        smoke.assert_case(case,response)

    def test_denied_facet_is_not_unknown_tool(self):
        case={'expect':{'refusal':True,'errorCode':-32002}}
        smoke.assert_case(case,{'error':{'code':-32002}})
        with self.assertRaises(AssertionError):smoke.assert_case(case,{'error':{'code':-32601}})

    def test_host_provenance_must_match_binary(self):
        case={'legalTime':'2024-03-15','expect':{'truthStatus':'NEITHER','evaluationStatus':'COMPUTED'}}
        response={'result':{'structuredContent':{'answer':{'truthStatus':'NEITHER','evaluationStatus':'COMPUTED'},'provenance':{'legalTime':'2024-03-15','rustCodeHash':'sha256:wrong'}}}}
        with self.assertRaises(AssertionError):smoke.assert_case(case,response,'expected')

    def test_service_environment_is_not_inherited(self):
        env=smoke.clean_env(Path('/state'))
        for name in ('LAW_ANSWERS_URL','LAW_NEURAL_URL','LAW_MCP_OTLP_URL','LAW_MCP_ROOT','LAW_MCP_PROFILE'):
            self.assertNotIn(name,env)


class PromotionIntegrityTests(unittest.TestCase):
    def test_altered_candidate_and_failed_smoke_cannot_promote(self):
        promotion_spec=importlib.util.spec_from_file_location('promote_mcp',Path(__file__).parents[2]/'tools/promote_mcp.py')
        promotion=importlib.util.module_from_spec(promotion_spec);promotion_spec.loader.exec_module(promotion)
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td);commit='a'*40;host_digest=hashlib.sha256(b'host').hexdigest()
            files=['image.tar','runtime.tar.gz','tree.pin.json','offline-smoke.json','image-smoke.json','materialization.json','container-policy.json','runtime-contract.json','host-compatibility.json','runtime.lock.json']
            for name in files:(directory/name).write_bytes(b'accepted')
            for name in ('offline-smoke.json','image-smoke.json'):
                (directory/name).write_text(json.dumps({'status':'passed','hostSha256':host_digest,'networkIsolation':'docker --network none','casesSha256':'cases','sourcePolicySha256':'policy','checks':[{'id':'initialize','status':'passed'}]}))
            image=docker_archive(directory/'image.tar');archive_bytes=(directory/'image.tar').read_bytes()
            (directory/'container-policy.json').write_text(json.dumps(policy(image)))
            accepted={'platform':'linux-amd64','binarySha256':'sha256:'+host_digest,'sourceCommit':commit}
            (directory/'runtime.lock.json').write_text(json.dumps({'host':{'sourceCommit':commit,'platforms':{'linux-amd64':{'binarySha256':'sha256:'+host_digest}}}}))
            (directory/'runtime-contract.json').write_text(json.dumps({'status':'accepted','acceptance':{'finalHostPin':accepted}}))
            (directory/'host-compatibility.json').write_text(json.dumps({'status':'compatible','platforms':{'linux-amd64':{'status':'compatible','checks':[{'status':'passed'}],'binarySha256':'sha256:'+host_digest,'sourceCommit':commit}}}))
            (directory/'tree.pin.json').write_text(json.dumps({'treeSha256':'tree'}))
            receipt={'imageId':image,'acceptance':{'casesSha256':'cases','sourcePolicySha256':'policy','httpCheckIds':['initialize']},'acceptedHost':accepted,'runtimeTreeDigest':'tree','status':'accepted','sourceCommit':commit,'fullCorpus':'not_checked','releaseVerified':False,'hostBinarySha256':host_digest,'files':{n:hashlib.sha256((directory/n).read_bytes()).hexdigest() for n in files}}
            path=directory/'candidate.json';path.write_text(json.dumps(receipt));digest=hashlib.sha256(path.read_bytes()).hexdigest()
            promotion.verify(directory,digest,commit)
            (directory/'image.tar').write_bytes(b'changed')
            with self.assertRaises(ValueError):promotion.verify(directory,digest,commit)
            (directory/'image.tar').write_bytes(archive_bytes)
            receipt['status']='failed';path.write_text(json.dumps(receipt));digest=hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):promotion.verify(directory,digest,commit)


class FinalGateTests(unittest.TestCase):
    def fixture(self, directory):
        root=directory/'repo';out=directory/'out';(root/'mcp').mkdir(parents=True);(out/'runtime/bin').mkdir(parents=True)
        binary=out/'runtime/bin/law-mcp-server';binary.write_bytes(b'host')
        self.digest='sha256:'+hashlib.sha256(b'host').hexdigest();self.commit='a'*40
        expected={'platform':'linux-amd64','binarySha256':self.digest,'sourceCommit':self.commit}
        self.lock={'host':{'sourceCommit':self.commit,'platforms':{'linux-amd64':{'binarySha256':self.digest,'sourceCommit':self.commit}}}}
        self.contract={'status':'accepted','acceptance':{'finalHostPin':expected}}
        self.compat={'status':'compatible','platforms':{'linux-amd64':{'status':'compatible','checks':[{'status':'passed'}],'binarySha256':self.digest,'sourceCommit':self.commit}}}
        for name,value in [('runtime.lock.json',self.lock),('runtime-contract.json',self.contract),('host-compatibility.json',self.compat)]:
            (root/'mcp'/name).write_text(json.dumps(value))
        (root/'mcp/cases').mkdir();(root/'mcp/cases/acceptance.json').write_bytes(b'cases');(root/'mcp/source-policy.json').write_bytes(b'policy')
        (out/'offline-smoke.json').write_text(json.dumps({'status':'passed','hostSha256':self.digest.removeprefix('sha256:'),'casesSha256':hashlib.sha256(b'cases').hexdigest(),'sourcePolicySha256':hashlib.sha256(b'policy').hexdigest(),'networkIsolation':'docker --network none','checks':[{'status':'passed'}]}))
        (root/'mcp/tree.pin.json').write_bytes(b'accepted tree');(out/'tree.pin.json').write_bytes(b'accepted tree')
        return root,out

    def test_final_gate_rejects_each_unproven_identity(self):
        spec=importlib.util.spec_from_file_location('build_mcp',Path(__file__).parents[2]/'tools/build_mcp.py')
        build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
        for mutation in ('pending-platform','wrong-host','wrong-source','candidate-contract','changed-tree','changed-binary','floating-source','empty-checks','failed-checks','changed-cases','stale-smoke-host'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                root,out=self.fixture(Path(td));build.final_gate(root,out)
                if mutation=='empty-checks':self.compat['platforms']['linux-amd64']['checks']=[]
                if mutation=='failed-checks':self.compat['platforms']['linux-amd64']['checks'][0]['status']='failed'
                if mutation=='changed-cases':(root/'mcp/cases/acceptance.json').write_bytes(b'different cases')
                if mutation=='stale-smoke-host':
                    smoke=json.loads((out/'offline-smoke.json').read_text());smoke['hostSha256']='wrong';(out/'offline-smoke.json').write_text(json.dumps(smoke))
                if mutation=='pending-platform':self.compat['platforms']['linux-amd64']['status']='not_checked'
                if mutation=='wrong-host':self.compat['platforms']['linux-amd64']['binarySha256']='sha256:wrong'
                if mutation=='wrong-source':self.compat['platforms']['linux-amd64']['sourceCommit']='b'*40
                if mutation=='candidate-contract':self.contract['status']='candidate'
                if mutation=='changed-tree':(out/'tree.pin.json').write_bytes(b'extra file')
                if mutation=='changed-binary':(out/'runtime/bin/law-mcp-server').write_bytes(b'altered')
                if mutation=='floating-source':self.lock['host']['sourceCommit']='main'
                for name,value in [('runtime.lock.json',self.lock),('runtime-contract.json',self.contract),('host-compatibility.json',self.compat)]:
                    (root/'mcp'/name).write_text(json.dumps(value))
                with self.assertRaises(ValueError):build.final_gate(root,out)


class AcquisitionIntegrityTests(unittest.TestCase):
    def test_archive_binary_and_member_identity_fail_closed(self):
        spec=importlib.util.spec_from_file_location('acquire_mcp',Path(__file__).parents[2]/'tools/acquire_mcp.py')
        acquire=importlib.util.module_from_spec(spec);spec.loader.exec_module(acquire)
        for mutation in ('archive-hash','binary-hash','symlink-member','traversal-path'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as td:
                root=Path(td);(root/'mcp').mkdir();buffer=io.BytesIO()
                with tarfile.open(fileobj=buffer,mode='w:gz') as tgz:
                    member=tarfile.TarInfo('package/bin/law-mcp-server');member.size=4
                    if mutation=='symlink-member':member.type=tarfile.SYMTYPE;member.linkname='/foreign';member.size=0
                    tgz.addfile(member,io.BytesIO(b'host') if member.isfile() else None)
                raw=buffer.getvalue();pin={'url':'https://registry.npmjs.org/pinned.tgz','archiveSha256':hashlib.sha256(raw).hexdigest(),'binarySha256':hashlib.sha256(b'host').hexdigest(),'binaryPath':'package/bin/law-mcp-server'}
                if mutation=='archive-hash':pin['archiveSha256']='0'*64
                if mutation=='binary-hash':pin['binarySha256']='0'*64
                if mutation=='traversal-path':pin['binaryPath']='../package/bin/law-mcp-server'
                (root/'mcp/runtime.lock.json').write_text(json.dumps({'host':{'platforms':{'linux-amd64':pin}}}))
                (root/'mcp/build.lock.json').write_text(json.dumps({'builderImage':'python@sha256:'+'0'*64,'baseImage':'debian@sha256:'+'1'*64}))
                with patch.object(acquire.urllib.request,'urlopen',return_value=io.BytesIO(raw)):
                    with self.assertRaises(ValueError):acquire.acquire(root,root/'acquired','linux-amd64',False)


class OCIIdentityTests(unittest.TestCase):
    def identity(self):
        spec=importlib.util.spec_from_file_location('identity',Path(__file__).parents[2]/'tools/mcp_identity.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

    def test_cached_expected_image_cannot_accept_different_archive(self):
        identity=self.identity()
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'image.tar';expected=docker_archive(path)
            wrong=docker_archive(path,b'{"architecture":"amd64","os":"linux","wrong":true}')
            self.assertNotEqual(expected,wrong)
            # A local Docker cache reporting expected does not participate in archive identity.
            with patch('subprocess.check_output',return_value=expected):
                with self.assertRaises(ValueError):identity.archive_image_id(path,expected)

    def test_mutable_tag_race_cannot_change_launch_or_saved_id(self):
        spec=importlib.util.spec_from_file_location('build_identity',Path(__file__).parents[2]/'tools/build_mcp.py')
        build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
        with tempfile.TemporaryDirectory() as td:
            directory=Path(td);id_a=docker_archive(directory/'a.tar');id_b=docker_archive(directory/'b.tar',b'{"other":true}')
            tags={'candidate':id_a};calls=[]
            def fake_run(*args):
                calls.append(args)
                if args[:2]==('docker','build'):
                    Path(args[args.index('--iidfile')+1]).write_text(id_a)
                    tags['candidate']=id_b
                if args[:2]==('docker','save'):
                    selected=tags.get(args[-1],args[-1])
                    Path(args[args.index('--output')+1]).write_bytes((directory/('a.tar' if selected==id_a else 'b.tar')).read_bytes())
            def fake_output(*args):
                calls.append(args);self.assertEqual(args[-1],id_a);return 'container-id'
            with patch.object(build,'run',side_effect=fake_run),patch.object(build,'output',side_effect=fake_output):
                selected=build.build_image(['docker','build','--tag','candidate','context'],directory/'built-image.id')
                self.assertEqual(tags['candidate'],id_b)
                build.start_pinned_container(['docker','run','--read-only'],selected)
                build.save_pinned_image(selected,directory/'saved.tar')
            self.assertEqual(selected,id_a)
            self.assertEqual(self.identity().archive_image_id(directory/'saved.tar',id_a),id_a)

    def test_registry_manifest_must_name_exact_smoked_config(self):
        identity=self.identity();expected='sha256:'+'a'*64
        identity.validate_registry_manifest({'schemaVersion':2,'mediaType':'application/vnd.oci.image.manifest.v1+json','config':{'digest':expected}},expected)
        for manifest in [{'schemaVersion':2,'config':{'digest':'sha256:'+'b'*64}},{'schemaVersion':2,'manifests':[{'digest':expected}]},{'schemaVersion':2}]:
            with self.subTest(manifest=manifest):
                with self.assertRaises(ValueError):identity.validate_registry_manifest(manifest,expected)

    def test_actual_container_policy_fails_each_weakened_boundary(self):
        identity=self.identity();image='sha256:'+'a'*64
        identity.validate_container_policy(policy(image),image)
        mutations=[('NetworkMode','bridge'),('ReadonlyRootfs',False),('Privileged',True),('CapDrop',[]),('CapAdd',['SYS_ADMIN']),('SecurityOpt',[]),('Memory',0),('PidsLimit',129),('NanoCpus',0)]
        for field,value in mutations:
            with self.subTest(field=field):
                document=policy(image);document['HostConfig'][field]=value
                with self.assertRaises(ValueError):identity.validate_container_policy(document,image)
        for mutation in ('fake-json','wrong-image','root-user','external-mount','state-large','state-exec','state-suid','state-device','state-owner','state-mode'):
            with self.subTest(mutation=mutation):
                document=policy(image)
                if mutation=='fake-json':document='accepted'
                if mutation=='wrong-image':document['Image']='sha256:'+'b'*64
                if mutation=='root-user':document['Config']['User']='0:0'
                if mutation=='external-mount':document['Mounts']=[{'Type':'bind','Destination':'/opt/cnaf/runtime','RW':True}]
                changes={'state-large':('64m','65m'),'state-exec':('noexec','exec'),'state-suid':('nosuid','suid'),'state-device':('nodev','dev'),'state-owner':('uid=65532','uid=0'),'state-mode':('0700','0755')}
                if mutation in changes:
                    a,b=changes[mutation];document['HostConfig']['Tmpfs']['/state']=document['HostConfig']['Tmpfs']['/state'].replace(a,b)
                with self.assertRaises(ValueError):identity.validate_container_policy(document,image)


if __name__=='__main__':unittest.main()

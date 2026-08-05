<script setup>
import { computed, onMounted, ref } from "vue";
import { ArrowRight, BookOpen, Building2, ClipboardCheck, Database, ExternalLink, FileWarning, Fingerprint, Gauge, History, LogOut, Menu, Plus, RefreshCw, Search, ShieldCheck, Sparkles, X } from "lucide-vue-next";
import LandingMembrane from "./components/LandingMembrane.vue";
import { connectWallet, contractAddress, explorerUrl, formatError, readContract, writeContract } from "./services/genlayer";

const KEY = "covenant-mesh:wallet-connected";
const authReady=ref(false), connecting=ref(false), authError=ref(""), wallet=ref(null), client=ref(null);
const active=ref("mesh"), mobileNav=ref(false), loading=ref(false), dataError=ref(""), selectedCollection=ref("");
const overview=ref({}), organizations=ref([]), collections=ref([]), requests=ref([]), permits=ref([]), usage=ref([]), audits=ref([]), remediations=ref([]);
const action=ref(null), tx=ref({open:false,stage:"",title:"",hash:"",error:""});
const requestForm=ref({organization_id:"",title:"Community resilience pattern study",purpose:"Study aggregate neighborhood resilience patterns to improve public heat response without identifying individuals or enabling commercial targeting.",methods:"Run privacy-preserving aggregate analysis in an isolated workspace, publish only thresholded statistics, and prevent joins against external identity datasets.",safeguards:"Apply role-based access, encrypted storage, query logging, minimum cohort thresholds, independent review, and verified deletion at the end of retention.",retention_days:30,requested_budget:12});
const createOrgForm=ref({name:"",kind:"RESEARCH",mission:"",jurisdiction:""});
const remediationForm=ref({plan:""});
const usageForm=ref({units:2,purpose_note:"Aggregate model validation under the approved research scope with no row-level export.",artifact_url:"https://github.com/MadBenOfficial/covenant-mesh"});
const auditForm=ref({report:"Access logs show analysis remained within the approved aggregate scope. Export controls were active, minimum cohort thresholds were enforced, and the isolated workspace is scheduled for verified deletion.",evidence_url:"https://github.com/MadBenOfficial/covenant-mesh"});
const short=(v="")=>`${v.slice(0,6)}...${v.slice(-4)}`;
const date=v=>v?new Date(Number(v)*1000).toLocaleDateString("en-GB",{day:"2-digit",month:"short",year:"numeric"}):"Pending";
const collectionById=id=>collections.value.find(x=>x.id===id);
const orgById=id=>organizations.value.find(x=>x.id===id);
const pendingRequests=computed(()=>requests.value.filter(x=>x.status==="PENDING"));
const pendingAudits=computed(()=>audits.value.filter(x=>x.status==="PENDING"));
const activePermits=computed(()=>permits.value.filter(x=>x.status==="ACTIVE"));
const currentCollection=computed(()=>collectionById(selectedCollection.value)||collections.value[0]);
const sameAddress=(a,b)=>String(a||"").toLowerCase()===String(b||"").toLowerCase();
const ownedOrganizations=computed(()=>organizations.value.filter(x=>sameAddress(x.owner,wallet.value)));
const researchOrganizations=computed(()=>ownedOrganizations.value.filter(x=>x.kind==="RESEARCH"));
const hasOrganization=computed(()=>researchOrganizations.value.length>0);
const statusOf=p=>{const now=Math.floor(Date.now()/1000);if(["ACTIVE","EXHAUSTED","AUDIT_OVERDUE","SUSPENDED"].includes(p.status)&&Number(p.expires_at)>0&&now>=Number(p.expires_at))return "EXPIRED";if(p.status==="ACTIVE"&&Number(p.next_audit_due)>0&&now>=Number(p.next_audit_due))return "AUDIT_OVERDUE";return p.status};
const suspendedPermits=computed(()=>permits.value.filter(x=>statusOf(x)==="SUSPENDED"));
const pendingRemediations=computed(()=>remediations.value.filter(x=>x.status==="PENDING"));
const holder=p=>sameAddress(p.holder,wallet.value);

async function restore(){if(localStorage.getItem(KEY)!=="true"){authReady.value=true;return}try{const s=await connectWallet({silent:true});if(s)enter(s);else localStorage.removeItem(KEY)}catch{localStorage.removeItem(KEY)}finally{authReady.value=true}}
async function connect(){connecting.value=true;authError.value="";try{const s=await connectWallet();if(!s)throw new Error("Wallet connection was not approved.");localStorage.setItem(KEY,"true");enter(s)}catch(e){authError.value=formatError(e)}finally{connecting.value=false;authReady.value=true}}
function enter(s){wallet.value=s.address;client.value=s.client;load()}
function disconnect(){localStorage.removeItem(KEY);wallet.value=null;client.value=null}
async function load(){loading.value=true;dataError.value="";try{const v=[];for(const name of ["get_overview","get_organizations","get_collections","get_requests","get_permits","get_usage","get_audits","get_remediations"])v.push(await readContract(name));[overview.value,organizations.value,collections.value,requests.value,permits.value,usage.value,audits.value,remediations.value]=v;if(!selectedCollection.value&&collections.value.length)selectedCollection.value=collections.value[0].id;const mine=organizations.value.find(x=>sameAddress(x.owner,wallet.value)&&x.kind==="RESEARCH");if(mine&&!researchOrganizations.value.some(x=>x.id===requestForm.value.organization_id))requestForm.value.organization_id=mine.id}catch(e){dataError.value=formatError(e)}finally{loading.value=false}}
async function transact(title,functionName,args){tx.value={open:true,stage:"signature",title,hash:"",error:"",status:""};try{const r=await writeContract({client:client.value,functionName,args,onStage:(stage,hash,status)=>{tx.value.stage=stage;if(hash)tx.value.hash=hash;if(status)tx.value.status=status}});tx.value.hash=r.hash;tx.value.stage="accepted";tx.value.status=r.receipt?.statusName||"FINALIZED";action.value=null;await load()}catch(e){if(e?.hash)tx.value.hash=e.hash;tx.value.stage="failed";tx.value.status=e?.receipt?.statusName||"ROLLBACK";tx.value.error=formatError(e)}}
const submitRequest=()=>{const selected=researchOrganizations.value.find(x=>x.id===requestForm.value.organization_id);if(!selected){createOrgForm.value.kind="RESEARCH";action.value="createOrg";return}return transact("Submit access request","submit_access_request",[selected.id,currentCollection.value.id,requestForm.value.title,requestForm.value.purpose,requestForm.value.methods,requestForm.value.safeguards,Number(requestForm.value.retention_days),Number(requestForm.value.requested_budget)])};
const createOrganization=()=>transact("Create organization","create_organization",[createOrgForm.value.name,createOrgForm.value.kind,createOrgForm.value.mission,createOrgForm.value.jurisdiction]);
const resolveRequest=id=>transact("Validators evaluate access","resolve_access_request",[id]);
const recordUsage=p=>transact("Record privacy budget use","record_usage",[p.id,Number(usageForm.value.units),usageForm.value.purpose_note,usageForm.value.artifact_url]);
const submitAudit=p=>transact("Submit compliance audit","submit_audit",[p.id,auditForm.value.report,auditForm.value.evidence_url]);
const resolveAudit=id=>transact("Validators resolve audit","resolve_audit",[id]);
const syncPermit=id=>transact("Enforce permit schedule","sync_permit_status",[id]);
const submitRemediation=p=>transact("Submit remediation plan","submit_remediation",[p.id,remediationForm.value.plan]);
const resolveRemediation=id=>transact("Validators evaluate remediation","resolve_remediation",[id]);
onMounted(restore);
</script>

<template>
  <div v-if="!authReady" class="boot"><Fingerprint :size="32"/><span>Restoring permission layer</span></div>
  <LandingMembrane v-else-if="!wallet" :busy="connecting" :error="authError" @connect="connect"/>
  <div v-else class="workspace">
    <header class="app-head">
      <button class="mobile-trigger" title="Open navigation" @click="mobileNav=!mobileNav"><Menu/></button>
      <a class="brand" href="#" @click.prevent="active='mesh'"><span>CM</span><strong>Covenant<br>Mesh</strong></a>
      <nav :class="{open:mobileNav}">
        <button :class="{active:active==='mesh'}" @click="active='mesh';mobileNav=false"><Database/> Mesh</button>
        <button :class="{active:active==='requests'}" @click="active='requests';mobileNav=false"><Search/> Requests <b>{{pendingRequests.length}}</b></button>
        <button :class="{active:active==='permits'}" @click="active='permits';mobileNav=false"><ShieldCheck/> Permits</button>
        <button :class="{active:active==='compliance'}" @click="active='compliance';mobileNav=false"><ClipboardCheck/> Compliance <b>{{pendingAudits.length}}</b></button>
      </nav>
      <div class="head-actions">
        <select v-if="researchOrganizations.length" v-model="requestForm.organization_id" class="org-select" title="Research organization"><option v-for="org in researchOrganizations" :key="org.id" :value="org.id">{{org.name}}</option></select>
        <button title="Create organization" @click="action='createOrg'"><Plus/></button>
        <a :href="`${explorerUrl}/address/${contractAddress}`" target="_blank" title="Open contract"><ExternalLink/></a>
        <button title="Refresh StudioNet data" :class="{spin:loading}" @click="load"><RefreshCw/></button>
        <button class="wallet-button" title="Disconnect wallet" @click="disconnect"><i></i>{{short(wallet)}}<LogOut/></button>
      </div>
    </header>
    <main>
      <div v-if="dataError" class="error-strip"><FileWarning/>{{dataError}}<button @click="load">Retry</button></div>
      <div v-if="loading&&!collections.length" class="data-loader"><div class="consensus-orbit"><span></span><i></i><b></b></div><strong>Reading the live covenant ledger</strong><small>StudioNet state is being verified.</small></div>
      <section v-else-if="!hasOrganization" class="onboarding-band"><Building2/><div><small>ORGANIZATION ONBOARDING</small><h2>Create your accountable identity.</h2><p>Requests and permits belong to an on-chain organization controlled by your connected wallet.</p></div><button class="primary" @click="action='createOrg'">Create organization <ArrowRight/></button></section>
      <template v-if="active==='mesh'">
        <section class="page-intro"><div><p class="eyebrow">LIVE COLLECTIVE PERMISSION GRAPH</p><h1>Data has<br><em>conditions.</em></h1></div><p>Each line is an enforceable relationship between a stewarded collection and a research organization. Consensus determines whether purpose, method, safeguards, and budget remain aligned.</p></section>
        <section class="metric-ribbon">
          <span><b>{{overview.collections||collections.length}}</b> collections</span><span><b>{{overview.active_permits||activePermits.length}}</b> active permits</span>
          <span><b>{{overview.budget_allocated||0}}</b> units allocated</span><span><b>{{overview.budget_consumed||0}}</b> units consumed</span><span class="live"><i></i> StudioNet synced</span>
        </section>
        <section class="mesh-board">
          <aside><p class="section-label">STEWARD COVENANTS</p><button v-for="item in collections" :key="item.id" :class="{selected:currentCollection?.id===item.id}" @click="selectedCollection=item.id"><span>{{item.id}}</span><strong>{{item.title}}</strong><small>{{item.domain}} / {{item.sensitivity}}</small></button></aside>
          <article v-if="currentCollection" class="covenant-sheet">
            <header><span>{{currentCollection.id}} / {{currentCollection.sensitivity}}</span><b>{{currentCollection.available_budget}} of {{currentCollection.total_budget}} budget available</b></header>
            <h2>{{currentCollection.title}}</h2><p class="lede">{{currentCollection.description}}</p>
            <div class="policy-line allowed"><ShieldCheck/><div><small>ALLOWED PURPOSES</small><p>{{currentCollection.allowed_purposes}}</p></div></div>
            <div class="policy-line blocked"><X/><div><small>PROHIBITED USES</small><p>{{currentCollection.prohibited_uses}}</p></div></div>
            <div class="policy-line guard"><Fingerprint/><div><small>REQUIRED SAFEGUARDS</small><p>{{currentCollection.required_safeguards}}</p></div></div>
          <footer><span>Retention ceiling {{currentCollection.max_retention_days}} days</span><span>Audit every {{currentCollection.audit_interval_days}} days</span><button :disabled="!hasOrganization" @click="action='request'">Request bounded access <ArrowRight/></button></footer>
          </article>
          <aside class="org-rail"><p class="section-label">PARTICIPANTS</p><div v-for="org in organizations" :key="org.id" class="org"><span>{{org.kind}}</span><strong>{{org.name}}</strong><small>{{org.jurisdiction}} · reputation {{org.reputation}}</small></div></aside>
        </section>
      </template>
      <template v-else-if="active==='requests'">
        <section class="page-intro"><div><p class="eyebrow">CONSENSUS INBOX</p><h1>Access<br><em>requests.</em></h1></div><button class="primary" :disabled="!hasOrganization" @click="action='request'"><Sparkles/> New request</button></section>
        <section class="list-table"><div class="table-head"><span>Request</span><span>Collection</span><span>Budget</span><span>Risk / verdict</span><span>Status</span><span></span></div>
          <article v-for="item in requests" :key="item.id">
            <span><small>{{item.id}}</small><strong>{{item.title}}</strong></span><span><small>{{item.collection_id}}</small>{{collectionById(item.collection_id)?.title}}</span><span class="numeric">{{item.requested_budget}}</span>
            <span>{{item.verdict||"Awaiting evaluation"}}<small v-if="item.risk_score">{{item.risk_score}}/100 risk</small></span><span><i :class="`status ${item.status.toLowerCase()}`"></i>{{item.status}}</span>
            <button v-if="item.status==='PENDING'" title="Run intelligent consensus" @click="resolveRequest(item.id)"><Sparkles/> Run consensus</button><button v-else title="View analysis" @click="action=item"><BookOpen/></button>
          </article>
        </section>
      </template>
      <template v-else-if="active==='permits'">
        <section class="page-intro"><div><p class="eyebrow">BOUNDED RIGHTS</p><h1>Active<br><em>permits.</em></h1></div><p>Every recorded use consumes the permission envelope written by validators. Rights can be audited, suspended, restored, or revoked.</p></section>
        <section class="permit-grid"><article v-for="p in permits" :key="p.id">
          <header><span>{{p.id}}</span><i :class="`status ${statusOf(p).toLowerCase()}`"></i>{{statusOf(p)}}</header><h2>{{collectionById(p.collection_id)?.title}}</h2><p>{{orgById(p.organization_id)?.name}}</p>
          <div class="gauge"><span :style="{width:`${(p.consumed_budget/p.allocated_budget)*100}%`}"></span></div><div class="permit-numbers"><strong>{{p.consumed_budget}} / {{p.allocated_budget}}</strong><small>privacy units consumed</small></div>
          <dl><dt>Issued</dt><dd>{{date(p.issued_at)}}</dd><dt>Expires</dt><dd :class="{warn:statusOf(p)==='EXPIRED'}">{{date(p.expires_at)}}</dd><dt>Next audit</dt><dd :class="{warn:statusOf(p)==='AUDIT_OVERDUE'}">{{date(p.next_audit_due)}}</dd></dl>
          <footer><button :disabled="statusOf(p)!=='ACTIVE'||!holder(p)" @click="action={type:'usage',permit:p}"><Gauge/> Record use</button><button :disabled="!['ACTIVE','EXHAUSTED','AUDIT_OVERDUE'].includes(statusOf(p))||!holder(p)" @click="action={type:'audit',permit:p}"><ClipboardCheck/> Submit audit</button><button v-if="statusOf(p)!==p.status" @click="syncPermit(p.id)"><RefreshCw/> Enforce</button></footer>
        </article></section>
        <section v-if="suspendedPermits.length" class="remediation-stream"><header><small>RECOVERY PATH</small><h2>Suspended permits</h2></header><article v-for="p in suspendedPermits" :key="p.id"><div><small>{{p.id}}</small><strong>{{orgById(p.organization_id)?.name}}</strong><p>{{p.conditions}}</p></div><button v-if="holder(p)&&!pendingRemediations.some(r=>r.permit_id===p.id)" @click="action={type:'remediation',permit:p}"><History/> Submit remediation</button><span v-else>Awaiting remediation</span></article></section>
      </template>
      <template v-else>
        <section class="page-intro"><div><p class="eyebrow">ACCOUNTABILITY LEDGER</p><h1>Compliance<br><em>signals.</em></h1></div><p>Audits preserve, warn, suspend, or revoke access. The result changes permit rights and organization reputation on-chain.</p></section>
        <section class="audit-stream"><article v-for="item in audits" :key="item.id">
          <div class="audit-code"><ClipboardCheck/><strong>{{item.id}}</strong><span>{{date(item.submitted_at)}}</span></div><div><small>{{item.permit_id}} / {{orgById(item.organization_id)?.name}}</small><p>{{item.report}}</p><a :href="item.evidence_url" target="_blank">Inspect evidence <ExternalLink/></a></div>
          <div class="audit-result"><span>{{item.outcome||"PENDING"}}</span><strong>{{item.compliance_score||"—"}}</strong><small>compliance score</small></div><button v-if="item.status==='PENDING'" @click="resolveAudit(item.id)"><Sparkles/> Resolve audit</button>
        </article><div v-if="!audits.length" class="empty">No compliance reports yet.</div></section>
        <section class="remediation-stream"><header><small>REMEDIATION LEDGER</small><h2>Corrective actions</h2></header><article v-for="item in remediations" :key="item.id"><div><small>{{item.id}} / {{item.permit_id}}</small><strong>{{item.decision||'PENDING'}}</strong><p>{{item.plan}}</p><p v-if="item.analysis">{{item.analysis}}</p></div><button v-if="item.status==='PENDING'" @click="resolveRemediation(item.id)"><Sparkles/> Run consensus</button></article><div v-if="!remediations.length" class="empty">No remediation plans have been submitted.</div></section>
      </template>
    </main>
    <div v-if="action" class="modal-backdrop" @click.self="action=null">
      <section v-if="action==='createOrg'" class="modal compact">
        <header><div><small>ON-CHAIN IDENTITY</small><h2>Create an organization.</h2></div><button @click="action=null"><X/></button></header>
        <label>Organization name<input v-model="createOrgForm.name" placeholder="Civic Systems Lab"></label><label>Organization role<select v-model="createOrgForm.kind"><option value="RESEARCH">Research organization</option></select></label>
        <label>Mission<textarea v-model="createOrgForm.mission" rows="4" placeholder="Describe the public purpose and operating mandate."></textarea></label><label>Jurisdiction<input v-model="createOrgForm.jurisdiction" placeholder="European Union"></label>
        <button class="primary wide" :disabled="createOrgForm.name.length<3||createOrgForm.mission.length<30||createOrgForm.jurisdiction.length<2" @click="createOrganization">Create on StudioNet <ArrowRight/></button>
      </section>
      <section v-else-if="action==='request'" class="modal">
        <header><div><small>NEW ACCESS REQUEST</small><h2>Ask with precision.</h2></div><button @click="action=null"><X/></button></header>
        <label>Requesting research organization<select v-model="requestForm.organization_id"><option v-for="org in researchOrganizations" :key="org.id" :value="org.id">{{org.name}} · {{org.kind}}</option></select></label><label>Collection<select v-model="selectedCollection"><option v-for="item in collections" :value="item.id">{{item.title}} · {{item.available_budget}} units</option></select></label><label>Research title<input v-model="requestForm.title"></label>
        <label>Purpose<textarea v-model="requestForm.purpose"></textarea></label><div class="form-pair"><label>Retention days<input v-model.number="requestForm.retention_days" type="number"></label><label>Requested budget<input v-model.number="requestForm.requested_budget" type="number"></label></div>
        <label>Methods<textarea v-model="requestForm.methods"></textarea></label><label>Safeguards<textarea v-model="requestForm.safeguards"></textarea></label><button class="primary wide" @click="submitRequest">Submit on StudioNet <ArrowRight/></button>
      </section>
      <section v-else-if="action.type==='usage'" class="modal compact"><header><div><small>{{action.permit.id}}</small><h2>Record bounded use.</h2></div><button @click="action=null"><X/></button></header><label>Units consumed<input v-model.number="usageForm.units" type="number"></label><label>Purpose note<textarea v-model="usageForm.purpose_note"></textarea></label><label>Public artifact URL<input v-model="usageForm.artifact_url"></label><button class="primary wide" @click="recordUsage(action.permit)">Write checkpoint <ArrowRight/></button></section>
      <section v-else-if="action.type==='audit'" class="modal compact"><header><div><small>{{action.permit.id}}</small><h2>Submit an audit.</h2></div><button @click="action=null"><X/></button></header><label>Compliance report<textarea v-model="auditForm.report" rows="6"></textarea></label><label>Evidence URL<input v-model="auditForm.evidence_url"></label><button class="primary wide" @click="submitAudit(action.permit)">Submit report <ArrowRight/></button></section>
      <section v-else-if="action.type==='remediation'" class="modal compact"><header><div><small>{{action.permit.id}}</small><h2>Repair the covenant.</h2></div><button @click="action=null"><X/></button></header><p>Identify corrective actions, accountable owners, deadlines, containment or deletion evidence, and future monitoring.</p><label>Remediation plan<textarea v-model="remediationForm.plan" rows="7"></textarea></label><button class="primary wide" :disabled="remediationForm.plan.length<100" @click="submitRemediation(action.permit)">Submit remediation <ArrowRight/></button></section>
      <section v-else class="modal compact detail"><header><div><small>{{action.id}}</small><h2>{{action.verdict}}</h2></div><button @click="action=null"><X/></button></header><p>{{action.analysis}}</p><div><small>CONDITIONS</small><p>{{action.conditions}}</p></div></section>
    </div>
    <div v-if="tx.open" class="tx-panel"><button v-if="['accepted','failed'].includes(tx.stage)" class="tx-close" @click="tx.open=false"><X/></button><div class="consensus-orbit" :class="tx.stage"><span></span><i></i><b></b></div><small>GENLAYER STUDIO NET · {{tx.status||tx.stage}}</small><h3 v-if="tx.stage==='accepted'">Transaction applied</h3><h3 v-else-if="tx.stage==='failed'">Transaction rolled back</h3><h3 v-else>{{tx.title}}</h3><p v-if="tx.stage==='signature'">Confirm the transaction in your wallet.</p><p v-else-if="tx.stage==='consensus'">Validators are interpreting covenant, purpose, and evidence.</p><p v-else-if="tx.stage==='accepted'">Success. The live permission ledger now includes this action.</p><p v-else>{{tx.error}}</p><a v-if="tx.hash" :href="`${explorerUrl}/tx/${tx.hash}`" target="_blank">{{short(tx.hash)}} <ExternalLink/></a></div>
  </div>
</template>

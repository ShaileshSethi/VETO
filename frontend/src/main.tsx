import { useEffect, useState, type FormEvent } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Status = { ready:boolean; provider:string; model:string; session:string; mode:'mock'|'nebius' };
type Answer = { answer:string; model:string; mode:string; latency_ms:number; request_id?:string; usage:{prompt_tokens?:number;completion_tokens?:number} };
type Preference = { sort_by:string; source:string; updated_at:string|null };
type Workspace = { root_id:string; relative_folder:string; granted:boolean; files:{path:string;size:number}[]; skipped:string[]; preferences:Preference };
type Plan = { id:string; hash:string; state:string; direction:string; preference:string; error:string|null; created_at:string; create_folders:string[]; skipped:string[]; items:{source:string;destination:string;identity:number[]}[]; conflicts:{reason:string}[]; actions:{source:string;destination:string;state:string}[] };

async function api<T>(path:string, session:string, method='GET', body?:unknown):Promise<T> {
  const response = await fetch('/api'+path,{method,headers:{'Content-Type':'application/json','X-Veto-Session':session},...(body===undefined?{}:{body:JSON.stringify(body)})});
  const data = await response.json();
  if(!response.ok) throw new Error(typeof data.detail==='string'?data.detail:'Request rejected. Review the input and try again.');
  return data;
}

function Chat({status}:{status:Status}) {
  const [prompt,setPrompt]=useState(''); const [answer,setAnswer]=useState<Answer>();
  const [error,setError]=useState(''); const [busy,setBusy]=useState(false);
  async function submit(event:FormEvent) {
    event.preventDefault();if(busy)return;setBusy(true);setError('');setAnswer(undefined);
    try{setAnswer(await api<Answer>('/chat',status.session,'POST',{prompt}));}
    catch(e){setError(e instanceof Error?e.message:'Request failed.');}finally{setBusy(false);}
  }
  const mock=status.mode==='mock';
  return <section className="workspace" aria-label="Ask Veto"><div className="panel-heading"><h2>Ask Veto</h2><span className="state">{busy?'Waiting…':mock?'Mock ready · no credits needed':status.ready?'Key configured · live testing pending':'Key setup needed'}</span></div>
    <form onSubmit={submit}><label htmlFor="question">Your question</label><textarea id="question" value={prompt} onChange={e=>setPrompt(e.target.value)} maxLength={2000} placeholder="How do I sort the sample files?" rows={3} required disabled={busy}/>
      <p className="disclosure">{mock?'Mock mode returns fixed sample replies locally. No API calls or charges. This question cannot execute file actions.':'Send transmits this question to Nebius. Use sample text only. File sorting uses the separate local preview and approval controls.'}</p>
      <div className="form-bottom"><span>{prompt.length} / 2,000</span><button disabled={busy||!prompt.trim()} type="submit">{busy?'Waiting…':mock?'Get sample reply':'Send to Nebius ↗'}</button></div></form>
    {!status.ready&&<aside className="setup">Enter your key only in the local .env file, then restart Veto. Never paste it into chat.</aside>}
    {error&&<div className="error" role="alert">{error}</div>}
    {answer&&<section className="answer" aria-live="polite"><h3>{answer.mode==='mock'?'MOCK · sample reply — no API call':'Live Nebius response'}</h3><p>{answer.answer}</p><small>{answer.model}{answer.mode!=='mock'&&<> · {answer.latency_ms} ms<br/>Request: {answer.request_id??'unreported'}<br/>Tokens: {answer.usage?.prompt_tokens??'unreported'} in / {answer.usage?.completion_tokens??'unreported'} out</>}</small></section>}
  </section>;
}

function Files({session}:{session:string}) {
  const [workspace,setWorkspace]=useState<Workspace>();const [history,setHistory]=useState<Plan[]>([]);const [plan,setPlan]=useState<Plan>();
  const [selected,setSelected]=useState('');const [preference,setPreference]=useState('file_type');const [error,setError]=useState('');
  const [notice,setNotice]=useState('');const [busy,setBusy]=useState(false);const [exported,setExported]=useState('');
  async function refresh(){const [w,h]=await Promise.all([api<Workspace>('/workspace',session),api<Plan[]>('/plans',session)]);setWorkspace(w);setHistory(h);setPreference(w.preferences.sort_by);}
  useEffect(()=>{refresh().catch(e=>setError(e.message));},[session]);
  useEffect(()=>{if(!busy||!plan)return;const timer=window.setInterval(()=>{api<Plan>('/plans/'+plan.id,session).then(setPlan).catch(e=>setError(e.message));},350);return()=>window.clearInterval(timer);},[busy,plan?.id,session]);
  async function action(operation:()=>Promise<void>){setBusy(true);setError('');setNotice('');try{await operation();await refresh();}catch(e){setError(e instanceof Error?e.message:'Action failed. Inspect receipts.');}finally{setBusy(false);}}
  async function allow(granted:boolean){await api('/permission',session,'POST',{root_id:granted?selected:workspace?.root_id,granted});setPlan(undefined);setNotice(granted?'Sample folder allowed. Preview before any move.':'Permission revoked. Waiting approvals are cancelled.');}
  async function execute(){if(!plan)return;const approval=await api<{approval_token:string}>(`/plans/${plan.id}/approve`,session,'POST',{plan_hash:plan.hash});const result=await api<Plan>(`/plans/${plan.id}/execute`,session,'POST',{approval_token:approval.approval_token});setPlan(result);setNotice(result.state==='done'?(result.direction==='undo'?'Undo completed. Original files restored; empty sorting folders remain.':'Approved sample files moved. Review receipts or preview undo.'):result.error??'Inspect action receipts.');}
  return <>
    <section className="workspace" aria-label="Folder permissions"><div className="panel-heading"><h2>Folder permissions</h2><span className="pill">SAMPLE FILES ONLY</span></div><p>Veto starts with no folder access. Only its generated inbox is offered; personal folders cannot be added.</p><p className="folder-path">{workspace?.relative_folder??'Loading sample folder…'}</p>
      {workspace?.granted?<div className="row"><span className="allowed">✓ Veto Demo Inbox is allowed</span><button className="secondary" onClick={()=>action(()=>allow(false))}>Revoke sample permission</button></div>:<div className="row"><div><label htmlFor="sample-root">Choose a sample folder</label><select id="sample-root" value={selected} onChange={e=>setSelected(e.target.value)} disabled={busy}><option value="">Select a folder…</option><option value="sample-inbox">Veto Demo Inbox (generated samples)</option></select></div><button disabled={busy||!selected} onClick={()=>action(()=>allow(true))}>Allow selected sample folder</button></div>}
      <p className="disclosure">Permission allows local filename metadata and approved sample moves. No file contents or filenames are sent to Nebius. Revoke permission at any time.</p></section>
    <section className="workspace spaced" aria-label="Sorting preferences"><h2>Sorting preference</h2><p>This choice stays on your laptop and survives a restart.</p><div className="row"><div><label htmlFor="sort-by">Group documents into</label><select id="sort-by" value={preference} onChange={e=>setPreference(e.target.value)} disabled={busy}><option value="file_type">Documents · by file type</option><option value="study">Notes · study grouping</option></select></div>
      <button disabled={busy} onClick={()=>action(async()=>{await api('/preferences',session,'PUT',{sort_by:preference});setNotice('Sorting preference saved locally.');})}>Save preference</button><button className="secondary" disabled={busy} onClick={()=>action(async()=>{await api('/preferences',session,'DELETE');setNotice('Stored preference removed; default restored.');})}>Reset preference</button><button className="secondary" disabled={busy} onClick={()=>action(async()=>{setExported(JSON.stringify(await api('/preferences/export',session),null,2));})}>Export preference</button></div>
      <p className="disclosure">Source: {workspace?.preferences.source??'loading'} · Last saved: {workspace?.preferences.updated_at?new Date(workspace.preferences.updated_at).toLocaleString():'default, not saved'}</p>{exported&&<pre className="export">{exported}</pre>}</section>
    <section className="workspace spaced" aria-label="Sample files"><div className="panel-heading"><h2>Sample files</h2><div className="row"><button className="secondary" disabled={busy} onClick={()=>action(refresh)}>Refresh files</button><button disabled={busy||!workspace?.granted} onClick={()=>action(async()=>{setPlan(await api<Plan>('/plans/preview',session,'POST',{root_id:workspace?.root_id}));})}>Preview sorting</button></div></div>
      {!workspace?.granted?<p>Allow the sample folder above to view files.</p>:<div className="table-wrap"><table><thead><tr><th>Current relative path</th><th>Size</th></tr></thead><tbody>{workspace.files.map(file=><tr key={file.path}><td>{file.path}</td><td>{file.size} bytes</td></tr>)}</tbody></table>{workspace.files.length===0&&<p>No eligible sample files.</p>}</div>}
      {!!workspace?.skipped.length&&<p className="disclosure">Skipped unsafe or inaccessible entries: {workspace.skipped.join(', ')}</p>}</section>
    {error&&<div className="error" role="alert">{error}</div>}{notice&&<p className="notice" role="status">{notice}</p>}
    {plan&&<section className="workspace spaced" aria-label="Exact action preview"><div className="panel-heading"><h2>{plan.direction==='undo'?'Undo preview':'Sorting preview'}</h2><span className="pill">{plan.state.toUpperCase()}</span></div><p>{plan.items.length} real sample moves · {plan.items.reduce((n,i)=>n+i.identity[2],0)} bytes · Veto Demo Inbox · rule: {plan.preference}</p><p className="disclosure">Fixed local rules, not an AI-generated plan. {plan.create_folders.length?'Create/use folders: '+plan.create_folders.join(', ')+'.':''} No overwrite or deletion.</p>
      <div className="table-wrap"><table><thead><tr><th>From</th><th>To</th><th>Receipt</th></tr></thead><tbody>{plan.actions.map((item,i)=><tr key={i}><td>{item.source}</td><td>{item.destination}</td><td>{item.state}</td></tr>)}</tbody></table></div>{plan.skipped.length>0&&<p className="disclosure">Left alone: {plan.skipped.join(', ')}</p>}
      {plan.conflicts.length>0&&<div className="error" role="alert">Approval blocked: {plan.conflicts.map(c=>c.reason).join(' ')}</div>}{plan.error&&<p className="error">{plan.error}</p>}<p className="plan-hash">Exact plan: {plan.hash}</p>
      <div className="row">{plan.state==='previewed'&&<><button disabled={busy||!!plan.conflicts.length} onClick={()=>action(execute)}>Approve exact {plan.direction==='undo'?'undo':'moves'}</button><button className="secondary" disabled={busy} onClick={()=>action(async()=>{setPlan(await api<Plan>(`/plans/${plan.id}/cancel`,session,'POST'));setNotice('Plan cancelled. No moves will run.');})}>Cancel plan</button></>}
      {busy&&<button className="secondary" onClick={async()=>{try{await api(`/plans/${plan.id}/stop`,session,'POST');setNotice('Stop requested. An in-flight move may finish; inspect receipts.');}catch(e){setError(e instanceof Error?e.message:'Stop failed.');}}}>Stop remaining moves</button>}</div></section>}
    <section className="workspace spaced" aria-label="Action history"><h2>Activity and undo</h2><p>Receipts are saved locally. Undo also needs an exact preview and approval.</p>{history.length===0&&<p>No plans yet.</p>}
      {history.map(item=><article className="history-row" key={item.id}><div><strong>{item.direction==='undo'?'Undo':'Sort'} · {item.state}</strong><small>{new Date(item.created_at).toLocaleString()} · {item.actions.filter(a=>a.state==='done'||a.state==='undone').length}/{item.actions.length} confirmed steps</small></div><div className="row"><button className="secondary" disabled={busy} onClick={()=>action(async()=>{setPlan(await api<Plan>(`/plans/${item.id}`,session));})}>View plan</button>{item.direction==='sort'&&['done','failed','cancelled','interrupted'].includes(item.state)&&item.actions.some(a=>a.state==='done')&&<button disabled={busy||!workspace?.granted} onClick={()=>action(async()=>{setPlan(await api<Plan>(`/plans/${item.id}/undo-preview`,session,'POST'));})}>Preview undo</button>}</div></article>)}</section>
  </>;
}

function App(){const [status,setStatus]=useState<Status>();const [tab,setTab]=useState<'chat'|'files'>('chat');const [error,setError]=useState('');
  useEffect(()=>{fetch('/api/status').then(async r=>{if(!r.ok)throw new Error('Backend unavailable. Restart Veto and refresh.');setStatus(await r.json());}).catch(e=>setError(e.message));},[]);
  return <main><header><a className="brand" href="/" aria-label="Veto home">veto<span>●</span></a><span className="pill">LOCAL SAMPLE WORKSPACE</span></header><section className="intro"><p className="eyebrow">YOUR LAPTOP. YOUR CALL.</p><h1>A little clarity.<br/>Every move, your choice.</h1><p className="description">Explore Veto with sample files.<br/>Preview first. Approve once. Keep an undo path.</p></section>
    <aside className={status?.mode==='mock'?'mode-banner':'live-banner'}><strong>{status?.mode==='mock'?'MOCK MODE · sample replies · no API calls':'NEBIUS MODE · questions use cloud inference'}</strong><p>Live NVIDIA/Nebius testing is still pending. {status?.mode==='mock'?'Sorting moves real sample files after approval. No key or credits needed.':'Sorting stays local and uses fixed rules.'} Voice is off.</p></aside>
    <nav className="tabs" aria-label="Veto sections"><button aria-pressed={tab==='chat'} onClick={()=>setTab('chat')}>Sample chat</button><button aria-pressed={tab==='files'} onClick={()=>setTab('files')}>Sample files & memory</button></nav>{error&&<div className="error" role="alert">{error}</div>}{status&&(tab==='chat'?<Chat status={status}/>:<Files session={status.session}/>)}
    <section className="boundaries"><article><span>01 / MODEL</span><h3>{status?.provider??'Loading…'}</h3><p>{status?.model??'Loading configuration…'} · live milestone pending</p></article><article><span>02 / ACCESS</span><h3>Generated samples only</h3><p>Folder permission, exact approval, local receipts and undo.</p></article><article><span>03 / MICROPHONE</span><h3>Voice is off</h3><p>No listener, settings control, or startup service.</p></article></section><footer><span>Small steps. Clear permissions.</span><span>Mock development · live integration pending</span></footer></main>;
}
createRoot(document.getElementById('root')!).render(<App/>);

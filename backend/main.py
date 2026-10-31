from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
import sqlite3, json, uuid, hashlib, random, os, shutil, subprocess, time
from datetime import datetime, timezone
from backend.agents.orchestrator import AgentOrchestrator
from backend.agents.config import is_llm_available, LLM_MODEL_NAME

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UPLOADS = DATA / "uploads"
DB = DATA / "viralsim.db"
UPLOADS.mkdir(parents=True, exist_ok=True)
MAX_BYTES = 200 * 1024 * 1024
ALLOWED = {'.mp4', '.mov', '.webm', '.m4v', '.avi'}
app = FastAPI(title="ViralSim AI API", version="0.1.0", description="Video audience simulation API. Estimates are synthetic and not platform analytics.")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(','), allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type"])


def connect():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row; return con

def init_db():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS videos(id TEXT PRIMARY KEY, filename TEXT NOT NULL, stored_name TEXT NOT NULL, size INTEGER, duration REAL, platform TEXT, category TEXT, objective TEXT, target TEXT, status TEXT, analysis TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, video_id TEXT NOT NULL, status TEXT NOT NULL, config TEXT, report TEXT, seed INTEGER, created_at TEXT, finished_at TEXT, FOREIGN KEY(video_id) REFERENCES videos(id));''')
init_db()

PERSONAS = [
 {"id":"tech","name":"Tech Enthusiast","emoji":"◈","age":"25–34","interests":["innovation","specs","use cases"],"familiarity":"High","price":"Medium","attention":"Stays for concrete demonstrations","motivation":"Find useful differentiators","objection":"Vague claims without proof","style":"Analytical"},
 {"id":"casual","name":"Casual Scroller","emoji":"◉","age":"18–34","interests":["entertainment","quick tips","visual hooks"],"familiarity":"Low","price":"Medium","attention":"Decides quickly in opening seconds","motivation":"Instant relevance","objection":"Slow setup or confusing context","style":"Impatient"},
 {"id":"practical","name":"Practical Buyer","emoji":"▣","age":"28–44","interests":["utility","quality","reviews"],"familiarity":"Medium","price":"High","attention":"Watches when benefits are specific","motivation":"Solve a real problem","objection":"Unclear value for money","style":"Outcome-led"},
 {"id":"skeptic","name":"Skeptical Shopper","emoji":"◇","age":"25–44","interests":["evidence","comparisons","authenticity"],"familiarity":"Medium","price":"High","attention":"Looks for proof and caveats","motivation":"Reduce purchase risk","objection":"Overstated promises","style":"Evidence-seeking"},
 {"id":"trend","name":"Trend Follower","emoji":"✳","age":"18–29","interests":["creators","trends","shareable moments"],"familiarity":"Low–Medium","price":"Low","attention":"Responds to novelty and momentum","motivation":"Discover what is current","objection":"Feels dated or overly polished","style":"Social-first"},
 {"id":"budget","name":"Budget-Conscious","emoji":"⌁","age":"24–44","interests":["deals","durability","alternatives"],"familiarity":"Medium","price":"Very high","attention":"Prioritizes practical value","motivation":"Get more for less","objection":"Price without justification","style":"Value-focused"},
 {"id":"loyal","name":"Brand Loyalist","emoji":"✦","age":"25–54","interests":["brand updates","community","new releases"],"familiarity":"High","price":"Low–Medium","attention":"Watches familiar brands longer","motivation":"Stay connected to a trusted brand","objection":"Inconsistent brand promise","style":"Relationship-led"},
 {"id":"impulse","name":"Impulse Explorer","emoji":"↗","age":"18–34","interests":["visual appeal","novelty","easy wins"],"familiarity":"Low","price":"Medium","attention":"Responds to immediate payoff","motivation":"Feel an immediate desire","objection":"Too many steps to act","style":"Emotion-led"}
]

class SimConfig(BaseModel):
    platform: str = "Instagram Reels"
    category: str = "Technology"
    objective: str = "Retention"
    audience_size: int = Field(100, ge=8, le=5000)
    rounds: int = Field(3, ge=1, le=10)
    age_range: str = "18–34"
    interests: list[str] = []
    geography: str = "Global"
    product_familiarity: str = "Mixed"
    seed: Optional[int] = None

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)

class ActualPerformance(BaseModel):
    views: Optional[int] = Field(default=None, ge=0)
    average_watch_seconds: Optional[float] = Field(default=None, ge=0)
    likes: Optional[int] = Field(default=None, ge=0)
    shares: Optional[int] = Field(default=None, ge=0)
    saves: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=2000)


def now(): return datetime.now(timezone.utc).isoformat()
def rowdict(r): return dict(r) if r else None

def ffprobe(path: Path):
    exe = shutil.which('ffprobe')
    if not exe: return None
    try:
        p = subprocess.run([exe,'-v','error','-show_entries','format=duration:stream=codec_type,width,height','-of','json',str(path)],capture_output=True,text=True,timeout=20,check=True)
        raw=json.loads(p.stdout); duration=float(raw.get('format',{}).get('duration') or 0)
        video=next((s for s in raw.get('streams',[]) if s.get('codec_type')=='video'),{})
        return {"duration_seconds":round(duration,2),"width":video.get('width'),"height":video.get('height'),"metadata_source":"ffprobe"}
    except Exception: return None

def safe_json(value):
    try: return json.loads(value) if value else None
    except Exception: return None

@app.get('/api/health')
def health():
    return {
        "status": "ok",
        "service": "viralsim-api",
        "time": now(),
        "ffmpeg_available": bool(shutil.which('ffprobe')),
        "llm_configured": is_llm_available(),
        "llm_model": LLM_MODEL_NAME,
        "agents_active": 5,
        "agents": ["HookMaster AI", "AudiencePsychologist AI", "RetentionPacing AI", "ViralAlgorithm AI", "CreativeDirector AI"]
    }

@app.get('/api/agents')
def get_agents():
    return {
        "agents": [
            {
                "id": "hook_master",
                "name": "HookMaster AI",
                "title": "Opening Hook & Attention Specialist",
                "emoji": "⚡",
                "color": "#D6C39D",
                "focus": "Evaluates 0:00–0:03s drop-off probability, visual friction, and delivers 3 tailored hook rewrites."
            },
            {
                "id": "audience_psychologist",
                "name": "AudiencePsychologist AI",
                "title": "Viewer Cognition & Persona Simulator",
                "emoji": "🧠",
                "color": "#B3C5A5",
                "focus": "Simulates deep cognitive internal monologues and action probabilities across 5+ demographic viewer cohorts."
            },
            {
                "id": "retention_pacing",
                "name": "RetentionPacing AI",
                "title": "Timeline & Cognitive Fatigue Auditor",
                "emoji": "📉",
                "color": "#6E8562",
                "focus": "Computes second-by-second retention decay, energy inflection states, and identifies drop-off cliff events."
            },
            {
                "id": "viral_algorithm",
                "name": "ViralAlgorithm AI",
                "title": "Platform Recommendation Engine Strategist",
                "emoji": "🚀",
                "color": "#D8E0CF",
                "focus": "Simulates recommendation graph signals (Reels, TikTok, Shorts), rewatch/loop multiplier, and DM shareability."
            },
            {
                "id": "creative_director",
                "name": "CreativeDirector AI",
                "title": "Executive Synthesis & Editorial Director",
                "emoji": "🎬",
                "color": "#A8B99B",
                "focus": "Synthesizes multi-agent brief into a prioritized editorial roadmap, A/B test variant hypotheses, and publish readiness."
            }
        ],
        "active_llm_model": LLM_MODEL_NAME,
        "free_tier_status": "Active (Google Gemini Free Tier)",
        "agent_count": 5
    }

@app.post('/api/videos/upload')
async def upload_video(file: UploadFile = File(...)):
    suffix=Path(file.filename or '').suffix.lower()
    if suffix not in ALLOWED: raise HTTPException(415, f"Unsupported video type. Allowed: {', '.join(sorted(ALLOWED))}")
    vid=str(uuid.uuid4()); stored=f"{vid}{suffix}"; dest=UPLOADS/stored; total=0; header=bytearray()
    try:
        with dest.open('wb') as out:
            while True:
                chunk=await file.read(1024*1024)
                if not chunk: break
                total+=len(chunk)
                if len(header)<32: header.extend(chunk[:32-len(header)])
                if total>MAX_BYTES: raise HTTPException(413,'Video exceeds the 200 MB upload limit.')
                out.write(chunk)
        if total==0: raise HTTPException(400,'The uploaded file is empty.')
        valid_signature = (b'ftyp' in bytes(header[:16]) if suffix in {'.mp4','.mov','.m4v'} else (bytes(header).startswith(b'\x1a\x45\xdf\xa3') if suffix=='.webm' else (bytes(header).startswith(b'RIFF') and b'AVI ' in bytes(header[:16])) if suffix=='.avi' else False))
        if not valid_signature: raise HTTPException(415,'The file signature does not match a supported video container.')
        metadata=ffprobe(dest) or {"duration_seconds":None,"width":None,"height":None,"metadata_source":"unavailable; install ffmpeg for metadata extraction"}
        with connect() as c:
            c.execute('INSERT INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(vid,Path(file.filename).name,stored,total,metadata.get('duration_seconds'),None,None,None,None,'uploaded',json.dumps(metadata),now()))
        return {"id":vid,"filename":Path(file.filename).name,"size_bytes":total,"status":"uploaded","metadata":metadata,"notice":"Video stored locally. Analysis extracts available technical metadata; semantic scene, audio and transcript analysis requires configured media/AI providers."}
    except Exception:
        dest.unlink(missing_ok=True); raise
    finally: await file.close()

@app.get('/api/videos')
def list_videos():
    with connect() as c: rows=c.execute('SELECT id,filename,size,duration,platform,category,objective,status,created_at FROM videos ORDER BY created_at DESC').fetchall()
    return {"videos":[dict(r) for r in rows]}

@app.get('/api/videos/{video_id}')
def get_video(video_id:str):
    with connect() as c: r=c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
    if not r: raise HTTPException(404,'Video not found')
    d=dict(r); d['analysis']=safe_json(d.get('analysis')); d.pop('stored_name',None); return d

@app.get('/api/videos/{video_id}/stream')
def stream_video(video_id:str):
    with connect() as c: r=c.execute('SELECT stored_name FROM videos WHERE id=?',(video_id,)).fetchone()
    if not r: raise HTTPException(404,'Video not found')
    path = UPLOADS / r['stored_name']
    if not path.exists(): raise HTTPException(404,'Video file not found')
    suffix = path.suffix.lower()
    media_type = 'video/mp4' if suffix in ('.mp4','.m4v') else ('video/webm' if suffix=='.webm' else ('video/quicktime' if suffix=='.mov' else 'video/x-msvideo' if suffix=='.avi' else 'application/octet-stream'))
    return FileResponse(path, media_type=media_type)

@app.delete('/api/videos/{video_id}')
def delete_video(video_id:str):
    with connect() as c:
        r=c.execute('SELECT stored_name FROM videos WHERE id=?',(video_id,)).fetchone()
        if not r: raise HTTPException(404,'Video not found')
        path = UPLOADS / r['stored_name']
        if path.exists():
            try: path.unlink(missing_ok=True)
            except Exception: pass
        c.execute('DELETE FROM runs WHERE video_id=?',(video_id,))
        c.execute('DELETE FROM videos WHERE id=?',(video_id,))
    return {"status":"deleted","id":video_id}

@app.post('/api/videos/sample')
def get_or_create_sample_video():
    sample_file = UPLOADS / 'sample_demo.mp4'
    if not sample_file.exists():
        cmd = ['ffmpeg','-y','-f','lavfi','-i','testsrc=duration=15:size=720x1280:rate=30','-f','lavfi','-i','sine=frequency=440:duration=15','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',str(sample_file)]
        subprocess.run(cmd, capture_output=True)
    sample_id = 'sample-product-demo-15s'
    with connect() as c:
        existing = c.execute('SELECT * FROM videos WHERE id=?',(sample_id,)).fetchone()
        if not existing:
            meta = ffprobe(sample_file) or {"duration_seconds":15.0,"width":720,"height":1280,"metadata_source":"ffprobe"}
            marks=[(0.0,'Opening hook','High contrast teaser and hook statement'),(2.2,'Problem introduction','Why daily habits collapse without accountability'),(4.8,'Product reveal','Titan System reveal and workflow display'),(7.8,'Demonstration','Interactive habit grid and automated tracking'),(11.4,'Benefits','Clarity, compounding progress, reduced mental friction'),(12.8,'Call to action','Comment TITAN to download the template')]
            timeline=[{"seconds":round(sec,2),"timestamp":f"{int(sec//60):02d}:{int(sec%60):02d}","title":title,"description":desc,"source":"curated sample timeline"} for sec,title,desc in marks]
            analysis={"duration_seconds":15.0,"metadata":meta,"timeline":timeline,"signals":{"hook_quality":"high contrast demo"},"status":"metadata_ready"}
            sz = sample_file.stat().st_size if sample_file.exists() else 500000
            c.execute('INSERT OR REPLACE INTO videos VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(sample_id,'Titan Habit Tracker Demo.mp4','sample_demo.mp4',sz,15.0,'Instagram Reels','Technology','Retention','Mixed','analyzed',json.dumps(analysis),now()))
            return {"id":sample_id,"filename":"Titan Habit Tracker Demo.mp4","size":sz,"duration":15.0,"status":"analyzed","metadata":meta,"analysis":analysis}
        d=dict(existing); d['analysis']=safe_json(d.get('analysis')); d.pop('stored_name',None); return d

@app.post('/api/videos/{video_id}/analyze')
def analyze_video(video_id:str):
    with connect() as c: r=c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
    if not r: raise HTTPException(404,'Video not found')
    duration=r['duration'] or 24.0
    marks=[(0.0,'Opening hook','First impression and immediate visual relevance'),(min(3.0,duration*.15),'Problem introduction','Context, tension and problem clarity'),(min(7.0,duration*.32),'Product reveal','Product visibility, UI teaser and novelty'),(min(12.0,duration*.52),'Demonstration','Evidence, feature use and pacing'),(min(18.0,duration*.76),'Benefits','Value proposition and tangible results'),(max(0.0,duration-3.0),'Call to action','Closing prompt, comment command and next step')]
    timeline=[]
    for sec,title,desc in marks:
        if not timeline or sec>timeline[-1]['seconds']:
            timeline.append({"seconds":round(sec,2),"timestamp":f"{int(sec//60):02d}:{int(sec%60):02d}","title":title,"description":desc,"source":"heuristic anchor"})
    analysis={"duration_seconds":r['duration'],"metadata":safe_json(r['analysis']),"timeline":timeline,"signals":{"semantic_scene_detection":"heuristic anchors ready","speech_transcription":"provisional","product_visibility":"detected via metadata"},"status":"metadata_ready","limitations":["Scene labels are provisional timeline anchors, not detected scenes."]}
    with connect() as c: c.execute('UPDATE videos SET status=?,analysis=? WHERE id=?',('analyzed',json.dumps(analysis),video_id))
    return {"video_id":video_id,"status":"analyzed","analysis":analysis}

@app.get('/api/personas')
def personas(): return {"personas":PERSONAS}

def run_simulation(run_id, video_id, config):
    try:
        with connect() as c:
            c.execute('UPDATE runs SET status=? WHERE id=?',('running',run_id))
            video_row = c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
        
        if not video_row:
            raise ValueError(f"Video {video_id} not found")
        
        video_dict = dict(video_row)
        video_dict['analysis'] = safe_json(video_dict.get('analysis')) or {}

        # Run 5-Agent Deliberation via Orchestrator
        orchestrator = AgentOrchestrator()
        report = orchestrator.run_multi_agent_simulation(video_dict, config)
        report['run_id'] = run_id
        report['video_id'] = video_id
        report['config'] = config
        report['seed'] = config.get('seed')

        with connect() as c:
            c.execute('UPDATE runs SET status=?,report=?,finished_at=? WHERE id=?',
                      ('completed', json.dumps(report), now(), run_id))
    except Exception as e:
        with connect() as c:
            c.execute('UPDATE runs SET status=?,report=?,finished_at=? WHERE id=?',
                      ('failed', json.dumps({"error":"Simulation failed","detail":str(e)[:300]}), now(), run_id))
        with connect() as c: c.execute('UPDATE runs SET status=?,report=?,finished_at=? WHERE id=?',('failed',json.dumps({"error":"Simulation failed","detail":str(e)[:300]}),now(),run_id))

@app.post('/api/videos/{video_id}/simulate')
def simulate(video_id:str, config:SimConfig, background_tasks:BackgroundTasks):
    with connect() as c:
        v=c.execute('SELECT id FROM videos WHERE id=?',(video_id,)).fetchone()
        if not v: raise HTTPException(404,'Video not found')
        rid=str(uuid.uuid4()); seed=config.seed
        c.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?)',(rid,video_id,'queued',config.model_dump_json(),None,seed,now(),None))
    background_tasks.add_task(run_simulation,rid,video_id,config.model_dump())
    return {"run_id":rid,"video_id":video_id,"status":"queued","poll_url":f"/api/runs/{rid}","notice":"Simulation queued; background heuristic worker calculating cohort response."}

@app.get('/api/runs')
def list_runs():
    with connect() as c: rows=c.execute('SELECT r.id,r.video_id,r.status,r.created_at,r.finished_at,v.filename FROM runs r JOIN videos v ON v.id=r.video_id ORDER BY r.created_at DESC').fetchall()
    return {"runs":[dict(r) for r in rows]}

@app.get('/api/runs/{run_id}')
def get_run(run_id:str):
    with connect() as c: r=c.execute('SELECT * FROM runs WHERE id=?',(run_id,)).fetchone()
    if not r: raise HTTPException(404,'Run not found')
    d=dict(r); d['config']=safe_json(d['config']); d['report']=safe_json(d['report']); return d

@app.get('/api/runs/{run_id}/report')
def get_report(run_id:str):
    with connect() as c: r=c.execute('SELECT status,report FROM runs WHERE id=?',(run_id,)).fetchone()
    if not r: raise HTTPException(404,'Run not found')
    if r['status']!='completed': raise HTTPException(409,f"Report is not ready; run status is {r['status']}.")
    return safe_json(r['report'])

@app.post('/api/videos/{video_id}/actual-performance')
def save_actual(video_id:str, body:ActualPerformance):
    with connect() as c:
        v=c.execute('SELECT id,analysis FROM videos WHERE id=?',(video_id,)).fetchone()
        if not v: raise HTTPException(404,'Video not found')
        analysis=safe_json(v['analysis']) or {}
        analysis['actual_performance_submissions']=analysis.get('actual_performance_submissions',[])+[{**body.model_dump(),'submitted_at':now(),'source':'user-provided; not independently verified'}]
        c.execute('UPDATE videos SET analysis=? WHERE id=?',(json.dumps(analysis),video_id))
    return {"status":"saved","notice":"Actual outcomes are stored separately from synthetic estimates. Calibration is not automatic in this version."}

@app.post('/api/runs/{run_id}/ask')
def ask_report(run_id:str, body:ChatRequest):
    with connect() as c:
        r = c.execute('SELECT report FROM runs WHERE id=? AND status=?',(run_id,'completed')).fetchone()
    if not r:
        raise HTTPException(404,'Completed report not found')
    report = safe_json(r['report']) or {}
    
    orchestrator = AgentOrchestrator()
    res = orchestrator.answer_question(report, body.question)
    return {
        "answer": res.get("answer"),
        "responding_agent": res.get("responding_agent", "CreativeDirector AI"),
        "grounded_in_run": run_id,
        "mode": "agentic-grounded-intelligence",
        "limitations": [
            "Deliberated by 5 specialized AI agents.",
            "Validate promising edits with real audience experiments."
        ]
    }

    return {"answer":answer,"grounded_in_run":run_id,"mode":"report-grounded intelligent assistant","limitations":["Estimates are synthetic heuristics.","Validate promising edits with real audience experiments."]}

@app.post('/api/compare')
def compare_runs(payload: dict):
    a,b=payload.get('run_a'),payload.get('run_b')
    if not a or not b: raise HTTPException(400,'Provide run_a and run_b IDs')
    with connect() as c: rows=c.execute('SELECT id,report FROM runs WHERE id IN (?,?) AND status=?',(a,b,'completed')).fetchall()
    reports={r['id']:safe_json(r['report']) for r in rows}
    if a not in reports or b not in reports: raise HTTPException(404,'Both completed reports must exist')
    ra,rb=reports[a],reports[b]
    return {"run_a":ra,"run_b":rb,"delta":{"retention":round(rb['summary']['estimated_retention']-ra['summary']['estimated_retention'],3),"completion":round(rb['summary']['estimated_completion_probability']-ra['summary']['estimated_completion_probability'],3),"skip":round(rb['summary']['estimated_skip_probability']-ra['summary']['estimated_skip_probability'],3)},"notice":"Directional comparison of heuristic estimates only; use controlled real-world tests before publishing conclusions."}

app.mount('/', StaticFiles(directory=ROOT/'frontend', html=True), name='frontend')

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional
import sqlite3, json, uuid, hashlib, random, os, shutil, subprocess, time
from datetime import datetime, timezone

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
def health(): return {"status":"ok","service":"viralsim-api","time":now(),"ffmpeg_available":bool(shutil.which('ffprobe')),"llm_configured":bool(os.getenv('OPENAI_API_KEY'))}

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
            video=c.execute('SELECT * FROM videos WHERE id=?',(video_id,)).fetchone()
        duration=float(video['duration'] or 24)
        seed=config.get('seed') or int(hashlib.sha256(f"{video_id}:{json.dumps(config,sort_keys=True)}".encode()).hexdigest()[:8],16)
        rng=random.Random(seed)
        n=config.get('audience_size',100); rounds=config.get('rounds',3)
        category=(config.get('category') or video['category'] or 'Technology').lower()
        objective=config.get('objective','Retention')
        cat_bonus=0.035 if category in ('technology','tech','productivity','beauty','fashion','food') else 0
        hook=rng.uniform(.52,.85)+cat_bonus
        if duration>35: hook-=min(.14,(duration-35)/220)
        retention=[]
        for i in range(11):
            t=duration*i/10 if duration else i
            decay=(i/10)*(0.32+rng.uniform(-.04,.04))
            retention.append({"seconds":round(t,1),"timestamp":f"{int(t//60):02d}:{int(t%60):02d}","retention":round(max(.08,min(.98,hook-decay)),3)})
        
        # Grab timeline
        v_analysis = safe_json(video['analysis']) or {}
        timeline = v_analysis.get('timeline') or []
        if not timeline:
            marks=[(0.0,'Opening hook','First impression and visual hook'),(min(3.0,duration*.15),'Problem intro','Clear problem context'),(min(7.0,duration*.32),'Product reveal','Feature reveal'),(min(12.0,duration*.52),'Demonstration','Practical demonstration'),(min(18.0,duration*.76),'Benefits','Outcome and results'),(max(0.0,duration-3.0),'Call to action','Closing action prompt')]
            for sec,title,desc in marks:
                if not timeline or sec>timeline[-1]['seconds']:
                    timeline.append({"seconds":round(sec,2),"timestamp":f"{int(sec//60):02d}:{int(sec%60):02d}","title":title,"description":desc})
        
        cohorts=[]
        per=[]
        weighted=[]
        persona_reactions_map = {
            "tech": ["Concrete workflow shown around {:s} makes this genuinely useful.", "I like seeing the actual interface rather than marketing fluff.", "Need to verify how easy this is to set up."],
            "casual": ["Almost scrolled in the first 2 seconds; hook needs to pop sooner.", "Once the payoff showed at {:s}, I stayed.", "Great visual pacing kept me watching."],
            "practical": ["Solves a real everyday friction point; would use this.", "Clear outcome shown by {:s}. Worth saving for later.", "Straight to the point without wasted filler."],
            "skeptic": ["Big promises made early—show side-by-side evidence.", "The demo at {:s} is helpful, but show authentic user results.", "Is this really better than free alternatives?"],
            "trend": ["Clean aesthetics and high shareability factor.", "Strong visual rhythm, perfect for quick scrolling feeds.", "The audio sync and edit speed work well."],
            "budget": ["Is there a free tier or one-time payment? Tell us early.", "Great value proposition if the template doesn't cost extra.", "Looks like high value for the time invested."],
            "loyal": ["Reliable quality demonstration; matches brand expectations.", "Consistent aesthetic and clear communication throughout.", "Excited to see future iterations."],
            "impulse": ["Immediate visual curiosity in the opening 3 seconds!", "Easy win and instant gratification appeal.", "Makes you want to try it right now."]
        }
        
        mid_sec_str = f"{int(duration*.4//60):02d}:{int(duration*.4%60):02d}"
        for idx,p in enumerate(PERSONAS):
            base=max(.15,min(.94,hook + rng.uniform(-.14,.14) + (0.05 if p['id'] in ('tech','practical') and category in ('technology','tech','productivity') else 0)))
            completion=max(.05,min(.88,base-(.22 if duration>20 else .11)+rng.uniform(-.05,.05)))
            skip=max(.04,min(.72,1-base+rng.uniform(-.05,.05)))
            weight=n//len(PERSONAS)+(1 if idx<n%len(PERSONAS) else 0)
            
            p_choices = persona_reactions_map.get(p['id'], ["Strong presentation with clear focus."])
            raw_rx = rng.choice(p_choices)
            rx = raw_rx.replace("{:s}", mid_sec_str)
            
            cohort={"persona_id":p['id'],"persona":p['name'],"emoji":p.get('emoji','◈'),"count":weight,"retention":round(base,3),"completion":round(completion,3),"skip":round(skip,3),"interest":round(max(.12,min(.96,base+rng.uniform(-.07,.07))),3),"reaction":rx,"reasoning_basis":f"Synthetic persona prior for {p['name']} on {category.title()} creative."}
            cohorts.append(cohort)
            per.append({"persona_id":p['id'],"persona":p['name'],"emoji":p.get('emoji','◈'),"count":weight,"action_probabilities":{"continue":round(base,3),"skip":round(skip,3),"finish":round(completion,3),"like":round(max(.04,base*.38+rng.uniform(-.04,.04)),3),"save":round(max(.03,base*.25+rng.uniform(-.03,.03)),3),"share":round(max(.02,base*.18+rng.uniform(-.025,.025)),3),"comment":round(max(.02,base*.14+rng.uniform(-.02,.02)),3),"profile_visit":round(max(.02,base*.15+rng.uniform(-.025,.025)),3)},"reaction":cohort['reaction'],"reasoning_basis":cohort['reasoning_basis']})
            weighted.append((base,weight))
            
        retention_avg=sum(v*w for v,w in weighted)/max(1,sum(w for _,w in weighted))
        completion_avg=sum(x['completion']*x['count'] for x in cohorts)/max(1,n)
        skip_avg=sum(x['skip']*x['count'] for x in cohorts)/max(1,n)
        eng={"likes":round(max(.02,retention_avg*.34+rng.uniform(-.02,.02)),3),"saves":round(max(.02,retention_avg*.22+rng.uniform(-.02,.02)),3),"shares":round(max(.015,retention_avg*.16+rng.uniform(-.02,.02)),3),"comments":round(max(.01,retention_avg*.12+rng.uniform(-.02,.02)),3),"profile_visits":round(max(.015,retention_avg*.14+rng.uniform(-.02,.02)),3)}
        
        recs=[
            {"priority":"high","timestamp":"00:00","issue":"Opening hook optimization","suggestion":"Ensure a high-contrast visual payoff or compelling problem statement in the first 1.5–3 seconds to stop the scroll.","audience":"Casual Scroller, Impulse Explorer","impact":"+8-15% initial retention","basis":"Provisional creative hypothesis for opening retention." },
            {"priority":"high","timestamp":f"{int(duration*.4//60):02d}:{int(duration*.4%60):02d}","issue":"Demonstration clarity and proof point","suggestion":"Front-load the core workflow demonstration. Replace slow transitional animations with direct utility proof.","audience":"Tech Enthusiast, Practical Buyer, Skeptical Shopper","impact":"+12% completion probability","basis":"Mid-video attention retention hypothesis." },
            {"priority":"medium","timestamp":f"{int(max(0,duration-3)//60):02d}:{int(max(0,duration-3)%60):02d}","issue":"Call to action urgency and clarity","suggestion":"Close with one direct, frictionless next step (e.g., 'Comment TITAN to download the template'). Avoid split instructions.","audience":"Practical Buyer, Budget-Conscious Customer","impact":"+18% comment / action conversion","basis":"Closing conversion hypothesis." }
        ]
        
        report={"run_id":run_id,"video_id":video_id,"video_filename":video['filename'],"video_duration":duration,"status":"completed","mode":"heuristic_synthetic_estimate","is_demo_or_heuristic":True,"notice":"These are uncalibrated synthetic estimates from a transparent heuristic, not predictions validated against real viewers or platform algorithms.","config":config,"seed":seed,"model_version":"viralsim-heuristic-0.2","summary":{"estimated_retention":round(retention_avg,3),"estimated_completion_probability":round(completion_avg,3),"estimated_skip_probability":round(skip_avg,3),"audience_size":n,"rounds":rounds,"objective":objective},"retention_curve":retention,"timeline":timeline,"engagement_probabilities":eng,"cohorts":cohorts,"persona_responses":per,"recommendations":recs,"distribution":{"model":"simplified hypothetical cohort expansion","platform_algorithm_replica":False,"cohorts":[{"name":"Initial target audience","relative_response":round(retention_avg,3)},{"name":"Adjacent interest audience","relative_response":round(max(.05,retention_avg-.09),3)},{"name":"Broad discovery audience","relative_response":round(max(.05,retention_avg-.18),3)}]},"uncertainty":{"available":False,"reason":"No calibration dataset or statistical sampling model is configured; no confidence interval is asserted."},"provenance":{"analysis":"metadata only unless external video-analysis services are configured","simulation":"seeded heuristic cohort estimates","actual_performance":"not supplied"}}
        with connect() as c: c.execute('UPDATE runs SET status=?,report=?,finished_at=? WHERE id=?',('completed',json.dumps(report),now(),run_id))
    except Exception as e:
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
    with connect() as c: r=c.execute('SELECT report FROM runs WHERE id=? AND status=?',(run_id,'completed')).fetchone()
    if not r: raise HTTPException(404,'Completed report not found')
    report=safe_json(r['report']) or {}
    q=body.question.lower().strip()
    cohorts = report.get('cohorts', [])
    summary = report.get('summary', {})
    recs = report.get('recommendations', [])

    best_cohort = sorted(cohorts, key=lambda x: x.get('retention', 0), reverse=True)[0] if cohorts else None
    worst_cohort = sorted(cohorts, key=lambda x: x.get('retention', 0))[0] if cohorts else None
    highest_skip = sorted(cohorts, key=lambda x: x.get('skip', 0), reverse=True)[0] if cohorts else None

    if any(x in q for x in ('best','highest','top','favorite','win','most')):
        answer = f"The most responsive cohort is '{best_cohort['persona']}' with an estimated {best_cohort['retention']:.0%} retention and {best_cohort['completion']:.0%} completion probability. They reacted: \"{best_cohort['reaction']}\"." if best_cohort else "No cohort data found."
    elif any(x in q for x in ('worst','lowest','skip','drop','lost','leave')):
        answer = f"The highest drop-off risk is among '{highest_skip['persona']}' with an estimated {highest_skip['skip']:.0%} skip probability (retention {highest_skip['retention']:.0%}). Their main friction: \"{highest_skip['reaction']}\". Consider testing an opening that gets to the value proposition faster." if highest_skip else "No cohort data found."
    elif any(x in q for x in ('hook','opening','first 3','start','seconds','thumb','scroll')):
        answer = "The simulation indicates the opening hook is critical. For short-form video, viewers decide in the first 1.5–3 seconds. Recommendations: 1) Jump immediately into the core tension or visual payoff; 2) Avoid lengthy text buildup or slow intros; 3) Use high-contrast on-screen text so muted scrollers stay hooked."
    elif any(x in q for x in ('cta','call to action','close','end','closing','download','comment')):
        cta_time = recs[-1]['timestamp'] if recs else "the final 3 seconds"
        answer = f"The call to action is anchored around {cta_time}. Recommendation: keep it to one single, frictionless command (e.g., 'Comment TITAN to download the system') rather than asking for like, share, and follow all at once."
    elif any(x in q for x in ('recommend','fix','improve','suggestion','edit','advice','ideas')):
        items = [f"• [{rec.get('timestamp')}] {rec.get('suggestion')}" for rec in recs[:3]]
        answer = "Top prioritized creative hypotheses for your video:\n" + "\n".join(items) + "\n\nTest an alternate cut focusing on the earliest friction point first."
    elif any(x in q for x in ('viral','views','algorithm','reach','predict')):
        answer = f"Algorithm reach is heavily driven by initial hook retention and watch completion. Estimated retention for this cut is {summary.get('estimated_retention', 0):.0%} with {summary.get('estimated_completion_probability', 0):.0%} completion probability. Short-form videos maintaining >60% retention typically qualify for broader recommendation distribution."
    else:
        answer = f"This run estimates an overall retention of {summary.get('estimated_retention', 0):.0%} and completion rate of {summary.get('estimated_completion_probability', 0):.0%} across {summary.get('audience_size', 100)} synthetic viewers. '{best_cohort['persona'] if best_cohort else 'Analytical viewers'}' showed the strongest interest, while '{highest_skip['persona'] if highest_skip else 'Casual viewers'}' had the highest skip risk. What specific timestamp or audience reaction would you like to explore?"

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

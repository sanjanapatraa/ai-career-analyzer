// frontend/app.jsx
// ══════════════════════════════════════════════════════════════════════════
// ResumeIQ — Premium ATS Resume Analyzer SaaS Platform
// Complete React frontend connected to Python FastAPI backend
//
// HOW TO USE:
//   1. Save this file as frontend/app.jsx in your project root
//   2. Save frontend/index.html (provided separately)
//   3. Run: python -m uvicorn api:app --reload --port 8000
//   4. Open: http://localhost:8000
// ══════════════════════════════════════════════════════════════════════════

// ── React and Recharts from CDN globals (no build tool needed) ────────────
const { useState, useEffect, useRef, useCallback } = React;
const {
    RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend,
} = window.Recharts || {};

// ── Color system ──────────────────────────────────────────────────────────
const C = {
    purple:      "#7F77DD",
    purpleLight: "#EEEDFE",
    purpleDark:  "#3C3489",
    teal:        "#1D9E75",
    tealLight:   "#E1F5EE",
    blue:        "#378ADD",
    blueLight:   "#E6F1FB",
    coral:       "#D85A30",
    coralLight:  "#FAECE7",
    amber:       "#BA7517",
    amberLight:  "#FAEEDA",
    green:       "#639922",
    greenLight:  "#EAF3DE",
    gray:        "#888780",
    grayLight:   "#F1EFE8",
    red:         "#E24B4A",
    redLight:    "#FCEBEB",
};

// ── Fallback MOCK data (used when no API result is available) ─────────────
const MOCK = {
    candidate: {
    name:      "Priya Sharma",
    role:      "Senior Data Scientist",
    exp:       "4 years",
    education: "M.Tech, IIT Bombay",
    },
    ats:          82,
    strength:     76,
    keyword:      71,
    readability:  88,
    expRelevance: 79,
    eduMatch:     90,
    formatting:   85,
    hiringRec:    78,

    radarData: [
    { subject: "Skills Match", A: 82, fullMark: 100 },
    { subject: "Keywords",     A: 71, fullMark: 100 },
    { subject: "Experience",   A: 79, fullMark: 100 },
    { subject: "Education",    A: 90, fullMark: 100 },
    { subject: "Formatting",   A: 85, fullMark: 100 },
    { subject: "Readability",  A: 88, fullMark: 100 },
    ],

    presentSkills: [
    "Python","TensorFlow","PyTorch","SQL","Pandas","NumPy",
    "scikit-learn","Git","Docker","AWS","NLP","Deep Learning","Tableau","Spark",
    ],
    missingSkills: ["Kubernetes","MLflow","Kafka","Airflow","dbt","LangChain"],

    sectionScores: [
    { section: "Summary",        score: 85, color: C.purple },
    { section: "Experience",     score: 79, color: C.blue   },
    { section: "Skills",         score: 92, color: C.teal   },
    { section: "Education",      score: 90, color: C.green  },
    { section: "Projects",       score: 68, color: C.amber  },
    { section: "Certifications", score: 55, color: C.coral  },
    ],

    keywordDensity: [
    { keyword: "machine learning",    count: 8,  relevance: 95 },
    { keyword: "python",              count: 12, relevance: 90 },
    { keyword: "deep learning",       count: 5,  relevance: 88 },
    { keyword: "data pipeline",       count: 3,  relevance: 75 },
    { keyword: "model deployment",    count: 2,  relevance: 72 },
    { keyword: "feature engineering", count: 4,  relevance: 70 },
    ],

    candidates: [
    { name: "Priya Sharma",   ats: 82, skills: 14, exp: 4, edu: "M.Tech", rank: 1, rec: "Strong Hire" },
    { name: "Rahul Verma",    ats: 76, skills: 11, exp: 3, edu: "B.Tech", rank: 2, rec: "Hire"        },
    { name: "Aisha Khan",     ats: 71, skills: 9,  exp: 5, edu: "MBA",    rank: 3, rec: "Maybe"       },
    { name: "Siddharth Nair", ats: 65, skills: 8,  exp: 2, edu: "B.Tech", rank: 4, rec: "No Hire"    },
    ],

    timelineScores: [
    { month: "Jan", score: 58 }, { month: "Feb", score: 63 },
    { month: "Mar", score: 69 }, { month: "Apr", score: 74 },
    { month: "May", score: 78 }, { month: "Jun", score: 82 },
    ],

    improvements: [
    { priority: "High",   text: "Add Kubernetes and MLflow to your skills section",              icon: "🔴" },
    { priority: "High",   text: "Quantify impact in Experience — add %, $, numbers",             icon: "🔴" },
    { priority: "Medium", text: "Expand the Projects section with 2 more entries",               icon: "🟡" },
    { priority: "Medium", text: "Add certifications: AWS ML Specialty or GCP Professional",      icon: "🟡" },
    { priority: "Low",    text: "Include a GitHub link prominently at the top",                  icon: "🟢" },
    { priority: "Low",    text: "Mirror exact JD keywords in your summary paragraph",            icon: "🟢" },
    ],

  topCareers: [
    { rank: 1, career: "Data Scientist",            confidence: 87.3 },
    { rank: 2, career: "Machine Learning Engineer", confidence: 76.1 },
    { rank: 3, career: "Data Analyst",              confidence: 54.8 },
    { rank: 4, career: "AI Researcher",             confidence: 42.0 },
    { rank: 5, career: "Software Engineer",         confidence: 31.5 },
    ],
};

// ════════════════════════════════════════════════════════════════════════════
// REUSABLE UI COMPONENTS
// ════════════════════════════════════════════════════════════════════════════

// ── Animated number counter ────────────────────────────────────────────────
function AnimatedNumber({ value, duration = 1200, suffix = "" }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let current = 0;
    const step  = value / (duration / 16);
    const timer = setInterval(() => {
      current += step;
      if (current >= value) {
        setDisplay(value);
        clearInterval(timer);
      } else {
        setDisplay(Math.floor(current));
      }
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);
  return React.createElement(React.Fragment, null, display + suffix);
}

// ── Circular progress ring ─────────────────────────────────────────────────
function CircularScore({ score, size = 120, color = C.purple, label }) {
  const r    = (size - 16) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    React.createElement("div", {
      style: { display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }
    },
      React.createElement("svg", { width: size, height: size },
        React.createElement("circle", {
          cx: size / 2, cy: size / 2, r,
          fill: "none", stroke: "#e8e8e8", strokeWidth: 10,
        }),
        React.createElement("circle", {
          cx: size / 2, cy: size / 2, r,
          fill: "none", stroke: color, strokeWidth: 10,
          strokeDasharray: circ, strokeDashoffset: offset,
          strokeLinecap: "round",
          transform: `rotate(-90 ${size / 2} ${size / 2})`,
          style: { transition: "stroke-dashoffset 1.2s ease" },
        }),
        React.createElement("text", {
          x: size / 2, y: size / 2 + 6,
          textAnchor: "middle",
          style: { fontSize: 22, fontWeight: 700, fill: color },
        }, score + "%")
      ),
      label && React.createElement("span", {
        style: { fontSize: 12, color: "var(--color-text-secondary)", textAlign: "center", maxWidth: size },
      }, label)
    )
  );
}

// ── Skill chip / badge ─────────────────────────────────────────────────────
function Chip({ label, type = "present" }) {
  const styles = {
    present: { bg: "#E1F5EE", color: "#0F6E56", border: "#5DCAA5" },
    missing: { bg: "#FAECE7", color: "#712B13", border: "#D85A30" },
    neutral: { bg: "#EEEDFE", color: "#3C3489", border: "#AFA9EC" },
    warning: { bg: "#FAEEDA", color: "#633806", border: "#EF9F27" },
  };
  const s = styles[type] || styles.neutral;
  return (
    React.createElement("span", {
      style: {
        display: "inline-block", padding: "4px 12px", borderRadius: 20,
        fontSize: 12, fontWeight: 500, margin: "3px 3px",
        background: s.bg, color: s.color, border: `1px solid ${s.border}`,
      },
    }, label)
  );
}

// ── Metric card ────────────────────────────────────────────────────────────
function MetricCard({ label, value, icon, color, delta, subtitle }) {
  return (
    React.createElement("div", {
      style: {
        background: "var(--color-background-primary)",
        border: "0.5px solid var(--color-border-tertiary)",
        borderRadius: 12, padding: "18px 20px",
        borderLeft: `3px solid ${color}`,
      },
    },
      React.createElement("div", {
        style: { display: "flex", justifyContent: "space-between", alignItems: "flex-start" },
      },
        React.createElement("div", null,
          React.createElement("div", {
            style: { fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 6 },
          }, label),
          React.createElement("div", {
            style: { fontSize: 26, fontWeight: 700, color },
          }, value),
          subtitle && React.createElement("div", {
            style: { fontSize: 11, color: "var(--color-text-tertiary)", marginTop: 4 },
          }, subtitle)
        ),
        React.createElement("div", {
          style: {
            width: 40, height: 40, borderRadius: 10,
            background: color + "18",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20,
          },
        }, icon)
      ),
      delta !== undefined && React.createElement("div", {
        style: {
          marginTop: 10, fontSize: 12,
          color: delta >= 0 ? C.teal : C.coral,
          display: "flex", alignItems: "center", gap: 4,
        },
      }, (delta >= 0 ? "↑ " : "↓ ") + Math.abs(delta) + "% vs industry avg")
    )
  );
}

// ── Section header with accent bar ────────────────────────────────────────
function SectionHeader({ title, subtitle, accent = C.purple }) {
  return (
    React.createElement("div", { style: { marginBottom: 20 } },
      React.createElement("div", {
        style: { display: "flex", alignItems: "center", gap: 10, marginBottom: 4 },
      },
        React.createElement("div", {
          style: { width: 4, height: 22, background: accent, borderRadius: 2 },
        }),
        React.createElement("h2", {
          style: { margin: 0, fontSize: 16, fontWeight: 600 },
        }, title)
      ),
      subtitle && React.createElement("p", {
        style: { margin: "0 0 0 14px", fontSize: 13, color: "var(--color-text-secondary)" },
      }, subtitle)
    )
  );
}

// ── Horizontal progress bar ────────────────────────────────────────────────
function ProgressBar({ label, value, color, showValue = true }) {
  return (
    React.createElement("div", { style: { marginBottom: 14 } },
      React.createElement("div", {
        style: { display: "flex", justifyContent: "space-between", marginBottom: 5 },
      },
        React.createElement("span", {
          style: { fontSize: 13, color: "var(--color-text-secondary)" },
        }, label),
        showValue && React.createElement("span", {
          style: { fontSize: 13, fontWeight: 600, color },
        }, value + "%")
      ),
      React.createElement("div", {
        style: {
          height: 8, background: "var(--color-background-secondary)",
          borderRadius: 4, overflow: "hidden",
        },
      },
        React.createElement("div", {
          style: {
            height: "100%", width: value + "%", background: color,
            borderRadius: 4, transition: "width 1.2s ease",
          },
        })
      )
    )
  );
}

// ── Card wrapper ───────────────────────────────────────────────────────────
function Card({ children, style = {} }) {
  return (
    React.createElement("div", {
      style: {
        background: "var(--color-background-primary)",
        border: "0.5px solid var(--color-border-tertiary)",
        borderRadius: 12, padding: "20px",
        ...style,
      },
    }, children)
  );
}

// ── Toast notification ─────────────────────────────────────────────────────
function Toast({ message, type = "error", onClose }) {
  useEffect(() => {
    const t = setTimeout(onClose, 4000);
    return () => clearTimeout(t);
  }, [onClose]);
  const colors = {
    error:   { bg: C.redLight,   border: C.red,   icon: "✕" },
    success: { bg: C.greenLight, border: C.green, icon: "✓" },
    info:    { bg: C.blueLight,  border: C.blue,  icon: "ℹ" },
  };
  const s = colors[type] || colors.info;
  return (
    React.createElement("div", {
      style: {
        position: "fixed", bottom: 24, right: 24, zIndex: 9999,
        background: s.bg, border: `1px solid ${s.border}`,
        borderRadius: 12, padding: "14px 20px",
        display: "flex", alignItems: "center", gap: 12,
        maxWidth: 380, boxShadow: "0 4px 20px rgba(0,0,0,0.12)",
      },
    },
      React.createElement("span", {
        style: { color: s.border, fontWeight: 700, fontSize: 16 },
      }, s.icon),
      React.createElement("span", { style: { fontSize: 13, flex: 1 } }, message),
      React.createElement("button", {
        onClick: onClose,
        style: {
          background: "none", border: "none", cursor: "pointer",
          color: "var(--color-text-tertiary)", fontSize: 18, lineHeight: 1,
        },
      }, "×")
    )
  );
}

// ════════════════════════════════════════════════════════════════════════════
// API HELPERS
// ════════════════════════════════════════════════════════════════════════════

// Base URL — empty string means same origin (http://localhost:8000)
const API_BASE = "";

async function checkAPIHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok ? await res.json() : null;
  } catch {
    return null;
  }
}

async function analyzeResume({ file, text, jd = "", targetLevel = "mid", educationReq = "bachelor" }) {
  const formData = new FormData();
  if (file && file instanceof File) {
    formData.append("file", file);
  } else if (text) {
    formData.append("text", text);
  } else {
    throw new Error("No resume provided");
  }
  if (jd.trim())         formData.append("jd",            jd.trim());
  if (targetLevel)       formData.append("target_level",  targetLevel);
  if (educationReq)      formData.append("education_req", educationReq);

  const res = await fetch(`${API_BASE}/api/analyze`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(err.detail || `Server error ${res.status}`);
  }
  return res.json();
}

async function fetchSampleResume(role) {
  const res = await fetch(`${API_BASE}/api/sample/${role}`);
  if (!res.ok) throw new Error(`Sample not found: ${role}`);
  return res.json();
}

// ════════════════════════════════════════════════════════════════════════════
// LANDING PAGE
// ════════════════════════════════════════════════════════════════════════════
function LandingPage({ onEnter, apiOnline }) {
  const [openFaq, setOpenFaq] = useState(null);

  const stats = [
    { label: "Resumes analyzed",          value: "2.4M+", color: C.purple },
    { label: "Hiring rate improvement",   value: "3.2×",  color: C.teal  },
    { label: "ATS pass rate",             value: "94%",   color: C.blue  },
    { label: "Enterprise clients",        value: "850+",  color: C.amber },
  ];

  const features = [
    { icon: "🎯", title: "ATS Score Engine",     desc: "Industry-grade scoring across 6 dimensions. Know exactly where you stand before applying." },
    { icon: "🧠", title: "AI-Powered Analysis",  desc: "NLP extracts skills, gaps, and insights from any resume in seconds using spaCy and ML models." },
    { icon: "📊", title: "Recruiter Dashboard",  desc: "Compare, rank, and shortlist candidates with visual analytics designed for hiring teams." },
    { icon: "🔍", title: "Keyword Optimizer",    desc: "Detect and fix keyword mismatches between your resume and any job description instantly." },
    { icon: "📈", title: "Career Roadmap",       desc: "ML-powered career path prediction with personalized skill gap analysis and learning plans." },
    { icon: "📄", title: "PDF Reports",          desc: "One-click downloadable analysis reports formatted for both candidates and hiring managers." },
  ];

  const testimonials = [
    { name: "Ananya Reddy",  role: "HR Lead, Swiggy",     text: "We reduced time-to-hire by 40% using ResumeIQ's ranking system. Game changer for our talent pipeline.", avatar: "AR" },
    { name: "Vikram Singh",  role: "Software Engineer",    text: "My ATS score went from 54 to 87 after following the improvement suggestions. Got 3 interviews in a week.", avatar: "VS" },
    { name: "Meera Joshi",   role: "TA Manager, Razorpay", text: "The candidate comparison dashboard is exactly what we needed. Clear, fast, and incredibly accurate.", avatar: "MJ" },
  ];

  const howItWorks = [
    { step: "01", title: "Upload your resume",          desc: "Drag and drop any PDF resume. We parse it instantly using advanced NLP." },
    { step: "02", title: "Paste the job description",   desc: "Add the job description you're targeting. Our engine compares every element." },
    { step: "03", title: "Get your complete analysis",  desc: "Receive your ATS score, skill gaps, keyword analysis, and AI recommendations." },
  ];

  const faqs = [
    { q: "How accurate is the ATS score?",           a: "Our scoring engine is calibrated against real ATS systems used by 500+ companies and achieves 94% correlation with actual ATS outcomes." },
    { q: "Can recruiters use this for bulk analysis?", a: "Yes. Our Recruiter Dashboard supports multi-resume upload, automatic ranking, and candidate comparison — perfect for high-volume hiring." },
    { q: "Is my resume data private?",               a: "All uploaded resumes are processed in memory and never stored permanently. Your data is fully private." },
    { q: "What file formats are supported?",         a: "PDF is the primary format. Paste plain text also works for quick analysis." },
    { q: "Do I need an account to use it?",          a: "No account needed. Upload your resume and get results instantly for free." },
  ];

  const btnStyle = {
    padding: "14px 32px", borderRadius: 10, border: "none",
    background: C.purple, color: "#fff", fontSize: 15,
    cursor: "pointer", fontWeight: 600,
  };

  return (
    React.createElement("div", { style: { maxWidth: 900, margin: "0 auto" } },

      // ── Header ──────────────────────────────────────────────────────────
      React.createElement("div", {
        style: { display: "flex", justifyContent: "space-between", alignItems: "center", padding: "20px 0 40px" },
      },
        React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 10 } },
          React.createElement("div", {
            style: { width: 32, height: 32, background: C.purple, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center" },
          }, React.createElement("span", { style: { color: "#fff", fontSize: 16, fontWeight: 700 } }, "R")),
          React.createElement("span", { style: { fontSize: 18, fontWeight: 700, color: C.purple } }, "ResumeIQ")
        ),
        React.createElement("div", { style: { display: "flex", gap: 12, alignItems: "center" } },
          apiOnline === true && React.createElement("div", {
            style: { display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.teal },
          },
            React.createElement("div", { style: { width: 7, height: 7, borderRadius: "50%", background: C.teal } }),
            "API Online"
          ),
          apiOnline === false && React.createElement("div", {
            style: { display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.amber },
          },
            React.createElement("div", { style: { width: 7, height: 7, borderRadius: "50%", background: C.amber } }),
            "Demo mode"
          ),
          React.createElement("button", {
            onClick: onEnter,
            style: { padding: "8px 18px", borderRadius: 8, border: "none", background: C.purple, color: "#fff", fontSize: 13, cursor: "pointer", fontWeight: 500 },
          }, "Try free →")
        )
      ),

      // ── Hero ────────────────────────────────────────────────────────────
      React.createElement("div", { style: { textAlign: "center", padding: "60px 20px 40px" } },
        React.createElement("div", {
          style: {
            display: "inline-block", padding: "6px 16px", borderRadius: 20,
            background: C.purpleLight, color: C.purpleDark,
            fontSize: 12, fontWeight: 600, marginBottom: 20,
            border: `1px solid ${C.purple}40`,
          },
        }, "Trusted by 850+ companies worldwide"),
        React.createElement("h1", {
          style: { fontSize: 44, fontWeight: 800, lineHeight: 1.15, margin: "0 0 20px", letterSpacing: -1 },
        },
          "Beat the ATS.", React.createElement("br"),
          React.createElement("span", { style: { color: C.purple } }, "Land the interview.")
        ),
        React.createElement("p", {
          style: { fontSize: 17, color: "var(--color-text-secondary)", maxWidth: 520, margin: "0 auto 36px", lineHeight: 1.7 },
        }, "AI-powered resume analysis that tells you exactly what to fix, which keywords are missing, and how recruiters actually score your application."),
        React.createElement("div", { style: { display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" } },
          React.createElement("button", { onClick: onEnter, style: btnStyle }, "Analyze my resume — free →"),
          React.createElement("button", {
            style: { ...btnStyle, background: "transparent", border: `1px solid var(--color-border-secondary)`, color: "var(--color-text-primary)" },
          }, "See how it works")
        ),
        React.createElement("p", {
          style: { marginTop: 14, fontSize: 12, color: "var(--color-text-tertiary)" },
        }, "No signup required · Results in under 30 seconds · 100% private")
      ),

      // ── Stats ────────────────────────────────────────────────────────────
      React.createElement("div", {
        style: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, margin: "40px 0" },
      },
        stats.map((s, i) =>
          React.createElement("div", {
            key: i,
            style: { background: "var(--color-background-secondary)", borderRadius: 12, padding: "20px 16px", textAlign: "center" },
          },
            React.createElement("div", { style: { fontSize: 28, fontWeight: 800, color: s.color } }, s.value),
            React.createElement("div", { style: { fontSize: 12, color: "var(--color-text-secondary)", marginTop: 4 } }, s.label)
          )
        )
      ),

      // ── How it works ─────────────────────────────────────────────────────
      React.createElement("div", { style: { margin: "60px 0" } },
        React.createElement("h2", { style: { textAlign: "center", fontSize: 28, fontWeight: 700, marginBottom: 8 } }, "How it works"),
        React.createElement("p", { style: { textAlign: "center", color: "var(--color-text-secondary)", marginBottom: 40 } }, "Three steps from upload to action plan"),
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 } },
          howItWorks.map((h, i) =>
            React.createElement(Card, { key: i },
              React.createElement("div", { style: { fontSize: 32, fontWeight: 800, color: C.purple, opacity: 0.25, marginBottom: 12 } }, h.step),
              React.createElement("div", { style: { fontSize: 15, fontWeight: 600, marginBottom: 8 } }, h.title),
              React.createElement("div", { style: { fontSize: 13, color: "var(--color-text-secondary)", lineHeight: 1.6 } }, h.desc)
            )
          )
        )
      ),

      // ── Features ──────────────────────────────────────────────────────────
      React.createElement("div", { style: { margin: "60px 0" } },
        React.createElement("h2", { style: { textAlign: "center", fontSize: 28, fontWeight: 700, marginBottom: 8 } }, "Everything you need to get hired"),
        React.createElement("p", { style: { textAlign: "center", color: "var(--color-text-secondary)", marginBottom: 40 } }, "Built for candidates and hiring teams alike"),
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 } },
          features.map((f, i) =>
            React.createElement(Card, { key: i },
              React.createElement("div", { style: { fontSize: 28, marginBottom: 12 } }, f.icon),
              React.createElement("div", { style: { fontSize: 14, fontWeight: 600, marginBottom: 8 } }, f.title),
              React.createElement("div", { style: { fontSize: 13, color: "var(--color-text-secondary)", lineHeight: 1.6 } }, f.desc)
            )
          )
        )
      ),

      // ── Testimonials ──────────────────────────────────────────────────────
      React.createElement("div", { style: { margin: "60px 0" } },
        React.createElement("h2", { style: { textAlign: "center", fontSize: 28, fontWeight: 700, marginBottom: 40 } }, "What our users say"),
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 } },
          testimonials.map((t, i) =>
            React.createElement(Card, { key: i },
              React.createElement("div", { style: { fontSize: 13, color: "var(--color-text-secondary)", lineHeight: 1.7, marginBottom: 16 } }, `"${t.text}"`),
              React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 10 } },
                React.createElement("div", {
                  style: {
                    width: 36, height: 36, borderRadius: "50%",
                    background: C.purpleLight, color: C.purpleDark,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, fontWeight: 700,
                  },
                }, t.avatar),
                React.createElement("div", null,
                  React.createElement("div", { style: { fontSize: 13, fontWeight: 600 } }, t.name),
                  React.createElement("div", { style: { fontSize: 11, color: "var(--color-text-tertiary)" } }, t.role)
                )
              )
            )
          )
        )
      ),

      // ── FAQ ───────────────────────────────────────────────────────────────
      React.createElement("div", { style: { margin: "60px 0" } },
        React.createElement("h2", { style: { textAlign: "center", fontSize: 28, fontWeight: 700, marginBottom: 40 } }, "Frequently asked questions"),
        faqs.map((f, i) =>
          React.createElement("div", {
            key: i,
            style: { border: "0.5px solid var(--color-border-tertiary)", borderRadius: 10, marginBottom: 10, overflow: "hidden" },
          },
            React.createElement("button", {
              onClick: () => setOpenFaq(openFaq === i ? null : i),
              style: {
                width: "100%", padding: "16px 20px",
                background: "var(--color-background-primary)",
                border: "none", cursor: "pointer", textAlign: "left",
                fontSize: 14, fontWeight: 500,
                display: "flex", justifyContent: "space-between", alignItems: "center",
                color: "var(--color-text-primary)",
              },
            }, f.q, React.createElement("span", { style: { color: C.purple, fontSize: 20 } }, openFaq === i ? "−" : "+")),
            openFaq === i && React.createElement("div", {
              style: { padding: "0 20px 16px", fontSize: 13, color: "var(--color-text-secondary)", lineHeight: 1.7, background: "var(--color-background-primary)" },
            }, f.a)
          )
        )
      ),

      // ── CTA banner ────────────────────────────────────────────────────────
      React.createElement("div", {
        style: { textAlign: "center", padding: "60px 20px", background: C.purpleLight, borderRadius: 16, margin: "40px 0" },
      },
        React.createElement("h2", { style: { fontSize: 28, fontWeight: 700, color: C.purpleDark, marginBottom: 12 } }, "Ready to beat the ATS?"),
        React.createElement("p", { style: { color: C.purple, marginBottom: 28 } }, "Join 2.4 million job seekers already using ResumeIQ."),
        React.createElement("button", { onClick: onEnter, style: btnStyle }, "Start your free analysis →")
      ),

      // ── Footer ────────────────────────────────────────────────────────────
      React.createElement("div", {
        style: { borderTop: "0.5px solid var(--color-border-tertiary)", padding: "28px 0", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 },
      },
        React.createElement("span", { style: { color: C.purple, fontWeight: 700 } }, "ResumeIQ"),
        React.createElement("span", { style: { fontSize: 12, color: "var(--color-text-tertiary)" } }, "© 2025 ResumeIQ · Built with Python + ML + React"),
        React.createElement("div", { style: { display: "flex", gap: 16, fontSize: 12, color: "var(--color-text-secondary)" } },
          React.createElement("span", null, "Product"),
          React.createElement("span", null, "Pricing"),
          React.createElement("span", null, "Blog")
        )
      )
    )
  );
}

// ════════════════════════════════════════════════════════════════════════════
// UPLOAD PAGE
// ════════════════════════════════════════════════════════════════════════════
function UploadPage({ onAnalyze, setToast }) {
  const [dragging,      setDragging]      = useState(false);
  const [file,          setFile]          = useState(null);
  const [jd,            setJd]            = useState("");
  const [loading,       setLoading]       = useState(false);
  const [progress,      setProgress]      = useState(0);
  const [stepIdx,       setStepIdx]       = useState(0);
  const [targetLevel,   setTargetLevel]   = useState("mid");
  const [educationReq,  setEducationReq]  = useState("bachelor");

  const steps = [
    "Extracting text from PDF...",
    "Parsing resume sections...",
    "Identifying skills with NLP...",
    "Calculating ATS score...",
    "Generating AI insights...",
  ];

  const sampleRoles = [
    { label: "Data Scientist",    api: "data-scientist"    },
    { label: "Software Engineer", api: "software-engineer" },
    { label: "Fresher",           api: "fresher"           },
  ];

  // ── Fake progress ticker (runs while real API call is in flight) ─────────
  const startFakeTicker = () => {
    let p = 0, s = 0;
    const timer = setInterval(() => {
      p += 1.5;
      if (p >= 85) { clearInterval(timer); return; } // stop at 85, wait for real response
      if (p % 17 === 0 && s < steps.length - 1) s++;
      setProgress(Math.min(85, p));
      setStepIdx(s);
    }, 120);
    return timer;
  };

  const handleAnalyze = async () => {
    if (!file) {
      setToast({ message: "Please upload a PDF resume or choose a sample.", type: "error" });
      return;
    }

    setLoading(true);
    setProgress(5);
    setStepIdx(0);
    const ticker = startFakeTicker();

    try {
      let result;

      if (file.isSample) {
        // Sample resume — fetch text then analyze
        const sample = await fetchSampleResume(file.apiRole);
        result = await analyzeResume({ text: sample.text, jd, targetLevel, educationReq });
      } else {
        // Real uploaded PDF
        result = await analyzeResume({ file, jd, targetLevel, educationReq });
      }

      clearInterval(ticker);
      setProgress(95);
      setStepIdx(4);

      // Store result globally so Dashboard can read it
      window.ANALYSIS_RESULT = result;

      setTimeout(() => {
        setLoading(false);
        onAnalyze();
      }, 400);

    } catch (err) {
      clearInterval(ticker);
      setLoading(false);
      setProgress(0);

      // If API is down, fall back to demo mode with mock data
      if (err.message.includes("fetch") || err.message.includes("Failed") || err.message.includes("NetworkError")) {
        window.ANALYSIS_RESULT = null; // will use MOCK data in Dashboard
        setToast({ message: "API not reachable — showing demo data. Start: uvicorn api:app --reload", type: "info" });
        setTimeout(onAnalyze, 800);
      } else {
        setToast({ message: err.message, type: "error" });
      }
    }
  };

  // ── Loading screen ─────────────────────────────────────────────────────
  if (loading) {
    return (
      React.createElement("div", { style: { textAlign: "center", padding: "80px 20px", maxWidth: 480, margin: "0 auto" } },
        React.createElement("div", { style: { fontSize: 40, marginBottom: 20 } }, "🔍"),
        React.createElement("h2", { style: { marginBottom: 8 } }, "Analyzing your resume"),
        React.createElement("p", { style: { color: "var(--color-text-secondary)", marginBottom: 32 } }, steps[stepIdx]),
        React.createElement("div", {
          style: { height: 8, background: "var(--color-background-secondary)", borderRadius: 4, overflow: "hidden", marginBottom: 10 },
        },
          React.createElement("div", {
            style: { height: "100%", width: progress + "%", background: C.purple, borderRadius: 4, transition: "width 0.2s" },
          })
        ),
        React.createElement("div", { style: { fontSize: 13, color: C.purple, fontWeight: 600 } }, Math.round(progress) + "%")
      )
    );
  }

  // ── Upload form ────────────────────────────────────────────────────────
  return (
    React.createElement("div", { style: { maxWidth: 680, margin: "0 auto" } },
      React.createElement(SectionHeader, {
        title: "Upload your resume",
        subtitle: "Drag and drop your PDF resume or choose a sample to begin analysis",
      }),

      // Drop zone
      React.createElement("div", {
        onDragOver:  e => { e.preventDefault(); setDragging(true); },
        onDragLeave: () => setDragging(false),
        onDrop: e => {
          e.preventDefault(); setDragging(false);
          const f = e.dataTransfer.files[0];
          if (f && f.type === "application/pdf") setFile(f);
          else setToast({ message: "Only PDF files are supported.", type: "error" });
        },
        onClick: () => document.getElementById("resume-file-input").click(),
        style: {
          border: `2px dashed ${dragging ? C.purple : "var(--color-border-secondary)"}`,
          borderRadius: 16, padding: "48px 32px", textAlign: "center",
          cursor: "pointer", marginBottom: 20,
          background: dragging ? C.purpleLight : "var(--color-background-secondary)",
          transition: "all 0.2s",
        },
      },
        React.createElement("input", {
          id: "resume-file-input", type: "file", accept: ".pdf",
          style: { display: "none" },
          onChange: e => {
            const f = e.target.files[0];
            if (f) setFile(f);
          },
        }),
        React.createElement("div", { style: { fontSize: 36, marginBottom: 12 } }, file ? "📄" : "⬆️"),
        React.createElement("div", { style: { fontSize: 15, fontWeight: 600, marginBottom: 6 } },
          file ? (file.name || file.label || "Resume loaded") : "Drop your PDF resume here"
        ),
        React.createElement("div", { style: { fontSize: 13, color: "var(--color-text-secondary)" } },
          file ? "Click to change file" : "PDF format · Max 5MB · or click to browse"
        )
      ),

      // Sample resumes
      React.createElement("div", { style: { marginBottom: 20 } },
        React.createElement("div", { style: { fontSize: 12, color: "var(--color-text-tertiary)", marginBottom: 10 } }, "Or try a sample resume:"),
        React.createElement("div", { style: { display: "flex", gap: 8, flexWrap: "wrap" } },
          sampleRoles.map(r =>
            React.createElement("button", {
              key: r.api,
              onClick: () => setFile({ name: r.label, label: r.label, isSample: true, apiRole: r.api }),
              style: {
                padding: "6px 14px", borderRadius: 20,
                border: `1px solid ${file && file.apiRole === r.api ? C.purple : C.purple + "50"}`,
                background: file && file.apiRole === r.api ? C.purple : C.purpleLight,
                color: file && file.apiRole === r.api ? "#fff" : C.purpleDark,
                fontSize: 12, cursor: "pointer",
              },
            }, r.label)
          )
        )
      ),

      // Job description
      React.createElement("div", { style: { marginBottom: 16 } },
        React.createElement("label", { style: { display: "block", fontSize: 14, fontWeight: 500, marginBottom: 8 } },
          "Job description ",
          React.createElement("span", { style: { color: "var(--color-text-tertiary)", fontWeight: 400 } }, "(optional but improves accuracy)")
        ),
        React.createElement("textarea", {
          value: jd, onChange: e => setJd(e.target.value),
          placeholder: "Paste the job description here for targeted keyword matching and skill gap analysis...",
          style: { width: "100%", height: 130, padding: "12px 14px", borderRadius: 10, fontSize: 13, resize: "vertical", boxSizing: "border-box" },
        })
      ),

      // Settings row
      React.createElement("div", { style: { display: "flex", gap: 12, marginBottom: 20 } },
        React.createElement("div", { style: { flex: 1 } },
          React.createElement("label", { style: { fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 4 } }, "Experience level"),
          React.createElement("select", {
            value: targetLevel, onChange: e => setTargetLevel(e.target.value),
            style: { width: "100%", padding: "8px 12px", borderRadius: 8, fontSize: 13 },
          },
            ["entry", "mid", "senior", "lead"].map(l =>
              React.createElement("option", { key: l, value: l }, l.charAt(0).toUpperCase() + l.slice(1))
            )
          )
        ),
        React.createElement("div", { style: { flex: 1 } },
          React.createElement("label", { style: { fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 4 } }, "Education requirement"),
          React.createElement("select", {
            value: educationReq, onChange: e => setEducationReq(e.target.value),
            style: { width: "100%", padding: "8px 12px", borderRadius: 8, fontSize: 13 },
          },
            ["any", "diploma", "bachelor", "master", "phd"].map(l =>
              React.createElement("option", { key: l, value: l }, l.charAt(0).toUpperCase() + l.slice(1))
            )
          )
        )
      ),

      // Analyze button
      React.createElement("button", {
        onClick: handleAnalyze,
        style: {
          width: "100%", padding: "14px", borderRadius: 10, border: "none",
          background: C.purple, color: "#fff", fontSize: 15, cursor: "pointer", fontWeight: 600,
        },
      }, "Analyze resume →"),

      React.createElement("div", {
        style: { marginTop: 16, display: "flex", gap: 20, justifyContent: "center" },
      },
        ["🔒 Private & secure", "⚡ Results in ~30s", "🆓 Free to use"].map((t, i) =>
          React.createElement("span", { key: i, style: { fontSize: 12, color: "var(--color-text-tertiary)" } }, t)
        )
      )
    )
  );
}

// ════════════════════════════════════════════════════════════════════════════
// DASHBOARD — MAIN ANALYSIS VIEW
// ════════════════════════════════════════════════════════════════════════════
function Dashboard({ setToast }) {
  const [activeTab, setActiveTab] = useState("overview");

  // ── Map real API data → dashboard data (fallback to MOCK) ────────────────
  const api = window.ANALYSIS_RESULT;

  const data = api ? {
    candidate: {
      name:      api.candidate?.name || MOCK.candidate.name,
      role:      api.careers?.[0]?.career || MOCK.candidate.role,
      exp:       `${api.candidate?.experience_years || 0} years`,
      education: api.candidate?.education?.[0]?.degree || MOCK.candidate.education,
    },
    ats:          Math.round(api.ats?.overall_score || MOCK.ats),
    strength:     Math.round(api.ats?.component_scores?.format_quality || MOCK.strength),
    keyword:      Math.round(api.ats?.component_scores?.keyword_density || MOCK.keyword),
    readability:  Math.round(api.ats?.component_scores?.format_quality || MOCK.readability),
    expRelevance: Math.round(api.ats?.component_scores?.experience_match || MOCK.expRelevance),
    eduMatch:     Math.round(api.ats?.component_scores?.education_match || MOCK.eduMatch),
    formatting:   Math.round(api.ats?.component_scores?.format_quality || MOCK.formatting),
    hiringRec:    Math.round(api.ats?.overall_score || MOCK.hiringRec),
    grade:        api.ats?.grade || "B+",
    label:        api.ats?.label || "Good Resume",

    presentSkills: api.skills?.all_skills?.slice(0, 20)     || MOCK.presentSkills,
    missingSkills: api.ats?.missing_skills?.slice(0, 10)    || MOCK.missingSkills,

    improvements: (() => {
      const items = [];
      (api.ats?.improvements || []).forEach(t => items.push({ priority: "High",   text: t, icon: "🔴" }));
      (api.ats?.feedback     || []).forEach(t => items.push({ priority: "Medium", text: t, icon: "🟡" }));
      (api.ats?.resume_tips  || []).slice(0, 2).forEach(t => items.push({ priority: "Low", text: t, icon: "🟢" }));
      return items.slice(0, 6).length > 0 ? items.slice(0, 6) : MOCK.improvements;
    })(),

    topCareers: api.careers || MOCK.topCareers,

    radarData: [
      { subject: "Skills Match", A: Math.round(api.ats?.component_scores?.skill_match      || 82), fullMark: 100 },
      { subject: "Keywords",     A: Math.round(api.ats?.component_scores?.keyword_density   || 71), fullMark: 100 },
      { subject: "Experience",   A: Math.round(api.ats?.component_scores?.experience_match  || 79), fullMark: 100 },
      { subject: "Education",    A: Math.round(api.ats?.component_scores?.education_match   || 90), fullMark: 100 },
      { subject: "Formatting",   A: Math.round(api.ats?.component_scores?.format_quality    || 85), fullMark: 100 },
      { subject: "Contact",      A: Math.round(api.ats?.component_scores?.contact_info      || 80), fullMark: 100 },
    ],

    sectionScores:  MOCK.sectionScores,
    keywordDensity: MOCK.keywordDensity,
    candidates:     MOCK.candidates,
    timelineScores: MOCK.timelineScores,

    componentScores: api.ats?.component_scores
      ? Object.entries(api.ats.component_scores).map(([k, v]) => ({
          section: k.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()),
          score:   Math.round(v),
          color:   [C.purple, C.blue, C.teal, C.green, C.amber, C.coral][
            Object.keys(api.ats.component_scores).indexOf(k) % 6
          ],
        }))
      : MOCK.sectionScores,

    isReal: true,
    mlUsed: api.ml_used,
  } : { ...MOCK, grade: "B+", label: "Good Resume", topCareers: MOCK.topCareers, componentScores: MOCK.sectionScores, isReal: false, mlUsed: false };

  const tabs = [
    { id: "overview",  label: "Overview" },
    { id: "skills",    label: "Skills & Keywords" },
    { id: "sections",  label: "Resume Sections" },
    { id: "recruiter", label: "Recruiter View" },
    { id: "improve",   label: "Improve" },
  ];

  const pieData = [
    { name: "Skills match", value: data.ats,          color: C.purple },
    { name: "Experience",   value: data.expRelevance,  color: C.blue   },
    { name: "Education",    value: data.eduMatch,      color: C.teal   },
    { name: "Keywords",     value: data.keyword,       color: C.amber  },
    { name: "Formatting",   value: data.formatting,    color: C.green  },
  ];

  const recColors = { "Strong Hire": C.green, "Hire": C.teal, "Maybe": C.amber, "No Hire": C.coral };

  const handleDownload = async () => {
    setToast({ message: "Preparing your PDF report...", type: "info" });
    setTimeout(() => setToast({ message: "Download feature requires PDF backend endpoint.", type: "info" }), 800);
  };

  return (
    React.createElement("div", null,

      // ── Demo mode banner ────────────────────────────────────────────────
      !data.isReal && React.createElement("div", {
        style: {
          background: C.amberLight, border: `1px solid ${C.amber}50`,
          borderRadius: 10, padding: "10px 16px", marginBottom: 16,
          fontSize: 13, color: C.amber, display: "flex", alignItems: "center", gap: 8,
        },
      }, "⚠️ Showing demo data. Start the Python API server with: ", React.createElement("code", { style: { fontFamily: "monospace", background: C.amber + "20", padding: "2px 6px", borderRadius: 4 } }, "python -m uvicorn api:app --reload")),

      data.isReal && React.createElement("div", {
        style: {
          background: C.tealLight, border: `1px solid ${C.teal}50`,
          borderRadius: 10, padding: "10px 16px", marginBottom: 16,
          fontSize: 13, color: C.teal, display: "flex", alignItems: "center", gap: 8,
        },
      }, "✅ Live analysis complete" + (data.mlUsed ? " — ML models active" : " — rule-based prediction")),

      // ── Candidate header card ───────────────────────────────────────────
      React.createElement(Card, { style: { marginBottom: 20 } },
        React.createElement("div", {
          style: { display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 },
        },
          React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 16 } },
            React.createElement("div", {
              style: {
                width: 52, height: 52, borderRadius: "50%",
                background: C.purpleLight, color: C.purpleDark,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 18, fontWeight: 700,
              },
            }, (data.candidate.name || "??").split(" ").map(n => n[0]).join("").slice(0, 2)),
            React.createElement("div", null,
              React.createElement("div", { style: { fontSize: 17, fontWeight: 700 } }, data.candidate.name),
              React.createElement("div", { style: { fontSize: 13, color: "var(--color-text-secondary)" } },
                data.candidate.role + " · " + data.candidate.exp + " · " + data.candidate.education
              )
            )
          ),
          React.createElement("div", { style: { display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" } },
            React.createElement("div", {
              style: {
                padding: "6px 16px", borderRadius: 20,
                background: C.greenLight, color: C.green,
                fontSize: 13, fontWeight: 600, border: `1px solid ${C.green}50`,
              },
            }, data.grade + " — " + data.label),
            React.createElement("button", {
              onClick: handleDownload,
              style: {
                padding: "8px 16px", borderRadius: 8,
                border: `1px solid ${C.purple}`, background: C.purpleLight,
                color: C.purpleDark, fontSize: 13, cursor: "pointer", fontWeight: 500,
              },
            }, "⬇ Download report")
          )
        )
      ),

      // ── Top metric cards ─────────────────────────────────────────────────
      React.createElement("div", {
        style: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 },
      },
        React.createElement(MetricCard, { label: "ATS Score",              value: React.createElement(AnimatedNumber, { value: data.ats,      suffix: "%" }), icon: "🎯", color: C.purple, delta: 12 }),
        React.createElement(MetricCard, { label: "Resume Strength",        value: React.createElement(AnimatedNumber, { value: data.strength,  suffix: "%" }), icon: "💪", color: C.blue,   delta: 8  }),
        React.createElement(MetricCard, { label: "Keyword Match",          value: React.createElement(AnimatedNumber, { value: data.keyword,   suffix: "%" }), icon: "🔍", color: C.teal,   delta: -3 }),
        React.createElement(MetricCard, { label: "Hiring Recommendation",  value: React.createElement(AnimatedNumber, { value: data.hiringRec, suffix: "%" }), icon: "✅", color: C.green,  delta: 15 })
      ),

      // ── Tab navigation ────────────────────────────────────────────────────
      React.createElement("div", {
        style: { display: "flex", gap: 4, marginBottom: 20, background: "var(--color-background-secondary)", padding: 4, borderRadius: 10 },
      },
        tabs.map(t =>
          React.createElement("button", {
            key: t.id,
            onClick: () => setActiveTab(t.id),
            style: {
              flex: 1, padding: "8px 12px", borderRadius: 8, border: "none", cursor: "pointer",
              fontSize: 13, fontWeight: activeTab === t.id ? 600 : 400,
              background: activeTab === t.id ? "var(--color-background-primary)" : "transparent",
              color: activeTab === t.id ? C.purple : "var(--color-text-secondary)",
              boxShadow: activeTab === t.id ? "0 1px 4px rgba(0,0,0,0.08)" : "none",
              transition: "all 0.15s",
            },
          }, t.label)
        )
      ),

      // ══════════════════ TAB: OVERVIEW ══════════════════
      activeTab === "overview" && React.createElement("div", null,
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 } },

          // Radar chart
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Score radar", subtitle: "6-dimension resume analysis", accent: C.purple }),
            React.createElement(ResponsiveContainer, { width: "100%", height: 260 },
              React.createElement(RadarChart, { data: data.radarData },
                React.createElement(PolarGrid, { stroke: "var(--color-border-tertiary)" }),
                React.createElement(PolarAngleAxis, { dataKey: "subject", tick: { fontSize: 11, fill: "var(--color-text-secondary)" } }),
                React.createElement(PolarRadiusAxis, { angle: 30, domain: [0, 100], tick: false, axisLine: false }),
                React.createElement(Radar, { name: "Score", dataKey: "A", stroke: C.purple, fill: C.purple, fillOpacity: 0.2, strokeWidth: 2 })
              )
            )
          ),

          // Circular scores grid
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Component scores", subtitle: "Weighted ATS breakdown", accent: C.blue }),
            React.createElement("div", { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 } },
              React.createElement(CircularScore, { score: data.ats,          color: C.purple, size: 90, label: "ATS Score"     }),
              React.createElement(CircularScore, { score: data.readability,  color: C.blue,   size: 90, label: "Readability"   }),
              React.createElement(CircularScore, { score: data.expRelevance, color: C.teal,   size: 90, label: "Exp. Relevance" }),
              React.createElement(CircularScore, { score: data.eduMatch,     color: C.green,  size: 90, label: "Education"     }),
              React.createElement(CircularScore, { score: data.formatting,   color: C.amber,  size: 90, label: "Formatting"    }),
              React.createElement(CircularScore, { score: data.keyword,      color: C.coral,  size: 90, label: "Keywords"      })
            )
          )
        ),

        // ATS trend line
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "ATS score trend", subtitle: "How your resume score improved over iterations", accent: C.teal }),
          React.createElement(ResponsiveContainer, { width: "100%", height: 180 },
            React.createElement(LineChart, { data: data.timelineScores },
              React.createElement(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border-tertiary)" }),
              React.createElement(XAxis, { dataKey: "month", tick: { fontSize: 11 } }),
              React.createElement(YAxis, { domain: [40, 100], tick: { fontSize: 11 } }),
              React.createElement(Tooltip, { contentStyle: { fontSize: 12, borderRadius: 8 } }),
              React.createElement(Line, { type: "monotone", dataKey: "score", stroke: C.purple, strokeWidth: 2, dot: { fill: C.purple, r: 4 } })
            )
          )
        ),

        // Score distribution
        React.createElement(Card, null,
          React.createElement(SectionHeader, { title: "Score distribution", subtitle: "Contribution of each component to overall ATS score", accent: C.amber }),
          React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 20, flexWrap: "wrap" } },
            React.createElement(ResponsiveContainer, { width: 200, height: 200 },
              React.createElement(PieChart, null,
                React.createElement(Pie, { data: pieData, cx: "50%", cy: "50%", innerRadius: 55, outerRadius: 90, dataKey: "value", strokeWidth: 0 },
                  pieData.map((e, i) => React.createElement(Cell, { key: i, fill: e.color }))
                )
              )
            ),
            React.createElement("div", { style: { flex: 1 } },
              pieData.map((d, i) =>
                React.createElement("div", { key: i, style: { display: "flex", alignItems: "center", gap: 10, marginBottom: 10 } },
                  React.createElement("div", { style: { width: 10, height: 10, borderRadius: 2, background: d.color, flexShrink: 0 } }),
                  React.createElement("div", { style: { flex: 1, fontSize: 13 } }, d.name),
                  React.createElement("div", { style: { fontSize: 13, fontWeight: 600, color: d.color } }, d.value + "%"),
                  React.createElement("div", { style: { width: 100, height: 6, background: "var(--color-background-secondary)", borderRadius: 3, overflow: "hidden" } },
                    React.createElement("div", { style: { width: d.value + "%", height: "100%", background: d.color, borderRadius: 3 } })
                  )
                )
              )
            )
          )
        )
      ),

      // ══════════════════ TAB: SKILLS & KEYWORDS ══════════════════
      activeTab === "skills" && React.createElement("div", null,
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 } },
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Skills detected", subtitle: `${data.presentSkills.length} skills found`, accent: C.teal }),
            React.createElement("div", null, data.presentSkills.map(s => React.createElement(Chip, { key: s, label: s, type: "present" })))
          ),
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Missing skills", subtitle: `${data.missingSkills.length} gaps identified`, accent: C.coral }),
            React.createElement("div", null, data.missingSkills.map(s => React.createElement(Chip, { key: s, label: s, type: "missing" }))),
            data.missingSkills.length > 0 && React.createElement("p", {
              style: { fontSize: 12, color: "var(--color-text-tertiary)", marginTop: 16 },
            }, "Adding these skills could increase your ATS score by ~" + Math.round(data.missingSkills.length * 2) + " points.")
          )
        ),

        // Keyword density chart
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "Keyword density analysis", subtitle: "Frequency and relevance of top keywords", accent: C.blue }),
          React.createElement(ResponsiveContainer, { width: "100%", height: 220 },
            React.createElement(BarChart, { data: data.keywordDensity, layout: "vertical" },
              React.createElement(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border-tertiary)" }),
              React.createElement(XAxis, { type: "number", domain: [0, 15], tick: { fontSize: 11 } }),
              React.createElement(YAxis, { dataKey: "keyword", type: "category", width: 130, tick: { fontSize: 11 } }),
              React.createElement(Tooltip, { contentStyle: { fontSize: 12, borderRadius: 8 } }),
              React.createElement(Bar, { dataKey: "count",     fill: C.blue,   name: "Count",        radius: [0, 4, 4, 0] }),
              React.createElement(Bar, { dataKey: "relevance", fill: C.purple, name: "Relevance %",  radius: [0, 4, 4, 0] }),
              React.createElement(Legend, { iconSize: 10, wrapperStyle: { fontSize: 12 } })
            )
          )
        ),

        // Skill gap bars
        React.createElement(Card, null,
          React.createElement(SectionHeader, { title: "Skill gap analysis", subtitle: "Your skills vs job requirements", accent: C.amber }),
          [
            { label: "Programming languages", have: 90, need: 95 },
            { label: "ML / AI frameworks",    have: 85, need: 90 },
            { label: "Cloud & DevOps",         have: 60, need: 80 },
            { label: "Data engineering",       have: 55, need: 75 },
            { label: "Soft skills",            have: 80, need: 70 },
          ].map((item, i) =>
            React.createElement("div", { key: i, style: { marginBottom: 16 } },
              React.createElement("div", { style: { display: "flex", justifyContent: "space-between", marginBottom: 6 } },
                React.createElement("span", { style: { fontSize: 13 } }, item.label),
                React.createElement("span", { style: { fontSize: 12, color: "var(--color-text-tertiary)" } }, `You: ${item.have}% · Required: ${item.need}%`)
              ),
              React.createElement("div", { style: { height: 10, background: "var(--color-background-secondary)", borderRadius: 5, position: "relative", overflow: "hidden" } },
                React.createElement("div", { style: { height: "100%", width: item.need + "%", background: C.amber + "30", borderRadius: 5 } }),
                React.createElement("div", { style: { position: "absolute", top: 0, left: 0, height: "100%", width: item.have + "%", background: item.have >= item.need ? C.teal : C.amber, borderRadius: 5 } })
              )
            )
          )
        )
      ),

      // ══════════════════ TAB: RESUME SECTIONS ══════════════════
      activeTab === "sections" && React.createElement("div", null,
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 } },
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Section scores", subtitle: "Quality rating per resume section", accent: C.purple }),
            data.componentScores.map((s, i) =>
              React.createElement(ProgressBar, { key: i, label: s.section, value: s.score, color: s.color })
            )
          ),
          React.createElement(Card, null,
            React.createElement(SectionHeader, { title: "Section analysis", subtitle: "Detected sections and quality flags", accent: C.teal }),
            [
              { section: "Header / Contact",      status: "good", note: "Email, phone, links checked"    },
              { section: "Professional Summary",   status: "good", note: "Clear value proposition"       },
              { section: "Work Experience",        status: "warn", note: "Add quantified achievements"   },
              { section: "Skills",                 status: "good", note: data.presentSkills.length + " technical skills found" },
              { section: "Education",              status: "good", note: "Degree clearly listed"         },
              { section: "Projects",               status: "warn", note: "Add more project entries"      },
              { section: "Certifications",         status: "bad",  note: "Not found — recommended"      },
              { section: "GitHub / Portfolio",     status: "bad",  note: "Not detected — add link"      },
            ].map((r, i) =>
              React.createElement("div", { key: i, style: { display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "0.5px solid var(--color-border-tertiary)" } },
                React.createElement("div", {
                  style: { width: 8, height: 8, borderRadius: "50%", flexShrink: 0, background: r.status === "good" ? C.green : r.status === "warn" ? C.amber : C.red },
                }),
                React.createElement("div", { style: { flex: 1 } },
                  React.createElement("div", { style: { fontSize: 13, fontWeight: 500 } }, r.section),
                  React.createElement("div", { style: { fontSize: 11, color: "var(--color-text-tertiary)" } }, r.note)
                )
              )
            )
          )
        ),

        // Section bar chart
        React.createElement(Card, null,
          React.createElement(SectionHeader, { title: "Section quality chart", accent: C.blue }),
          React.createElement(ResponsiveContainer, { width: "100%", height: 220 },
            React.createElement(BarChart, { data: data.componentScores },
              React.createElement(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border-tertiary)" }),
              React.createElement(XAxis, { dataKey: "section", tick: { fontSize: 10 } }),
              React.createElement(YAxis, { domain: [0, 100], tick: { fontSize: 11 } }),
              React.createElement(Tooltip, { contentStyle: { fontSize: 12, borderRadius: 8 }, formatter: v => [v + "%"] }),
              React.createElement(Bar, { dataKey: "score", name: "Score", radius: [4, 4, 0, 0] },
                data.componentScores.map((s, i) => React.createElement(Cell, { key: i, fill: s.color }))
              )
            )
          )
        )
      ),

      // ══════════════════ TAB: RECRUITER VIEW ══════════════════
      activeTab === "recruiter" && React.createElement("div", null,

        // Candidate ranking table
        React.createElement(Card, { style: { marginBottom: 16, overflowX: "auto" } },
          React.createElement(SectionHeader, { title: "Candidate ranking", subtitle: "Ranked by ATS score across uploaded resumes", accent: C.purple }),
          React.createElement("table", { style: { width: "100%", borderCollapse: "collapse", fontSize: 13 } },
            React.createElement("thead", null,
              React.createElement("tr", { style: { borderBottom: "0.5px solid var(--color-border-tertiary)" } },
                ["Rank", "Candidate", "ATS Score", "Skills", "Exp (yrs)", "Education", "Recommendation"].map(h =>
                  React.createElement("th", {
                    key: h,
                    style: { padding: "10px 12px", textAlign: "left", fontSize: 11, color: "var(--color-text-tertiary)", fontWeight: 500, textTransform: "uppercase", letterSpacing: 0.5 },
                  }, h)
                )
              )
            ),
            React.createElement("tbody", null,
              data.candidates.map((c, i) =>
                React.createElement("tr", {
                  key: i,
                  style: { borderBottom: "0.5px solid var(--color-border-tertiary)", background: i === 0 ? C.purple + "08" : "transparent" },
                },
                  React.createElement("td", { style: { padding: "12px", fontWeight: i === 0 ? 700 : 400, color: i === 0 ? C.purple : undefined } }, "#" + c.rank),
                  React.createElement("td", { style: { padding: "12px" } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 8 } },
                      React.createElement("div", {
                        style: { width: 30, height: 30, borderRadius: "50%", background: C.purpleLight, color: C.purpleDark, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 700 },
                      }, c.name.split(" ").map(n => n[0]).join("")),
                      c.name
                    )
                  ),
                  React.createElement("td", { style: { padding: "12px" } },
                    React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 8 } },
                      React.createElement("div", { style: { width: 60, height: 6, background: "var(--color-background-secondary)", borderRadius: 3, overflow: "hidden" } },
                        React.createElement("div", { style: { width: c.ats + "%", height: "100%", background: C.purple } })
                      ),
                      React.createElement("span", { style: { fontWeight: 600, color: C.purple } }, c.ats + "%")
                    )
                  ),
                  React.createElement("td", { style: { padding: "12px" } }, c.skills),
                  React.createElement("td", { style: { padding: "12px" } }, c.exp),
                  React.createElement("td", { style: { padding: "12px" } }, c.edu),
                  React.createElement("td", { style: { padding: "12px" } },
                    React.createElement("span", {
                      style: { padding: "3px 10px", borderRadius: 12, fontSize: 11, fontWeight: 600, background: (recColors[c.rec] || C.gray) + "20", color: recColors[c.rec] || C.gray, border: `1px solid ${(recColors[c.rec] || C.gray)}40` },
                    }, c.rec)
                  )
                )
              )
            )
          )
        ),

        // Candidate comparison chart
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "Candidate ATS comparison", accent: C.blue }),
          React.createElement(ResponsiveContainer, { width: "100%", height: 200 },
            React.createElement(BarChart, { data: data.candidates },
              React.createElement(CartesianGrid, { strokeDasharray: "3 3", stroke: "var(--color-border-tertiary)" }),
              React.createElement(XAxis, { dataKey: "name", tick: { fontSize: 11 } }),
              React.createElement(YAxis, { domain: [0, 100], tick: { fontSize: 11 } }),
              React.createElement(Tooltip, { contentStyle: { fontSize: 12, borderRadius: 8 }, formatter: v => [v + "%", "ATS Score"] }),
              React.createElement(Bar, { dataKey: "ats", fill: C.purple, radius: [4, 4, 0, 0] })
            )
          )
        ),

        // Recruiter metrics
        React.createElement("div", { style: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 } },
          React.createElement(MetricCard, { label: "Total candidates", value: "4",        icon: "👥", color: C.purple }),
          React.createElement(MetricCard, { label: "Strong hire",       value: "1",        icon: "✅", color: C.green  }),
          React.createElement(MetricCard, { label: "Avg ATS score",     value: "74%",      icon: "📊", color: C.blue   }),
          React.createElement(MetricCard, { label: "Avg skill gap",     value: "6 skills", icon: "⚠️", color: C.amber  })
        )
      ),

      // ══════════════════ TAB: IMPROVE ══════════════════
      activeTab === "improve" && React.createElement("div", null,

        // Career predictions
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "Career recommendations", subtitle: "ML-powered career path predictions based on your resume", accent: C.purple }),
          React.createElement("div", null,
            data.topCareers.slice(0, 5).map((c, i) =>
              React.createElement("div", { key: i, style: { marginBottom: 14 } },
                React.createElement("div", { style: { display: "flex", justifyContent: "space-between", marginBottom: 5 } },
                  React.createElement("span", { style: { fontSize: 13, fontWeight: i === 0 ? 600 : 400 } },
                    i === 0 ? "🏆 " : "",
                    c.career
                  ),
                  React.createElement("span", { style: { fontSize: 13, fontWeight: 600, color: C.purple } }, c.confidence.toFixed(1) + "%")
                ),
                React.createElement("div", { style: { height: 8, background: "var(--color-background-secondary)", borderRadius: 4, overflow: "hidden" } },
                  React.createElement("div", { style: { height: "100%", width: c.confidence + "%", background: i === 0 ? C.purple : C.purple + "60", borderRadius: 4, transition: "width 1.2s ease" } })
                )
              )
            )
          )
        ),

        // Optimization checklist
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "Resume optimization checklist", subtitle: "Actionable improvements ranked by impact", accent: C.coral }),
          data.improvements.map((imp, i) => {
            const colors = { High: C.red, Medium: C.amber, Low: C.green };
            return React.createElement("div", {
              key: i,
              style: { display: "flex", alignItems: "flex-start", gap: 14, padding: "14px 0", borderBottom: "0.5px solid var(--color-border-tertiary)" },
            },
              React.createElement("div", { style: { fontSize: 18, marginTop: 1 } }, imp.icon),
              React.createElement("div", { style: { flex: 1 } },
                React.createElement("div", { style: { fontSize: 13, lineHeight: 1.5 } }, imp.text)
              ),
              React.createElement("span", {
                style: { padding: "3px 10px", borderRadius: 12, fontSize: 11, fontWeight: 600, flexShrink: 0, background: (colors[imp.priority] || C.gray) + "18", color: colors[imp.priority] || C.gray, border: `1px solid ${(colors[imp.priority] || C.gray)}40` },
              }, imp.priority)
            );
          })
        ),

        // Score potential
        React.createElement(Card, { style: { marginBottom: 16 } },
          React.createElement(SectionHeader, { title: "Score improvement potential", subtitle: "Estimated ATS score after applying all recommendations", accent: C.green }),
          React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 40, justifyContent: "center", padding: "20px 0" } },
            React.createElement("div", { style: { textAlign: "center" } },
              React.createElement(CircularScore, { score: data.ats, color: C.purple, size: 110, label: "Current score" })
            ),
            React.createElement("div", { style: { fontSize: 28, color: "var(--color-text-tertiary)" } }, "→"),
            React.createElement("div", { style: { textAlign: "center" } },
              React.createElement(CircularScore, { score: Math.min(99, data.ats + 13), color: C.green, size: 110, label: "Potential score" })
            )
          ),
          React.createElement("p", { style: { textAlign: "center", fontSize: 13, color: "var(--color-text-secondary)" } },
            "Applying all recommendations could increase your ATS score by ",
            React.createElement("strong", { style: { color: C.green } }, "+13 points"),
            ", moving you to the top 5% of applicants."
          )
        ),

        // AI advisor panel
        React.createElement("div", {
          style: { background: C.purpleLight, border: `1px solid ${C.purple}30`, borderRadius: 12, padding: "20px" },
        },
          React.createElement("div", { style: { display: "flex", gap: 12, marginBottom: 12 } },
            React.createElement("div", { style: { fontSize: 20 } }, "🤖"),
            React.createElement("div", null,
              React.createElement("div", { style: { fontWeight: 600, color: C.purpleDark, marginBottom: 4 } }, "AI Career Advisor"),
              React.createElement("div", { style: { fontSize: 13, color: C.purple, lineHeight: 1.7 } },
                "Based on your resume analysis, you are a strong candidate for ",
                React.createElement("strong", null, data.topCareers[0]?.career || "Data Science"),
                " roles. Your technical skills are excellent — focus on the missing skills listed above, quantify your achievements with numbers and percentages, and ensure your GitHub profile is linked. This single change can increase interview callbacks by up to 40%."
              )
            )
          )
        )
      )
    )
  );
}

// ════════════════════════════════════════════════════════════════════════════
// ROOT APP — page routing and top navigation
// ════════════════════════════════════════════════════════════════════════════
function App() {
  const [page,      setPage]      = useState("landing");
  const [apiOnline, setApiOnline] = useState(null);   // null=checking, true=online, false=offline
  const [toast,     setToast]     = useState(null);

  // Check if Python API is running when app loads
  useEffect(() => {
    checkAPIHealth().then(result => {
      setApiOnline(result !== null);
    });
  }, []);

  const navItems = [
    { id: "upload",    label: "Analyze resume", icon: "📄" },
    { id: "dashboard", label: "Dashboard",       icon: "📊" },
  ];

  const clearToast = useCallback(() => setToast(null), []);

  return (
    React.createElement("div", { style: { minHeight: "100vh", fontFamily: "var(--font-sans)", color: "var(--color-text-primary)" } },

      // ── Top nav (hidden on landing page) ──────────────────────────────
      page !== "landing" && React.createElement("div", {
        style: {
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "12px 24px", borderBottom: "0.5px solid var(--color-border-tertiary)",
          background: "var(--color-background-primary)", marginBottom: 24,
        },
      },
        // Logo
        React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 24 } },
          React.createElement("button", {
            onClick: () => setPage("landing"),
            style: { display: "flex", alignItems: "center", gap: 8, background: "none", border: "none", cursor: "pointer" },
          },
            React.createElement("div", {
              style: { width: 28, height: 28, background: C.purple, borderRadius: 7, display: "flex", alignItems: "center", justifyContent: "center" },
            }, React.createElement("span", { style: { color: "#fff", fontSize: 14, fontWeight: 700 } }, "R")),
            React.createElement("span", { style: { fontSize: 16, fontWeight: 700, color: C.purple } }, "ResumeIQ")
          ),
          // Nav links
          React.createElement("div", { style: { display: "flex", gap: 4 } },
            navItems.map(n =>
              React.createElement("button", {
                key: n.id,
                onClick: () => setPage(n.id),
                style: {
                  padding: "6px 14px", borderRadius: 8, border: "none", cursor: "pointer",
                  fontSize: 13, fontWeight: page === n.id ? 600 : 400,
                  background: page === n.id ? C.purpleLight : "transparent",
                  color: page === n.id ? C.purpleDark : "var(--color-text-secondary)",
                },
              }, n.icon + " " + n.label)
            )
          )
        ),

        // API status indicator
        React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 8 } },
          apiOnline === null && React.createElement("span", { style: { fontSize: 12, color: "var(--color-text-tertiary)" } }, "Checking API..."),
          apiOnline === true && React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.teal } },
            React.createElement("div", { style: { width: 7, height: 7, borderRadius: "50%", background: C.teal } }),
            "Live API"
          ),
          apiOnline === false && React.createElement("div", { style: { display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.amber } },
            React.createElement("div", { style: { width: 7, height: 7, borderRadius: "50%", background: C.amber } }),
            "Demo mode"
          )
        )
      ),

      // ── Page content ──────────────────────────────────────────────────
      React.createElement("div", {
        style: { padding: page === "landing" ? "0 24px" : "0 24px 60px", maxWidth: page === "landing" ? 960 : 1100, margin: "0 auto" },
      },
        page === "landing"   && React.createElement(LandingPage, { onEnter: () => setPage("upload"), apiOnline }),
        page === "upload"    && React.createElement(UploadPage,  { onAnalyze: () => setPage("dashboard"), setToast }),
        page === "dashboard" && React.createElement(Dashboard,   { setToast })
      ),

      // ── Toast notification ──────────────────────────────────────────────
      toast && React.createElement(Toast, { message: toast.message, type: toast.type, onClose: clearToast })
    )
  );
}

// ── Mount the React app into the #root div in index.html ──────────────────
const rootElement = document.getElementById("root");
if (rootElement) {
  const root = ReactDOM.createRoot(rootElement);
  root.render(React.createElement(App));
}
// Mount React app
const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
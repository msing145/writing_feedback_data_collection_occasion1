// Change this if your backend runs elsewhere
const API_BASE = "http://localhost:8000";

export async function saveDemographics(payload) {
  const res = await fetch(`${API_BASE}/api/demographics`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const detail = await res.json().catch(()=>({}));
    throw new Error(Array.isArray(detail?.detail) ? detail.detail.join("\n") : (detail?.detail || res.statusText));
  }
  return res.json();
}

export async function startSession(asurite) {
  const res = await fetch(`${API_BASE}/api/writing-session/start`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ asurite })
  });
  if (!res.ok) {
    const detail = await res.json().catch(()=>({}));
    throw new Error(detail?.detail || res.statusText);
  }
  return res.json();
}

export async function submitEssay(sessionId, essayText) {
  const res = await fetch(`${API_BASE}/api/essay/submit`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ session_id: sessionId, essay_text: essayText })
  });
  if (!res.ok) {
    const detail = await res.json().catch(()=>({}));
    throw new Error(detail?.detail || res.statusText);
  }
  return res.json();
}

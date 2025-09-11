// frontend/js/app.js
// Finalized app script (ES module) after latest tweaks

import { saveDemographics, startSession, submitEssay } from "./api.js";

/* ----------------------------- State & Screens ---------------------------- */

const screens = {
  info: document.getElementById("screen-info"),
  demo: document.getElementById("screen-demographics"),
  instructions: document.getElementById("screen-instructions"),
  write: document.getElementById("screen-writing"),
  thanks: document.getElementById("screen-thanks"),
};

const state = {
  asurite: null,
  demographics: null,
  sessionId: null,         // set once writing session starts
  hasAgreed: false,        // pressed "I Agree" on instructions (pre-start)
  clientWriteStart: null,  // ms since epoch when user is shown the writing page
};

function show(screen) {
  Object.values(screens).forEach(s => s?.classList.remove("active"));
  screen?.classList.add("active");

  // Hide the big header on all pages except Consent
  const header = document.querySelector(".site-header");
  if (header) header.style.display = (screen === screens.info ? "block" : "none");

  // When navigating to writing page, mark client start time & bind guards
  if (screen === screens.write) {
    if (!state.clientWriteStart) state.clientWriteStart = Date.now();
    bindWriteTextareaGuards();
  }
}

/* -------------------------------- Consent -------------------------------- */

const agreeBtn = document.getElementById("agree");
const nextBtn = document.getElementById("next");
const thanksCard = document.getElementById("thanks");

agreeBtn?.addEventListener("click", () => {
  if (thanksCard) thanksCard.style.display = "block";
  agreeBtn.disabled = true;
});

nextBtn?.addEventListener("click", () => {
  show(screens.demo);
});

/* -------------------------------- Helpers -------------------------------- */

function getRadioValue(name) {
  const input = document.querySelector(`input[name="${name}"]:checked`);
  return input ? input.value : "";
}

function getCheckedValues(name) {
  return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map(i => i.value);
}

function ensureConditionalVisibility() {
  // Show/hide "Other (please specify)" for Race
  const otherChecked = getCheckedValues("Race_List").includes("Other (please specify)");
  const otherSpecify = document.querySelector('input[name="Race_Other_Specify"]');
  if (otherSpecify) {
    if (otherChecked) otherSpecify.classList.remove("hidden");
    else { otherSpecify.classList.add("hidden"); otherSpecify.value = ""; }
  }

  // Non-English group visibility
  const lbVal = getRadioValue("Language_Background");
  const nonEnglish = document.getElementById("nonEnglishGroup");
  if (nonEnglish) {
    if (lbVal === "I grew up speaking language(s) other than English") {
      nonEnglish.classList.remove("hidden");
    } else {
      nonEnglish.classList.add("hidden");
      nonEnglish.querySelectorAll("input").forEach(i => (i.value = ""));
    }
  }
}

// Disable copy/paste/cut/drag/drop in the essay textarea
function bindWriteTextareaGuards() {
  const textarea = document.getElementById("essayText");
  if (!textarea || textarea.dataset.guarded === "1") return;
  textarea.dataset.guarded = "1";

  ["paste", "copy", "cut", "dragstart", "drop", "dragover", "contextmenu"].forEach(evt =>
    textarea.addEventListener(evt, e => e.preventDefault())
  );

  textarea.addEventListener("keydown", e => {
    const k = e.key.toLowerCase();
    if ((e.ctrlKey || e.metaKey) && (k === "c" || k === "v" || k === "x")) {
      e.preventDefault();
    }
  });
}

// Bind visibility handlers (radios + checkboxes)
document.querySelectorAll('.radio-group input[type="radio"], .radio-group input[type="checkbox"]').forEach(el => {
  el.addEventListener("change", ensureConditionalVisibility);
});

/* -------------------------- Populate Age (18–100) ------------------------- */

const ageSelect = document.getElementById("ageSelect");
if (ageSelect) {
  for (let age = 18; age <= 100; age++) {
    const opt = document.createElement("option");
    opt.value = String(age);
    opt.textContent = String(age);
    ageSelect.appendChild(opt);
  }
}

/* --------------------------- Demographics Submit -------------------------- */

const demoForm = document.getElementById("demographicsForm");
demoForm?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const formData = new FormData(demoForm);
  const asuEmail = (formData.get("ASU_Email") || "").toString().trim().toLowerCase();
  const asurite = asuEmail.includes("@") ? asuEmail.split("@")[0] : asuEmail;

  const hispanic = getRadioValue("Hispanic_Origin");
  const races = getCheckedValues("Race_List");
  const raceOther = (formData.get("Race_Other_Specify") || "").toString().trim();
  const packedRace = `Hispanic_Origin=${hispanic}; Race=${races.join(", ")}`;

  const payload = {
    program_use_only: false,           // consent handled in UI
    ASURite: asurite,
    Gender: getRadioValue("Gender"),
    Age: (formData.get("Age") || "").toString().trim(),
    Race_Ethnicity: packedRace,
    Race_Ethnicity_Specify: raceOther,
    Major: "",
    Major_Category: "",
    Major_Category_Specify: "",
    Language_Background: getRadioValue("Language_Background"),
    Native_Language: (formData.get("Native_Language") || "").toString().trim(),
    Years_Studied_English: (formData.get("Years_Studied_English") || "").toString().trim(),
    Years_in_US: (formData.get("Years_in_US") || "").toString().trim(),
  };

  const submitBtn = demoForm.querySelector('button[type="submit"]');
  if (submitBtn) submitBtn.disabled = true;

  try {
    const result = await saveDemographics(payload);
    state.asurite = result.asurite;
    state.demographics = payload;

    // Go to Instructions (do NOT start session yet)
    state.hasAgreed = false;
    state.clientWriteStart = null;
    show(screens.instructions);
    setInstructionsMode();
  } catch (err) {
    alert(err.message || "Failed to save demographics.");
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
});

/* -------------------------- Instructions Page UX -------------------------- */

const instrAgreeBar = document.getElementById("instrAgreeBar");
const instrStartBar = document.getElementById("instrStartBar");
const instrBackBar  = document.getElementById("instrBackBar");
const btnInstrAgree = document.getElementById("btnInstrAgree");
const btnInstrStart = document.getElementById("btnInstrStart");
const btnBackToWriting = document.getElementById("btnBackToWriting");

function setInstructionsMode() {
  if (!screens.instructions?.classList.contains("active")) return;

  // Center the title (CSS can also handle this; here as safeguard)
  const title = screens.instructions.querySelector("h2");
  if (title) title.style.textAlign = "center";

  if (state.sessionId) {
    // Revisiting after writing started: only show "Back To Writing →"
    if (instrAgreeBar) instrAgreeBar.style.display = "none";
    if (instrStartBar) instrStartBar.style.display = "none";
    if (instrBackBar)  instrBackBar.style.display  = "flex";
  } else {
    // Before writing has started
    if (instrBackBar)  instrBackBar.style.display  = "none";
    if (instrAgreeBar) instrAgreeBar.style.display = state.hasAgreed ? "none" : "flex";
    if (instrStartBar) instrStartBar.style.display = state.hasAgreed ? "flex" : "none";
  }
}

// Phase 1: "I Agree" -> reveal "Start Writing"
btnInstrAgree?.addEventListener("click", () => {
  state.hasAgreed = true;
  setInstructionsMode();
});

// Phase 2: "Start Writing" -> start session (if needed), go to Writing
btnInstrStart?.addEventListener("click", async () => {
  if (!state.asurite) {
    alert("Missing participant info. Please complete the demographic survey first.");
    return;
  }
  btnInstrStart.disabled = true;
  try {
    if (!state.sessionId) {
      const session = await startSession(state.asurite);
      state.sessionId = session.session_id;
    }
    show(screens.write); // clientWriteStart is set inside show()
  } catch (err) {
    alert(err.message || "Failed to start writing session.");
  } finally {
    btnInstrStart.disabled = false;
  }
});

// When revisiting Instructions from Writing
btnBackToWriting?.addEventListener("click", () => {
  show(screens.write); // textarea content remains; clientWriteStart not touched
});

/* ------------------------------ Writing Page ------------------------------ */

const btnBackToInstructions = document.getElementById("btnBackToInstructions");
const btnSubmitEssay = document.getElementById("btnSubmitEssay");

btnBackToInstructions?.addEventListener("click", () => {
  show(screens.instructions);
  setInstructionsMode(); // shows only "Back To Writing →" if session started
});

btnSubmitEssay?.addEventListener("click", async () => {
  const textarea = document.getElementById("essayText");
  const text = (textarea?.value || "").trim();
  if (!text && !confirm("Your essay text is empty. Submit anyway?")) return;
  if (!state.sessionId) {
    alert("Missing writing session. Please start writing from the instructions page.");
    return;
  }
  btnSubmitEssay.disabled = true;
  try {
    // Send client start time to backend to compute precise duration
    await submitEssay(
      state.sessionId,
      text,
      state.clientWriteStart ? new Date(state.clientWriteStart).toISOString() : null
    );
    show(screens.thanks);
  } catch (err) {
    alert(err.message || "Failed to submit essay.");
  } finally {
    btnSubmitEssay.disabled = false;
  }
});

/* --------------------------------- Init ---------------------------------- */

ensureConditionalVisibility();
setInstructionsMode();
bindWriteTextareaGuards();

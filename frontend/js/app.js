import { saveDemographics, startSession, submitEssay } from "./api.js";

const screens = {
  info: document.getElementById("screen-info"),
  demo: document.getElementById("screen-demographics"),
  write: document.getElementById("screen-writing"),
  thanks: document.getElementById("screen-thanks"),
};

const state = {
  programUseOnly: false,
  demographics: null,
  asurite: null,
  sessionId: null,
};

function show(screen) {
  Object.values(screens).forEach(s => s.classList.remove("active"));
  screen.classList.add("active");
}

// Step 1
document.getElementById("btnToDemographics").addEventListener("click", () => {
  state.programUseOnly = document.getElementById("programUseOnly").checked;
  show(screens.demo);
});

// Helpers: collect radio group
function getRadioValue(name) {
  const input = document.querySelector(`input[name="${name}"]:checked`);
  return input ? input.value : "";
}

function ensureConditionalVisibility() {
  const reVal = getRadioValue("Race_Ethnicity");
  const reSpecify = document.querySelector('input[name="Race_Ethnicity_Specify"]');
  if (reVal === "Multiple ethnicity / Other (please specify)") {
    reSpecify.classList.remove("hidden");
  } else {
    reSpecify.classList.add("hidden");
    reSpecify.value = "";
  }

  const mcVal = getRadioValue("Major_Category");
  const mcSpecify = document.querySelector('input[name="Major_Category_Specify"]');
  if (mcVal === "Other (Please specify)") {
    mcSpecify.classList.remove("hidden");
  } else {
    mcSpecify.classList.add("hidden");
    mcSpecify.value = "";
  }

  const lbVal = getRadioValue("Language_Background");
  const nonEnglish = document.getElementById("nonEnglishGroup");
  if (lbVal === "I grew up speaking language(s) other than English") {
    nonEnglish.classList.remove("hidden");
  } else {
    nonEnglish.classList.add("hidden");
    nonEnglish.querySelectorAll("input").forEach(i => i.value = "");
  }
}

// Bind visibility handlers
document.querySelectorAll('.radio-group input[type="radio"]').forEach(el => {
  el.addEventListener("change", ensureConditionalVisibility);
});

// Step 2: Demographics submit
const demoForm = document.getElementById("demographicsForm");
demoForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Gather form data
  const formData = new FormData(demoForm);
  const payload = {
    program_use_only: state.programUseOnly,
    ASURite: (formData.get("ASURite") || "").trim(),
    Gender: getRadioValue("Gender"),
    Age: (formData.get("Age") || "").trim(),
    Race_Ethnicity: getRadioValue("Race_Ethnicity"),
    Race_Ethnicity_Specify: (formData.get("Race_Ethnicity_Specify") || "").trim(),
    Major: (formData.get("Major") || "").trim(),
    Major_Category: getRadioValue("Major_Category"),
    Major_Category_Specify: (formData.get("Major_Category_Specify") || "").trim(),
    Language_Background: getRadioValue("Language_Background"),
    Native_Language: (formData.get("Native_Language") || "").trim(),
    Years_Studied_English: (formData.get("Years_Studied_English") || "").trim(),
    Years_in_US: (formData.get("Years_in_US") || "").trim(),
  };

  try {
    const result = await saveDemographics(payload);
    state.asurite = result.asurite;
    state.demographics = payload;

    // Immediately start a server-timed writing session.
    const session = await startSession(state.asurite);
    state.sessionId = session.session_id;

    show(screens.write);
  } catch (err) {
    alert(err.message || "Failed to save demographics.");
  }
});

// Step 3: Submit Essay
document.getElementById("btnSubmitEssay").addEventListener("click", async () => {
  const text = document.getElementById("essayText").value.trim();
  if (!text) {
    if (!confirm("Your essay text is empty. Submit anyway?")) return;
  }
  if (!state.sessionId) {
    alert("Missing writing session. Please go back to the demographics step.");
    return;
  }
  try {
    await submitEssay(state.sessionId, text);
    show(screens.thanks);
  } catch (err) {
    alert(err.message || "Failed to submit essay.");
  }
});

// Initialize
ensureConditionalVisibility();

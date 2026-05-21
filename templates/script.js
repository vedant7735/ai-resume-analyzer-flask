const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadForm = document.getElementById('uploadForm');
const fileInfo = document.getElementById('fileInfo');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const uploadContainer = document.getElementById('uploadContainer');
const dashboardContainer = document.getElementById('dashboardContainer');
const uploadNewBtn = document.getElementById('uploadNewBtn');
const submitBtn = document.getElementById('submitBtn');
const dashboardPdfBtn = document.getElementById('dashboardPdfBtn');

let resumeData = null;

// Click to upload
uploadArea.addEventListener('click', (e) => {
    if (e.target !== fileInput) {
        fileInput.click();
    }
});

// File selected
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        fileInfo.textContent = `Selected: ${files[0].name} (${(files[0].size / 1024).toFixed(2)} KB)`;
    }
});

// Form submission
uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    error.classList.remove('show');
    loading.classList.add('show');
    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loading.classList.remove('show');
        submitBtn.disabled = false;

        if (response.ok && data.success) {
            resumeData = data.data;
            showDashboard(resumeData);
        } else {
            error.textContent = data.error || 'An error occurred';
            error.classList.add('show');
        }

    } catch (err) {
        loading.classList.remove('show');
        submitBtn.disabled = false;
        error.textContent = 'Failed to upload file. Please try again.';
        error.classList.add('show');
    }
});

// Upload new resume
uploadNewBtn.addEventListener('click', () => {
    uploadContainer.style.display = 'flex';
    dashboardContainer.style.display = 'none';
    fileInput.value = '';
    fileInfo.textContent = '';
    resumeData = null;
    dashboardPdfBtn.style.display = 'none';
});

// Show dashboard with data
function showDashboard(data) {
    uploadContainer.style.display = 'none';
    dashboardContainer.style.display = 'block';
    dashboardPdfBtn.style.display = 'none';

    // Populate identity
    document.getElementById('candidateName').textContent = data.identity?.name || 'Unknown Candidate';

    // Populate scores
    const analysis = data.analysis || {};
    const score = analysis.score || {};
    const breakdown = score.breakdown || {};

    document.getElementById('overallScore').textContent = score.overall || '--';
    document.getElementById('scoreExplanation').textContent = score.explanation || '';
    document.getElementById('overallScoreBar').style.width = `${score.overall || 0}%`;

    document.getElementById('contentScore').textContent = breakdown.content_quality || '--';
    document.getElementById('contentBar').style.width = `${breakdown.content_quality || 0}%`;

    document.getElementById('structureScore').textContent = breakdown.structure || '--';
    document.getElementById('structureBar').style.width = `${breakdown.structure || 0}%`;

    document.getElementById('impactScore').textContent = breakdown.impact || '--';
    document.getElementById('impactBar').style.width = `${breakdown.impact || 0}%`;

    document.getElementById('completenessScore').textContent = breakdown.completeness || '--';
    document.getElementById('completenessBar').style.width = `${breakdown.completeness || 0}%`;

    document.getElementById('formattingScore').textContent = breakdown.formatting || '--';
    document.getElementById('formattingBar').style.width = `${breakdown.formatting || 0}%`;

    // Professional summary
    document.getElementById('summaryText').textContent = analysis.professional_summary || 'No summary available.';

    // Strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    (analysis.strengths || []).forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        strengthsList.appendChild(li);
    });

    // Improvements - Accordion Style
    const improvementsList = document.getElementById('improvementsList');
    improvementsList.innerHTML = '';
    (analysis.improvements || []).forEach((improvement, index) => {
        const div = document.createElement('div');
        div.className = 'improvement-item';
        if (index === 0) div.classList.add('active'); // First one open by default

        div.innerHTML = `
        <div class="improvement-header">
            <div class="improvement-header-left">
                <span class="improvement-section">${improvement.section}</span>
                <div class="improvement-issue">${improvement.issue}</div>
            </div>
            <div class="improvement-header-right">
                <span class="priority-badge priority-${improvement.priority.toLowerCase()}">${improvement.priority}</span>
                <div class="accordion-icon">▼</div>
            </div>
        </div>
        <div class="improvement-content">
            <div class="improvement-suggestion">${improvement.suggestion}</div>
        </div>`;

        // Add click handler for accordion
        const header = div.querySelector('.improvement-header');
        header.addEventListener('click', () => {
            div.classList.toggle('active');
        });

        improvementsList.appendChild(div);
    });

    // Recommended roles
    const roleTags = document.getElementById('roleTags');
    roleTags.innerHTML = '';
    (analysis.recommended_for || []).forEach(role => {
        const span = document.createElement('span');
        span.className = 'role-tag';
        span.textContent = role;
        roleTags.appendChild(span);
    });

    // ATS Keywords
    const keywordCloud = document.getElementById('keywordCloud');
    keywordCloud.innerHTML = '';
    (analysis.ats_keywords || []).forEach(keyword => {
        const span = document.createElement('span');
        span.className = 'keyword-tag';
        span.textContent = keyword;
        keywordCloud.appendChild(span);
    });

    // Populate tabs
    populateProjectsTab(data.projects || []);
    populateExperienceTab(data.experience || []);
    populateEducationTab(data.education || []);
    populateSkillsTab(data.skills || {});
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const targetTab = btn.dataset.tab;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`tab-${targetTab}`).classList.add('active');
    });
});

function populateProjectsTab(projects) {
    const container = document.getElementById('tab-projects');
    container.innerHTML = '';

    projects.forEach(project => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const techTags = project.tech_stack.map(tech =>
            `<span class="data-tag">${tech}</span>`
        ).join('');

        const bullets = (project.bullets || []).map(bullet =>
            `<li>${bullet}</li>`
        ).join('');

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${project.title}</div>
                <div class="data-meta">${project.type} • ${project.year}</div>
            </div>
            <div class="data-tags">${techTags}</div>
            <ul class="data-details">${bullets}</ul>
        `;

        container.appendChild(div);
    });
}

function populateExperienceTab(experiences) {
    const container = document.getElementById('tab-experience');
    container.innerHTML = '';

    experiences.forEach(exp => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const bullets = (exp.bullets || []).map(bullet =>
            `<li>${bullet}</li>`
        ).join('');

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${exp.title}</div>
                <div class="data-meta">${exp.company} • ${exp.duration} • ${exp.type}</div>
            </div>
            <ul class="data-details">${bullets}</ul>
        `;

        container.appendChild(div);
    });
}

function populateEducationTab(education) {
    const container = document.getElementById('tab-education');
    container.innerHTML = '';

    education.forEach(edu => {
        const div = document.createElement('div');
        div.className = 'data-item';

        const coursework = edu.relevant_coursework?.map(course =>
            `<span class="data-tag">${course}</span>`
        ).join('') || '';

        div.innerHTML = `
            <div class="data-item-header">
                <div class="data-title">${edu.degree} in ${edu.major}</div>
                <div class="data-meta">${edu.institution} • ${edu.graduation_year} • GPA: ${edu.gpa}</div>
            </div>
            ${coursework ? `<div class="data-tags">${coursework}</div>` : ''}
        `;

        container.appendChild(div);
    });
}

function populateSkillsTab(skills) {
    const container = document.getElementById('tab-skills');
    container.innerHTML = '';

    const categories = [
        { title: 'Languages', data: skills.languages || [] },
        { title: 'Frameworks', data: skills.frameworks || [] },
        { title: 'Tools', data: skills.tools || [] },
        { title: 'Domains', data: skills.domains || [] }
    ];

    categories.forEach(cat => {
        if (cat.data.length > 0) {
            const div = document.createElement('div');
            div.className = 'data-item';

            const tags = cat.data.map(item =>
                `<span class="data-tag">${item}</span>`
            ).join('');

            div.innerHTML = `
                <div class="data-title">${cat.title}</div>
                <div class="data-tags">${tags}</div>
            `;

            container.appendChild(div);
        }
    });
}

// ===== LATEX EDITOR FUNCTIONALITY =====

const downloadLatexBtn = document.getElementById('downloadLatexBtn');
const latexModal = document.getElementById('latexModal');
const closeModal = document.getElementById('closeModal');
const latexEditor = document.getElementById('latexEditor');
const resetBtn = document.getElementById('resetBtn');
const downloadEditedBtn = document.getElementById('downloadEditedBtn');
const editorStatus = document.getElementById('editorStatus');
const lineCount = document.getElementById('lineCount');
const charCount = document.getElementById('charCount');

let originalLatexCode = '';
let currentFileId = null;
let currentDownloadBasename = 'candidate_resume_ai_pack';

// Download LaTeX (generates code and opens editor)
downloadLatexBtn.addEventListener('click', async () => {

    if (!resumeData) return;

    downloadLatexBtn.disabled = true;
    downloadLatexBtn.innerHTML =
        '<span class="btn-text">⏳ GENERATING...</span>';

    editorStatus.textContent = 'Generating LaTeX...';

    try {

        const response = await fetch('/enhance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                resume: resumeData
            })
        });

        const data = await response.json();

        console.log("Enhance Response:", data);

        if (!data.success) {

            alert(
                'Failed to generate LaTeX: ' +
                (data.error || 'Unknown error')
            );

            editorStatus.textContent = 'Generation failed';
            return;
        }

        // Store current file ID globally
        currentFileId = data.file_id;
        currentDownloadBasename =
            data.download_basename || 'candidate_resume_ai_pack';

        // Fetch generated .tex content
        const fileResponse = await fetch(
            `/download-tex/${data.file_id}?download_name=${encodeURIComponent(data.tex_filename || `${currentDownloadBasename}.tex`)}`
        );

        if (!fileResponse.ok) {
            throw new Error('Failed to fetch generated .tex');
        }

        const latexCode = await fileResponse.text();

        // Store original code
        originalLatexCode = latexCode;

        // Populate editor
        latexEditor.value = latexCode;

        // Update stats
        updateEditorStats();

        // Open modal
        latexModal.classList.add('show');

        editorStatus.textContent = 'Ready to edit';

        // -----------------------------
        // PDF BUTTON LOGIC
        // -----------------------------

        if (data.pdf_available === true) {

            console.log("PDF AVAILABLE");

            showPdfDownloadButton(data.file_id);

        } else {

            console.warn("PDF NOT AVAILABLE");

            hidePdfDownloadButton();
        }

    } catch (err) {

        console.error(err);

        alert('Error generating files');

        editorStatus.textContent = 'Error';

    } finally {

        downloadLatexBtn.disabled = false;

        downloadLatexBtn.innerHTML =
            '<span class="btn-text">↓ DOWNLOAD .TEX</span>';
    }
});


// -----------------------------
// DASHBOARD PDF DOWNLOAD
// -----------------------------

dashboardPdfBtn.addEventListener('click', () => {

    if (!currentFileId) {
        console.warn("No currentFileId available");
        return;
    }

    window.location.href =
        `/download-pdf/${currentFileId}?download_name=${encodeURIComponent(`${currentDownloadBasename}.pdf`)}`;
});


// -----------------------------
// SHOW PDF BUTTON
// -----------------------------

function showPdfDownloadButton(fileId) {

    const pdfBtn =
        document.getElementById('dashboardPdfBtn');

    if (!pdfBtn) {
        console.error(
            'dashboardPdfBtn not found'
        );
        return;
    }

    // Ensure global ID stays synced
    currentFileId = fileId;

    // Make visible
    pdfBtn.style.display = 'inline-flex';

    // Remove hidden state if any
    pdfBtn.hidden = false;

    pdfBtn.classList.remove('hidden');

    console.log(
        'PDF button enabled for:',
        fileId
    );
}


// -----------------------------
// HIDE PDF BUTTON
// -----------------------------

function hidePdfDownloadButton() {

    const pdfBtn =
        document.getElementById('dashboardPdfBtn');

    if (!pdfBtn) return;

    pdfBtn.style.display = 'none';
}


// -----------------------------
// CLOSE MODAL
// -----------------------------

closeModal.addEventListener('click', () => {

    latexModal.classList.remove('show');
});


// -----------------------------
// CLOSE ON OVERLAY CLICK
// -----------------------------

latexModal.addEventListener('click', (e) => {

    if (e.target === latexModal) {
        latexModal.classList.remove('show');
    }
});


// -----------------------------
// RESET TO ORIGINAL
// -----------------------------

resetBtn.addEventListener('click', () => {

    if (!confirm(
        'Reset to original generated code?'
    )) {
        return;
    }

    latexEditor.value = originalLatexCode;

    updateEditorStats();

    editorStatus.textContent =
        'Reset to original';
});


// -----------------------------
// DOWNLOAD EDITED TEX
// -----------------------------

downloadEditedBtn.addEventListener('click', () => {

    const editedCode = latexEditor.value;

    const blob = new Blob(
        [editedCode],
        { type: 'text/plain' }
    );

    const url =
        URL.createObjectURL(blob);

    const a =
        document.createElement('a');

    a.href = url;

    a.download =
        `${currentDownloadBasename}_edited.tex`;

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);

    editorStatus.textContent =
        'Downloaded';

    setTimeout(() => {

        editorStatus.textContent =
            'Ready to edit';

    }, 2000);
});


// -----------------------------
// LIVE EDITOR STATS
// -----------------------------

latexEditor.addEventListener('input', () => {

    updateEditorStats();

    editorStatus.textContent = 'Modified';
});


// -----------------------------
// UPDATE STATS
// -----------------------------

function updateEditorStats() {

    const text = latexEditor.value;

    const lines =
        text.split('\n').length;

    const chars =
        text.length;

    lineCount.textContent = lines;

    charCount.textContent = chars;
}


// -----------------------------
// ESCAPE KEY CLOSE
// -----------------------------

document.addEventListener('keydown', (e) => {

    if (
        e.key === 'Escape' &&
        latexModal.classList.contains('show')
    ) {
        latexModal.classList.remove('show');
    }
});

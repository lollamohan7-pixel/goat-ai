/**
 * GOAT AI — Frontend Controller & Dynamic UI Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const dropzone = document.getElementById('dropzone');
  const resumeFileInput = document.getElementById('resumeFile');
  const selectedFileCard = document.getElementById('selectedFileCard');
  const fileNameDisplay = document.getElementById('fileName');
  const fileSizeDisplay = document.getElementById('fileSize');
  const removeFileBtn = document.getElementById('removeFileBtn');

  const tabUpload = document.getElementById('tabUpload');
  const tabText = document.getElementById('tabText');
  const uploadContainer = document.getElementById('uploadContainer');
  const textContainer = document.getElementById('textContainer');
  const resumeTextInput = document.getElementById('resumeText');

  const jobDescInput = document.getElementById('jobDescription');
  const targetRoleSelect = document.getElementById('targetRole');
  const analyzeBtn = document.getElementById('analyzeBtn');
  const loadingOverlay = document.getElementById('loadingOverlay');

  // Results Elements
  const resultsSection = document.getElementById('resultsSection');
  const scoreNumber = document.getElementById('scoreNumber');
  const scoreCircle = document.getElementById('scoreCircle');
  const statusBadge = document.getElementById('statusBadge');
  const matchedCountEl = document.getElementById('matchedCount');
  const missingCountEl = document.getElementById('missingCount');
  const totalRequiredEl = document.getElementById('totalRequired');
  const scoreExplanation = document.getElementById('scoreExplanation');
  const matchedSkillsList = document.getElementById('matchedSkillsList');
  const missingSkillsList = document.getElementById('missingSkillsList');
  const roadmapLevelsGrid = document.getElementById('roadmapLevelsGrid');
  const suggestionsContainer = document.getElementById('suggestionsContainer');
  const downloadReportBtn = document.getElementById('downloadReportBtn');

  // History Modal Elements
  const historyModal = document.getElementById('historyModal');
  const openHistoryBtn = document.getElementById('openHistoryBtn');
  const closeHistoryBtn = document.getElementById('closeHistoryBtn');
  const historyListContainer = document.getElementById('historyListContainer');

  let activeMode = 'file'; // 'file' or 'text'
  let currentAnalysisId = null;

  // Preset Sample Jobs for 1-Click Testing
  const SAMPLES = {
    swe: `Looking for a Software Engineer with strong experience in Python, Flask, REST APIs, SQL, PostgreSQL, Git, Docker, and frontend basics (JavaScript, HTML, CSS). Experience with AWS or Azure cloud services, unit testing (pytest), and CI/CD pipelines is a strong plus. Requirements: 2+ years of programming experience, strong problem solving and data structures knowledge.`,
    data: `Seeking a Junior Data Analyst proficient in SQL, Python (Pandas, NumPy), Excel, and data visualization tools like Power BI or Tableau. Must be familiar with data cleaning, statistical analysis, and basic machine learning principles. Strong written and verbal communication skills required.`,
    devops: `Senior DevOps Engineer required. Mandatory skills: Docker, Kubernetes, Terraform, Linux system administration, AWS, CI/CD with GitHub Actions or GitLab, Python or Bash scripting, and Prometheus monitoring.`
  };

  // Sample Resumes for 1-Click Testing
  const SAMPLE_RESUMES = {
    high: `Software Developer with 2 years experience building web applications.
Technical Skills: Python, Flask, Django, PostgreSQL, SQL, JavaScript, HTML, CSS, Git, Docker, REST APIs, Unit Testing, AWS basics.
Projects: Built an e-commerce backend with Flask and PostgreSQL; implemented Docker containers and automated GitHub Actions pipeline.`,
    low: `Entry level applicant passionate about technology.
Skills: Java, HTML, CSS, Microsoft Word, Communication, Teamwork.
Projects: Simple personal portfolio page hosted on GitHub Pages.`
  };

  // Quick Sample Job Buttons
  document.querySelectorAll('.sample-job-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const role = btn.getAttribute('data-role');
      if (SAMPLES[role]) {
        jobDescInput.value = SAMPLES[role];
        jobDescInput.dispatchEvent(new Event('input'));
      }
    });
  });

  // Quick Sample Resume Buttons
  document.querySelectorAll('.sample-resume-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tier = btn.getAttribute('data-tier');
      switchTab('text');
      if (SAMPLE_RESUMES[tier]) {
        resumeTextInput.value = SAMPLE_RESUMES[tier];
        resumeTextInput.dispatchEvent(new Event('input'));
      }
    });
  });

  // Tab Switching
  function switchTab(mode) {
    activeMode = mode;
    if (mode === 'file') {
      tabUpload.classList.add('active');
      tabText.classList.remove('active');
      uploadContainer.style.display = 'block';
      textContainer.style.display = 'none';
    } else {
      tabText.classList.add('active');
      tabUpload.classList.remove('active');
      uploadContainer.style.display = 'none';
      textContainer.style.display = 'block';
    }
  }

  tabUpload?.addEventListener('click', () => switchTab('file'));
  tabText?.addEventListener('click', () => switchTab('text'));

  // Bridge: Auto-load resume if forwarded from Resume Builder studio
  try {
    const builderResumeText = sessionStorage.getItem('goat_builder_resume_text');
    if (builderResumeText) {
      sessionStorage.removeItem('goat_builder_resume_text');
      switchTab('text');
      if (resumeTextInput) {
        resumeTextInput.value = builderResumeText;
        resumeTextInput.dispatchEvent(new Event('input'));
      }
      setTimeout(() => {
        const analyzerEl = document.getElementById('analyzer');
        if (analyzerEl) {
          analyzerEl.scrollIntoView({ behavior: 'smooth' });
        }
      }, 150);
    }
  } catch (_) {}

  // File Upload & Drag-and-Drop Handling
  ['dragenter', 'dragover'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    dropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  resumeFileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    const validExtensions = ['.pdf', '.docx'];
    const fileName = file.name.toLowerCase();
    const isValidType = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValidType) {
      alert('Please upload a valid PDF (.pdf) or Word document (.docx).');
      resumeFileInput.value = '';
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File size exceeds the 5MB limit. Please upload a smaller resume.');
      resumeFileInput.value = '';
      return;
    }

    fileNameDisplay.textContent = file.name;
    fileSizeDisplay.textContent = formatBytes(file.size);
    selectedFileCard.style.display = 'flex';
    dropzone.style.display = 'none';
  }

  removeFileBtn?.addEventListener('click', () => {
    resumeFileInput.value = '';
    selectedFileCard.style.display = 'none';
    dropzone.style.display = 'block';
  });

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  }

  // Submit Analysis Request
  analyzeBtn.addEventListener('click', async (e) => {
    e.preventDefault();

    const jobDescription = jobDescInput.value.trim();
    if (!jobDescription) {
      alert('Please paste or select a job description before analyzing.');
      jobDescInput.focus();
      return;
    }

    const formData = new FormData();
    formData.append('job_description', jobDescription);
    formData.append('target_role', targetRoleSelect.value);

    if (activeMode === 'file') {
      const file = resumeFileInput.files[0];
      if (!file) {
        alert('Please upload your resume file (PDF or DOCX) or switch to Paste Text mode.');
        return;
      }
      formData.append('resume_file', file);
    } else {
      const text = resumeTextInput.value.trim();
      if (!text) {
        alert('Please paste your resume content in the text box.');
        resumeTextInput.focus();
        return;
      }
      formData.append('resume_text', text);
    }

    // Show Loading Animation
    loadingOverlay.style.display = 'flex';
    analyzeBtn.disabled = true;

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to analyze resume. Please try again.');
      }

      displayResults(data);
    } catch (err) {
      console.error(err);
      alert('Error: ' + err.message);
    } finally {
      loadingOverlay.style.display = 'none';
      analyzeBtn.disabled = false;
    }
  });

  // Display Analysis Results
  function displayResults(data) {
    currentAnalysisId = data.analysis_id || null;

    const score = Math.round(data.overall_match_score || 0);
    const isVerified = score >= 85;

    // Animate Score Counter
    animateScoreCounter(score);

    // Animate Circular Progress Meter
    const circumference = 2 * Math.PI * 80; // r = 80
    const offset = circumference - (score / 100) * circumference;
    scoreCircle.style.strokeDashoffset = offset;

    // Status Badge
    statusBadge.className = 'status-badge ' + (isVerified ? 'verified' : 'not-verified');
    statusBadge.innerHTML = isVerified
      ? '✓ Verified — Score Threshold Met'
      : '⚠️ Not Verified — Below 85%';

    // Metric Summary Counters
    matchedCountEl.textContent = data.matched_skills ? data.matched_skills.length : 0;
    missingCountEl.textContent = data.missing_skills ? data.missing_skills.length : 0;
    totalRequiredEl.textContent = data.total_job_skills || (data.matched_skills.length + data.missing_skills.length);

    // Score Explanation
    scoreExplanation.textContent = data.score_explanation || 
      `Your resume matches ${score}% of the core skills and keywords required by this job description.`;

    // Render Skills Clouds
    renderSkillsCloud(matchedSkillsList, data.matched_skills || [], 'matched', '✓ ');
    renderSkillsCloud(missingSkillsList, data.missing_skills || [], 'missing', '+ ');

    // Render Learning Roadmap
    renderRoadmap(data.roadmap || {});

    // Render Resume Bullet Suggestions
    renderSuggestions(data.suggestions || []);

    // Reveal and scroll smoothly
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function animateScoreCounter(target) {
    let current = 0;
    const duration = 1200;
    const stepTime = 16;
    const totalSteps = duration / stepTime;
    const increment = target / totalSteps;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      scoreNumber.textContent = Math.round(current) + '%';
    }, stepTime);
  }

  function renderSkillsCloud(container, skills, typeClass, prefix = '') {
    container.innerHTML = '';
    if (!skills || skills.length === 0) {
      container.innerHTML = `<span class="empty-state-notice">None detected</span>`;
      return;
    }

    skills.forEach(skill => {
      const tag = document.createElement('span');
      tag.className = `skill-tag ${typeClass}`;
      tag.textContent = `${prefix}${skill}`;
      container.appendChild(tag);
    });
  }

  function renderRoadmap(roadmap) {
    roadmapLevelsGrid.innerHTML = '';
    const tiers = [
      { key: 'beginner', label: '1. Fundamentals', badgeClass: 'level-beginner' },
      { key: 'intermediate', label: '2. Core Projects', badgeClass: 'level-intermediate' },
      { key: 'advanced', label: '3. Advanced Mastery', badgeClass: 'level-advanced' }
    ];

    tiers.forEach(tier => {
      const items = roadmap[tier.key] || [];
      const card = document.createElement('div');
      card.className = 'roadmap-level-card';

      let itemsHtml = items.length > 0
        ? items.map(item => `<li>${escapeHtml(item)}</li>`).join('')
        : `<li>No specific gap identified at this level. Practice core portfolio projects.</li>`;

      card.innerHTML = `
        <div class="roadmap-card-header">
          <h4 style="font-size: 1.05rem;">${tier.label}</h4>
          <span class="level-badge ${tier.badgeClass}">${tier.key}</span>
        </div>
        <ul class="roadmap-list">${itemsHtml}</ul>
      `;
      roadmapLevelsGrid.appendChild(card);
    });
  }

  function renderSuggestions(suggestions) {
    suggestionsContainer.innerHTML = '';
    if (!suggestions || suggestions.length === 0) {
      suggestionsContainer.innerHTML = `
        <div class="suggestion-card">
          <p style="color: var(--text-secondary); font-size: 0.9rem;">
            Great job! Your current experience points clearly articulate your technical stack. Keep quantifying your achievements with metrics.
          </p>
        </div>`;
      return;
    }

    suggestions.forEach(s => {
      const card = document.createElement('div');
      card.className = 'suggestion-card';
      card.innerHTML = `
        <h5 style="color: #38bdf8; font-size: 0.92rem; margin-bottom: 6px;">Focus Area: ${escapeHtml(s.topic || 'Resume Bullet Point')}</h5>
        <div class="suggestion-before-after">
          <div class="sub-box sub-box-before">
            <span class="sub-box-lbl">Original / Vague phrasing</span>
            "${escapeHtml(s.original || 'Assisted in building website and fixed bugs.')}"
          </div>
          <div class="sub-box sub-box-after">
            <span class="sub-box-lbl">Recommended / Impact phrasing</span>
            "${escapeHtml(s.recommended || 'Engineered responsive full-stack features using Flask and PostgreSQL, reducing latency by 20%.')}"
          </div>
        </div>
        <p style="font-size: 0.78rem; color: var(--text-muted); margin-top: 8px;">
          💡 <em>${escapeHtml(s.reason || 'Quantifying metrics and specifying technologies provides clear evidence of skill competency.')}</em>
        </p>
      `;
      suggestionsContainer.appendChild(card);
    });
  }

  // Download PDF Report
  downloadReportBtn?.addEventListener('click', () => {
    if (currentAnalysisId) {
      window.location.href = `/api/download-report/${currentAnalysisId}`;
    } else {
      window.print();
    }
  });

  // History Modal Logic
  openHistoryBtn?.addEventListener('click', async (e) => {
    e.preventDefault();
    historyModal.style.display = 'flex';
    historyListContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">Loading history records...</p>';

    try {
      const res = await fetch('/api/history');
      const data = await res.json();

      if (!data.history || data.history.length === 0) {
        historyListContainer.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 20px;">No previous analysis records found. Run your first analysis above!</p>';
        return;
      }

      historyListContainer.innerHTML = data.history.map(item => `
        <div class="history-item">
          <div>
            <strong style="color: #f8fafc; font-size: 0.95rem;">${escapeHtml(item.target_role || 'General Role')}</strong>
            <p style="color: var(--text-muted); font-size: 0.78rem; margin-top: 2px;">
              ${new Date(item.created_at).toLocaleString()} • ${item.source_type || 'Resume'}
            </p>
          </div>
          <div style="display: flex; align-items: center; gap: 12px;">
            <span class="status-badge ${item.match_score >= 85 ? 'verified' : 'not-verified'}" style="padding: 4px 10px; font-size: 0.75rem;">
              ${Math.round(item.match_score)}%
            </span>
            <a href="/api/download-report/${item.id}" class="btn-nav-action" style="padding: 6px 12px; font-size: 0.78rem;" title="Download PDF">
              PDF 📥
            </a>
          </div>
        </div>
      `).join('');
    } catch (err) {
      historyListContainer.innerHTML = '<p style="color: #f87171; text-align: center; padding: 20px;">Failed to load history records.</p>';
    }
  });

  closeHistoryBtn?.addEventListener('click', () => {
    historyModal.style.display = 'none';
  });

  window.addEventListener('click', (e) => {
    if (e.target === historyModal) {
      historyModal.style.display = 'none';
    }
  });

  function escapeHtml(text) {
    if (!text) return '';
    return text.toString()
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});

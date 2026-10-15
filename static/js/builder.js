/**
 * GOAT AI — Professional Resume Builder Controller
 * Manages guided multi-section form state, dynamic additions/removals,
 * real-time safe DOM live preview rendering, template style switching,
 * and ReportLab PDF download integration.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Current state
  let currentTemplate = 'modern'; // 'modern' or 'classic'
  let entryCounter = 0;

  // DOM Form Controls
  const fullNameInput = document.getElementById('fullName');
  const headlineInput = document.getElementById('headline');
  const emailInput = document.getElementById('email');
  const phoneInput = document.getElementById('phone');
  const locationInput = document.getElementById('location');
  const linkedinInput = document.getElementById('linkedin');
  const githubInput = document.getElementById('github');
  const portfolioInput = document.getElementById('portfolio');
  const summaryInput = document.getElementById('summary');

  const skillsLanguagesInput = document.getElementById('skillsLanguages');
  const skillsFrameworksInput = document.getElementById('skillsFrameworks');
  const skillsToolsInput = document.getElementById('skillsTools');
  const skillsDatabasesInput = document.getElementById('skillsDatabases');

  const achievementsInput = document.getElementById('achievements');

  // Containers
  const experienceContainer = document.getElementById('experienceListContainer');
  const educationContainer = document.getElementById('educationListContainer');
  const projectsContainer = document.getElementById('projectsListContainer');
  const certificationsContainer = document.getElementById('certificationsListContainer');
  const languagesContainer = document.getElementById('languagesListContainer');

  // Action Buttons
  const addExperienceBtn = document.getElementById('addExperienceBtn');
  const addEducationBtn = document.getElementById('addEducationBtn');
  const addProjectBtn = document.getElementById('addProjectBtn');
  const addCertificationBtn = document.getElementById('addCertificationBtn');
  const addLanguageBtn = document.getElementById('addLanguageBtn');

  const templateModernBtn = document.getElementById('templateModernBtn');
  const templateClassicBtn = document.getElementById('templateClassicBtn');
  const prefillSampleBtn = document.getElementById('prefillSampleBtn');
  const analyzeMatchBtn = document.getElementById('analyzeMatchBtn');
  const resetFormBtn = document.getElementById('resetFormBtn');
  const downloadPdfBtn = document.getElementById('downloadPdfBtn');
  const alertBanner = document.getElementById('builderAlertBanner');

  // Preview Elements
  const resumePaperSheet = document.getElementById('resumePaperSheet');
  const previewLayoutIndicator = document.getElementById('previewLayoutIndicator');
  const rpName = document.getElementById('rpName');
  const rpHeadline = document.getElementById('rpHeadline');
  const rpContact = document.getElementById('rpContact');

  const rpSectionSummary = document.getElementById('rpSectionSummary');
  const rpSummary = document.getElementById('rpSummary');

  const rpSectionSkills = document.getElementById('rpSectionSkills');
  const rpSkills = document.getElementById('rpSkills');

  const rpSectionExperience = document.getElementById('rpSectionExperience');
  const rpExpHeading = document.getElementById('rpExpHeading');
  const rpExperience = document.getElementById('rpExperience');

  const rpSectionProjects = document.getElementById('rpSectionProjects');
  const rpProjects = document.getElementById('rpProjects');

  const rpSectionEducation = document.getElementById('rpSectionEducation');
  const rpEducation = document.getElementById('rpEducation');

  const rpSectionCertifications = document.getElementById('rpSectionCertifications');
  const rpCertifications = document.getElementById('rpCertifications');

  const rpSectionAchievements = document.getElementById('rpSectionAchievements');
  const rpAchievements = document.getElementById('rpAchievements');

  const rpSectionLanguages = document.getElementById('rpSectionLanguages');
  const rpLanguages = document.getElementById('rpLanguages');

  // Mobile Tabs
  const tabBtnEditor = document.getElementById('tabBtnEditor');
  const tabBtnPreview = document.getElementById('tabBtnPreview');
  const builderFormPane = document.getElementById('builderFormPane');
  const builderPreviewPane = document.getElementById('builderPreviewPane');

  // Sample data payload for 1-click test pre-filling
  const SAMPLE_DATA = {
    fullName: "Jordan Hayes",
    headline: "Lead Full Stack Software Engineer",
    email: "jordan.hayes@example.com",
    phone: "+1 (555) 349-2819",
    location: "San Francisco, CA",
    linkedin: "linkedin.com/in/jordanhayes",
    github: "github.com/jordanhayes",
    portfolio: "jordanhayes.dev",
    summary: "Full Stack Engineer with 6+ years of experience designing high-throughput distributed systems and responsive user interfaces. Proven track record in microservice scalability and automated CI/CD pipelines.",
    skillsLanguages: "Python, TypeScript, Go, SQL, Bash",
    skillsFrameworks: "Flask, FastAPI, React, Node.js, Next.js",
    skillsTools: "Docker, Kubernetes, AWS, Terraform, Git, CI/CD",
    skillsDatabases: "PostgreSQL, Redis, DynamoDB, MongoDB",
    experience: [
      {
        role: "Senior Software Engineer",
        company: "Apex Cloud Systems",
        location: "San Francisco, CA",
        startDate: "2022-04",
        endDate: "Present",
        current: true,
        bullets: "Spearheaded redesign of the billing microservice, handling 15M daily transactions with 99.99% uptime.\nReduced p95 API response latency by 38% via PostgreSQL connection pooling and Redis caching.\nMentored 4 junior software engineers in clean code design and automated testing."
      },
      {
        role: "Software Engineer",
        company: "DataVibe Analytics",
        location: "Austin, TX",
        startDate: "2019-06",
        endDate: "2022-03",
        current: false,
        bullets: "Built full-stack analytics dashboards with React and Flask.\nAutomated integration testing and container builds using GitHub Actions."
      }
    ],
    education: [
      {
        degree: "B.S. in Computer Science",
        school: "University of Texas at Austin",
        location: "Austin, TX",
        gradYear: "2019",
        gpa: "3.88 / 4.0",
        honors: "Magna Cum Laude"
      }
    ],
    projects: [
      {
        title: "GOAT AI Resume Matcher",
        technologies: "Python, Flask, PyMuPDF, scikit-learn",
        link: "github.com/jordanhayes/goat-ai",
        bullets: "Engineered transparent NLP skill extraction and contextual similarity scoring.\nIntegrated ReportLab for instantaneous PDF report generation."
      }
    ],
    certifications: [
      {
        name: "AWS Certified Solutions Architect – Associate",
        issuer: "Amazon Web Services",
        date: "2023",
        id: "AWS-829103"
      }
    ],
    achievements: "Winner — Austin Cloud Hackathon 2021 (Top 1% out of 250 teams)\nSpeaker at PyTexas 2023 on Microservices Optimization",
    languages: [
      { name: "English", proficiency: "Native" },
      { name: "Spanish", proficiency: "Professional Working" }
    ]
  };

  // Safe DOM Helper: creates element and assigns textContent safely
  function createSafeEl(tag, text = '', className = '') {
    const el = document.createElement(tag);
    if (text) el.textContent = text;
    if (className) el.className = className;
    return el;
  }

  // Notice Banner Helper
  function showNotification(msg, type = 'error') {
    if (!alertBanner) return;
    alertBanner.textContent = msg;
    alertBanner.className = `builder-alert-banner ${type}`;
    alertBanner.style.display = 'block';
    if (type === 'success') {
      setTimeout(() => {
        alertBanner.style.display = 'none';
      }, 4000);
    }
  }

  function hideNotification() {
    if (alertBanner) alertBanner.style.display = 'none';
  }

  // --------------------------------------------------------------------------
  // Dynamic Item Card Generators
  // --------------------------------------------------------------------------

  function addExperienceEntry(data = {}) {
    entryCounter++;
    const cardId = `exp-item-${entryCounter}`;
    const card = document.createElement('div');
    card.className = 'dynamic-entry-card';
    card.id = cardId;

    card.innerHTML = `
      <div class="entry-card-header">
        <span class="entry-card-title">Experience Item</span>
        <button type="button" class="btn-remove-entry" title="Remove Experience">✕ Remove</button>
      </div>
      <div class="form-grid-2col">
        <div class="form-field-group">
          <label class="form-label required-label">Job Title / Role</label>
          <input type="text" class="form-input exp-role" placeholder="e.g. Senior Software Engineer" required>
        </div>
        <div class="form-field-group">
          <label class="form-label required-label">Company / Organization</label>
          <input type="text" class="form-input exp-company" placeholder="e.g. Apex Cloud Systems" required>
        </div>
      </div>
      <div class="form-grid-3col">
        <div class="form-field-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input exp-location" placeholder="e.g. San Francisco, CA">
        </div>
        <div class="form-field-group">
          <label class="form-label">Start Date</label>
          <input type="text" class="form-input exp-start" placeholder="e.g. 2022-04">
        </div>
        <div class="form-field-group">
          <label class="form-label">End Date</label>
          <input type="text" class="form-input exp-end" placeholder="e.g. Present">
        </div>
      </div>
      <div class="form-field-group" style="margin-top: 8px;">
        <label style="display: inline-flex; align-items: center; gap: 8px; font-size: 0.82rem; color: var(--text-secondary); cursor: pointer;">
          <input type="checkbox" class="exp-current" style="cursor: pointer;">
          I currently work in this role
        </label>
      </div>
      <div class="form-field-group" style="margin-top: 8px;">
        <label class="form-label">Responsibilities & Key Achievements (one bullet per line)</label>
        <textarea class="form-textarea exp-bullets" rows="3" placeholder="Engineered high-throughput REST APIs...&#10;Decreased query response time by 40%..."></textarea>
      </div>
    `;

    // Populate data if provided
    if (data.role) card.querySelector('.exp-role').value = data.role;
    if (data.company) card.querySelector('.exp-company').value = data.company;
    if (data.location) card.querySelector('.exp-location').value = data.location;
    if (data.startDate) card.querySelector('.exp-start').value = data.startDate;
    if (data.endDate) card.querySelector('.exp-end').value = data.endDate;
    if (data.current) {
      card.querySelector('.exp-current').checked = true;
      card.querySelector('.exp-end').value = 'Present';
      card.querySelector('.exp-end').disabled = true;
    }
    if (data.bullets) card.querySelector('.exp-bullets').value = data.bullets;

    // Events
    card.querySelector('.btn-remove-entry').addEventListener('click', () => {
      card.remove();
      updateLivePreview();
    });

    const currentCheckbox = card.querySelector('.exp-current');
    const endDateInput = card.querySelector('.exp-end');
    currentCheckbox.addEventListener('change', () => {
      if (currentCheckbox.checked) {
        endDateInput.value = 'Present';
        endDateInput.disabled = true;
      } else {
        endDateInput.disabled = false;
        if (endDateInput.value === 'Present') endDateInput.value = '';
      }
      updateLivePreview();
    });

    card.querySelectorAll('input, textarea').forEach(input => {
      input.addEventListener('input', updateLivePreview);
    });

    experienceContainer.appendChild(card);
    updateLivePreview();
  }

  function addEducationEntry(data = {}) {
    entryCounter++;
    const card = document.createElement('div');
    card.className = 'dynamic-entry-card';

    card.innerHTML = `
      <div class="entry-card-header">
        <span class="entry-card-title">Education Item</span>
        <button type="button" class="btn-remove-entry" title="Remove Education">✕ Remove</button>
      </div>
      <div class="form-grid-2col">
        <div class="form-field-group">
          <label class="form-label required-label">Degree / Qualification</label>
          <input type="text" class="form-input edu-degree" placeholder="e.g. B.S. in Computer Science" required>
        </div>
        <div class="form-field-group">
          <label class="form-label required-label">Institution / University</label>
          <input type="text" class="form-input edu-school" placeholder="e.g. University of Texas at Austin" required>
        </div>
      </div>
      <div class="form-grid-4col">
        <div class="form-field-group">
          <label class="form-label">Location</label>
          <input type="text" class="form-input edu-location" placeholder="e.g. Austin, TX">
        </div>
        <div class="form-field-group">
          <label class="form-label">Graduation Year / Dates</label>
          <input type="text" class="form-input edu-year" placeholder="e.g. 2019">
        </div>
        <div class="form-field-group">
          <label class="form-label">GPA / Grade</label>
          <input type="text" class="form-input edu-gpa" placeholder="e.g. 3.88 / 4.0">
        </div>
        <div class="form-field-group">
          <label class="form-label">Honors / Distinctions</label>
          <input type="text" class="form-input edu-honors" placeholder="e.g. Magna Cum Laude">
        </div>
      </div>
    `;

    if (data.degree) card.querySelector('.edu-degree').value = data.degree;
    if (data.school) card.querySelector('.edu-school').value = data.school;
    if (data.location) card.querySelector('.edu-location').value = data.location;
    if (data.gradYear) card.querySelector('.edu-year').value = data.gradYear;
    if (data.gpa) card.querySelector('.edu-gpa').value = data.gpa;
    if (data.honors) card.querySelector('.edu-honors').value = data.honors;

    card.querySelector('.btn-remove-entry').addEventListener('click', () => {
      card.remove();
      updateLivePreview();
    });

    card.querySelectorAll('input').forEach(input => {
      input.addEventListener('input', updateLivePreview);
    });

    educationContainer.appendChild(card);
    updateLivePreview();
  }

  function addProjectEntry(data = {}) {
    entryCounter++;
    const card = document.createElement('div');
    card.className = 'dynamic-entry-card';

    card.innerHTML = `
      <div class="entry-card-header">
        <span class="entry-card-title">Project Item</span>
        <button type="button" class="btn-remove-entry" title="Remove Project">✕ Remove</button>
      </div>
      <div class="form-grid-3col">
        <div class="form-field-group">
          <label class="form-label required-label">Project Name</label>
          <input type="text" class="form-input proj-title" placeholder="e.g. GOAT AI Resume Matcher" required>
        </div>
        <div class="form-field-group">
          <label class="form-label">Technologies Used</label>
          <input type="text" class="form-input proj-tech" placeholder="e.g. Python, Flask, Docker, scikit-learn">
        </div>
        <div class="form-field-group">
          <label class="form-label">Project / Repository Link</label>
          <input type="text" class="form-input proj-link" placeholder="e.g. github.com/username/project">
        </div>
      </div>
      <div class="form-field-group" style="margin-top: 8px;">
        <label class="form-label">Description / Bullet Points (one per line)</label>
        <textarea class="form-textarea proj-bullets" rows="2" placeholder="Engineered NLP matching algorithms with explainable scoring..."></textarea>
      </div>
    `;

    if (data.title) card.querySelector('.proj-title').value = data.title;
    if (data.technologies) card.querySelector('.proj-tech').value = data.technologies;
    if (data.link) card.querySelector('.proj-link').value = data.link;
    if (data.bullets) card.querySelector('.proj-bullets').value = data.bullets;

    card.querySelector('.btn-remove-entry').addEventListener('click', () => {
      card.remove();
      updateLivePreview();
    });

    card.querySelectorAll('input, textarea').forEach(input => {
      input.addEventListener('input', updateLivePreview);
    });

    projectsContainer.appendChild(card);
    updateLivePreview();
  }

  function addCertificationEntry(data = {}) {
    entryCounter++;
    const card = document.createElement('div');
    card.className = 'dynamic-entry-card';

    card.innerHTML = `
      <div class="entry-card-header">
        <span class="entry-card-title">Certification Item</span>
        <button type="button" class="btn-remove-entry" title="Remove Certification">✕ Remove</button>
      </div>
      <div class="form-grid-4col">
        <div class="form-field-group">
          <label class="form-label required-label">Certification Name</label>
          <input type="text" class="form-input cert-name" placeholder="e.g. AWS Solutions Architect" required>
        </div>
        <div class="form-field-group">
          <label class="form-label">Issuing Organization</label>
          <input type="text" class="form-input cert-issuer" placeholder="e.g. Amazon Web Services">
        </div>
        <div class="form-field-group">
          <label class="form-label">Date / Year</label>
          <input type="text" class="form-input cert-date" placeholder="e.g. 2023">
        </div>
        <div class="form-field-group">
          <label class="form-label">Credential ID / URL</label>
          <input type="text" class="form-input cert-id" placeholder="e.g. AWS-829103">
        </div>
      </div>
    `;

    if (data.name) card.querySelector('.cert-name').value = data.name;
    if (data.issuer) card.querySelector('.cert-issuer').value = data.issuer;
    if (data.date) card.querySelector('.cert-date').value = data.date;
    if (data.id) card.querySelector('.cert-id').value = data.id;

    card.querySelector('.btn-remove-entry').addEventListener('click', () => {
      card.remove();
      updateLivePreview();
    });

    card.querySelectorAll('input').forEach(input => {
      input.addEventListener('input', updateLivePreview);
    });

    certificationsContainer.appendChild(card);
    updateLivePreview();
  }

  function addLanguageEntry(data = {}) {
    entryCounter++;
    const card = document.createElement('div');
    card.className = 'dynamic-entry-card';

    card.innerHTML = `
      <div class="entry-card-header">
        <span class="entry-card-title">Language Item</span>
        <button type="button" class="btn-remove-entry" title="Remove Language">✕ Remove</button>
      </div>
      <div class="form-grid-2col">
        <div class="form-field-group">
          <label class="form-label required-label">Language</label>
          <input type="text" class="form-input lang-name" placeholder="e.g. English, French, Spanish" required>
        </div>
        <div class="form-field-group">
          <label class="form-label">Proficiency Level</label>
          <select class="custom-select lang-prof">
            <option value="Native / Bilingual">Native / Bilingual</option>
            <option value="Full Professional">Full Professional</option>
            <option value="Professional Working">Professional Working</option>
            <option value="Conversational">Conversational</option>
            <option value="Elementary">Elementary</option>
          </select>
        </div>
      </div>
    `;

    if (data.name) card.querySelector('.lang-name').value = data.name;
    if (data.proficiency) card.querySelector('.lang-prof').value = data.proficiency;

    card.querySelector('.btn-remove-entry').addEventListener('click', () => {
      card.remove();
      updateLivePreview();
    });

    card.querySelector('.lang-name').addEventListener('input', updateLivePreview);
    card.querySelector('.lang-prof').addEventListener('change', updateLivePreview);

    languagesContainer.appendChild(card);
    updateLivePreview();
  }

  // --------------------------------------------------------------------------
  // Real-Time Safe DOM Live Preview Renderer
  // --------------------------------------------------------------------------

  function updateLivePreview() {
    hideNotification();

    // 1. Header (Name, Headline, Contact)
    const fullName = fullNameInput.value.trim() || 'Your Name';
    rpName.textContent = currentTemplate === 'classic' ? fullName.toUpperCase() : fullName;

    const headline = headlineInput.value.trim();
    if (headline) {
      rpHeadline.textContent = headline;
      rpHeadline.style.display = 'block';
    } else {
      rpHeadline.textContent = '';
      rpHeadline.style.display = 'none';
    }

    // Build Contact Row safely
    const contactParts = [];
    if (emailInput.value.trim()) contactParts.push(emailInput.value.trim());
    if (phoneInput.value.trim()) contactParts.push(phoneInput.value.trim());
    if (locationInput.value.trim()) contactParts.push(locationInput.value.trim());
    if (linkedinInput.value.trim()) contactParts.push(linkedinInput.value.trim());
    if (githubInput.value.trim()) contactParts.push(githubInput.value.trim());
    if (portfolioInput.value.trim()) contactParts.push(portfolioInput.value.trim());

    rpContact.textContent = '';
    const delimiter = currentTemplate === 'classic' ? '  |  ' : '  •  ';
    if (contactParts.length > 0) {
      rpContact.textContent = contactParts.join(delimiter);
      rpContact.style.display = 'block';
    } else {
      rpContact.style.display = 'none';
    }

    // 2. Professional Summary
    const summaryText = summaryInput.value.trim();
    if (summaryText) {
      rpSummary.textContent = summaryText;
      rpSectionSummary.style.display = 'block';
    } else {
      rpSectionSummary.style.display = 'none';
    }

    // 3. Technical Skills
    const skillsLang = skillsLanguagesInput.value.trim();
    const skillsFw = skillsFrameworksInput.value.trim();
    const skillsTools = skillsToolsInput.value.trim();
    const skillsDb = skillsDatabasesInput.value.trim();

    rpSkills.textContent = '';
    const skillCategories = [];
    if (skillsLang) skillCategories.push({ name: 'Languages', value: skillsLang });
    if (skillsFw) skillCategories.push({ name: 'Frameworks', value: skillsFw });
    if (skillsTools) skillCategories.push({ name: 'Cloud & Tools', value: skillsTools });
    if (skillsDb) skillCategories.push({ name: 'Databases', value: skillsDb });

    if (skillCategories.length > 0) {
      skillCategories.forEach(cat => {
        const row = document.createElement('div');
        row.className = 'rp-skill-row';
        const strong = createSafeEl('strong', `${cat.name}: `);
        const text = document.createTextNode(cat.value);
        row.appendChild(strong);
        row.appendChild(text);
        rpSkills.appendChild(row);
      });
      rpSectionSkills.style.display = 'block';
    } else {
      rpSectionSkills.style.display = 'none';
    }

    // 4. Work Experience
    rpExperience.textContent = '';
    const expCards = experienceContainer.querySelectorAll('.dynamic-entry-card');
    let hasValidExp = false;

    if (currentTemplate === 'classic') {
      rpExpHeading.textContent = 'PROFESSIONAL EXPERIENCE';
    } else {
      rpExpHeading.textContent = 'EXPERIENCE & INTERNSHIPS';
    }

    expCards.forEach(card => {
      const role = card.querySelector('.exp-role').value.trim();
      const company = card.querySelector('.exp-company').value.trim();
      const loc = card.querySelector('.exp-location').value.trim();
      const start = card.querySelector('.exp-start').value.trim();
      const end = card.querySelector('.exp-end').value.trim();
      const bulletsText = card.querySelector('.exp-bullets').value.trim();

      if (role || company) {
        hasValidExp = true;
        const itemWrap = document.createElement('div');
        itemWrap.className = 'rp-item-wrap';

        const topRow = document.createElement('div');
        topRow.className = 'rp-item-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'rp-item-title';

        if (currentTemplate === 'classic') {
          // Classic style: Company bold, role italic
          const bCompany = createSafeEl('strong', company || role);
          titleEl.appendChild(bCompany);
          if (loc) {
            titleEl.appendChild(document.createTextNode(` — ${loc}`));
          }
        } else {
          // Modern style: Role bold, company regular
          const bRole = createSafeEl('strong', role);
          titleEl.appendChild(bRole);
          if (company) {
            titleEl.appendChild(document.createTextNode(` — ${company}`));
          }
        }

        let dateStr = '';
        if (start && end) dateStr = `${start} – ${end}`;
        else if (start) dateStr = start;
        else if (end) dateStr = end;

        const dateEl = createSafeEl('div', dateStr, 'rp-item-date');
        topRow.appendChild(titleEl);
        topRow.appendChild(dateEl);
        itemWrap.appendChild(topRow);

        // Subtitle row (Role in italic for classic, location in modern)
        if (currentTemplate === 'classic' && role && company) {
          const subEl = createSafeEl('div', role, 'rp-item-sub');
          itemWrap.appendChild(subEl);
        } else if (currentTemplate === 'modern' && loc) {
          const subEl = createSafeEl('div', loc, 'rp-item-sub');
          itemWrap.appendChild(subEl);
        }

        // Bullets
        if (bulletsText) {
          const ul = document.createElement('ul');
          ul.className = 'rp-bullet-list';
          bulletsText.split('\n').map(b => b.trim()).filter(b => b.length > 0).forEach(b => {
            const cleanBullet = b.replace(/^[-*•–]\s*/, '');
            ul.appendChild(createSafeEl('li', cleanBullet));
          });
          itemWrap.appendChild(ul);
        }

        rpExperience.appendChild(itemWrap);
      }
    });
    rpSectionExperience.style.display = hasValidExp ? 'block' : 'none';

    // 5. Projects
    rpProjects.textContent = '';
    const projCards = projectsContainer.querySelectorAll('.dynamic-entry-card');
    let hasValidProjects = false;

    projCards.forEach(card => {
      const title = card.querySelector('.proj-title').value.trim();
      const tech = card.querySelector('.proj-tech').value.trim();
      const link = card.querySelector('.proj-link').value.trim();
      const bulletsText = card.querySelector('.proj-bullets').value.trim();

      if (title) {
        hasValidProjects = true;
        const itemWrap = document.createElement('div');
        itemWrap.className = 'rp-item-wrap';

        const topRow = document.createElement('div');
        topRow.className = 'rp-item-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'rp-item-title';
        titleEl.appendChild(createSafeEl('strong', title));
        if (tech) {
          const techSpan = createSafeEl('span', ` | ${tech}`, 'rp-sub-tech');
          titleEl.appendChild(techSpan);
        }

        const linkEl = createSafeEl('div', link, 'rp-item-date');
        topRow.appendChild(titleEl);
        topRow.appendChild(linkEl);
        itemWrap.appendChild(topRow);

        if (bulletsText) {
          const ul = document.createElement('ul');
          ul.className = 'rp-bullet-list';
          bulletsText.split('\n').map(b => b.trim()).filter(b => b.length > 0).forEach(b => {
            const cleanBullet = b.replace(/^[-*•–]\s*/, '');
            ul.appendChild(createSafeEl('li', cleanBullet));
          });
          itemWrap.appendChild(ul);
        }

        rpProjects.appendChild(itemWrap);
      }
    });
    rpSectionProjects.style.display = hasValidProjects ? 'block' : 'none';

    // 6. Education
    rpEducation.textContent = '';
    const eduCards = educationContainer.querySelectorAll('.dynamic-entry-card');
    let hasValidEdu = false;

    eduCards.forEach(card => {
      const degree = card.querySelector('.edu-degree').value.trim();
      const school = card.querySelector('.edu-school').value.trim();
      const loc = card.querySelector('.edu-location').value.trim();
      const year = card.querySelector('.edu-year').value.trim();
      const gpa = card.querySelector('.edu-gpa').value.trim();
      const honors = card.querySelector('.edu-honors').value.trim();

      if (degree || school) {
        hasValidEdu = true;
        const itemWrap = document.createElement('div');
        itemWrap.className = 'rp-item-wrap';

        const topRow = document.createElement('div');
        topRow.className = 'rp-item-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'rp-item-title';

        if (currentTemplate === 'classic') {
          titleEl.appendChild(createSafeEl('strong', school || degree));
          if (loc) titleEl.appendChild(document.createTextNode(`, ${loc}`));
        } else {
          titleEl.appendChild(createSafeEl('strong', degree || school));
          if (school) titleEl.appendChild(document.createTextNode(` — ${school}`));
          if (loc) titleEl.appendChild(document.createTextNode(` (${loc})`));
        }

        const dateEl = createSafeEl('div', year, 'rp-item-date');
        topRow.appendChild(titleEl);
        topRow.appendChild(dateEl);
        itemWrap.appendChild(topRow);

        const subNotes = [];
        if (currentTemplate === 'classic' && degree) subNotes.push(degree);
        if (gpa) subNotes.push(`GPA: ${gpa}`);
        if (honors) subNotes.push(honors);

        if (subNotes.length > 0) {
          const subEl = createSafeEl('div', subNotes.join(' — '), 'rp-item-sub');
          itemWrap.appendChild(subEl);
        }

        rpEducation.appendChild(itemWrap);
      }
    });
    rpSectionEducation.style.display = hasValidEdu ? 'block' : 'none';

    // 7. Certifications
    rpCertifications.textContent = '';
    const certCards = certificationsContainer.querySelectorAll('.dynamic-entry-card');
    let hasValidCert = false;

    certCards.forEach(card => {
      const name = card.querySelector('.cert-name').value.trim();
      const issuer = card.querySelector('.cert-issuer').value.trim();
      const date = card.querySelector('.cert-date').value.trim();
      const id = card.querySelector('.cert-id').value.trim();

      if (name) {
        hasValidCert = true;
        const itemWrap = document.createElement('div');
        itemWrap.className = 'rp-item-wrap';

        const topRow = document.createElement('div');
        topRow.className = 'rp-item-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'rp-item-title';
        titleEl.appendChild(createSafeEl('strong', name));
        if (issuer) titleEl.appendChild(document.createTextNode(` — ${issuer}`));
        if (id) titleEl.appendChild(createSafeEl('span', ` (ID: ${id})`, 'rp-sub-tech'));

        const dateEl = createSafeEl('div', date, 'rp-item-date');
        topRow.appendChild(titleEl);
        topRow.appendChild(dateEl);
        itemWrap.appendChild(topRow);

        rpCertifications.appendChild(itemWrap);
      }
    });
    rpSectionCertifications.style.display = hasValidCert ? 'block' : 'none';

    // 8. Achievements
    rpAchievements.textContent = '';
    const achText = achievementsInput.value.trim();
    if (achText) {
      achText.split('\n').map(a => a.trim()).filter(a => a.length > 0).forEach(a => {
        const cleanAch = a.replace(/^[-*•–]\s*/, '');
        rpAchievements.appendChild(createSafeEl('li', cleanAch));
      });
      rpSectionAchievements.style.display = 'block';
    } else {
      rpSectionAchievements.style.display = 'none';
    }

    // 9. Languages
    rpLanguages.textContent = '';
    const langCards = languagesContainer.querySelectorAll('.dynamic-entry-card');
    const langList = [];
    langCards.forEach(card => {
      const name = card.querySelector('.lang-name').value.trim();
      const prof = card.querySelector('.lang-prof').value.trim();
      if (name) {
        langList.push(prof ? `${name} (${prof})` : name);
      }
    });

    if (langList.length > 0) {
      rpLanguages.textContent = langList.join(', ');
      rpSectionLanguages.style.display = 'block';
    } else {
      rpSectionLanguages.style.display = 'none';
    }
  }

  // --------------------------------------------------------------------------
  // Template Switcher
  // --------------------------------------------------------------------------

  function setTemplateStyle(style) {
    currentTemplate = style;
    if (style === 'classic') {
      resumePaperSheet.classList.remove('style-modern');
      resumePaperSheet.classList.add('style-classic');
      templateClassicBtn.classList.add('active');
      templateModernBtn.classList.remove('active');
      previewLayoutIndicator.innerHTML = 'Layout: <strong>Classic ATS</strong>';
    } else {
      resumePaperSheet.classList.remove('style-classic');
      resumePaperSheet.classList.add('style-modern');
      templateModernBtn.classList.add('active');
      templateClassicBtn.classList.remove('active');
      previewLayoutIndicator.innerHTML = 'Layout: <strong>Modern Minimalist</strong>';
    }
    updateLivePreview();
  }

  templateModernBtn.addEventListener('click', () => setTemplateStyle('modern'));
  templateClassicBtn.addEventListener('click', () => setTemplateStyle('classic'));

  // --------------------------------------------------------------------------
  // Data Collection & Contract Serialization
  // --------------------------------------------------------------------------

  function serializeResumeData() {
    const payload = {
      template_style: currentTemplate,
      full_name: fullNameInput.value.trim(),
      headline: headlineInput.value.trim(),
      contact: {
        email: emailInput.value.trim(),
        phone: phoneInput.value.trim(),
        location: locationInput.value.trim(),
        linkedin: linkedinInput.value.trim(),
        github: githubInput.value.trim(),
        portfolio: portfolioInput.value.trim()
      },
      summary: summaryInput.value.trim(),
      skills: {
        languages: skillsLanguagesInput.value.trim(),
        frameworks: skillsFrameworksInput.value.trim(),
        cloud_devops: skillsToolsInput.value.trim(),
        databases: skillsDatabasesInput.value.trim()
      },
      experience: [],
      education: [],
      projects: [],
      certifications: [],
      achievements: [],
      languages: []
    };

    // Experience
    experienceContainer.querySelectorAll('.dynamic-entry-card').forEach(card => {
      const role = card.querySelector('.exp-role').value.trim();
      const company = card.querySelector('.exp-company').value.trim();
      if (role || company) {
        payload.experience.push({
          role: role,
          company: company,
          location: card.querySelector('.exp-location').value.trim(),
          start_date: card.querySelector('.exp-start').value.trim(),
          end_date: card.querySelector('.exp-end').value.trim(),
          current: card.querySelector('.exp-current').checked,
          bullets: card.querySelector('.exp-bullets').value.trim()
        });
      }
    });

    // Education
    educationContainer.querySelectorAll('.dynamic-entry-card').forEach(card => {
      const degree = card.querySelector('.edu-degree').value.trim();
      const school = card.querySelector('.edu-school').value.trim();
      if (degree || school) {
        payload.education.push({
          degree: degree,
          school: school,
          location: card.querySelector('.edu-location').value.trim(),
          graduation_year: card.querySelector('.edu-year').value.trim(),
          gpa: card.querySelector('.edu-gpa').value.trim(),
          honors: card.querySelector('.edu-honors').value.trim()
        });
      }
    });

    // Projects
    projectsContainer.querySelectorAll('.dynamic-entry-card').forEach(card => {
      const title = card.querySelector('.proj-title').value.trim();
      if (title) {
        payload.projects.push({
          title: title,
          technologies: card.querySelector('.proj-tech').value.trim(),
          link: card.querySelector('.proj-link').value.trim(),
          bullets: card.querySelector('.proj-bullets').value.trim()
        });
      }
    });

    // Certifications
    certificationsContainer.querySelectorAll('.dynamic-entry-card').forEach(card => {
      const name = card.querySelector('.cert-name').value.trim();
      if (name) {
        payload.certifications.push({
          name: name,
          issuer: card.querySelector('.cert-issuer').value.trim(),
          date: card.querySelector('.cert-date').value.trim(),
          credential_id: card.querySelector('.cert-id').value.trim()
        });
      }
    });

    // Achievements
    if (achievementsInput.value.trim()) {
      payload.achievements = achievementsInput.value.trim().split('\n').map(a => a.trim()).filter(a => a.length > 0);
    }

    // Languages
    languagesContainer.querySelectorAll('.dynamic-entry-card').forEach(card => {
      const name = card.querySelector('.lang-name').value.trim();
      if (name) {
        payload.languages.push({
          name: name,
          proficiency: card.querySelector('.lang-prof').value.trim()
        });
      }
    });

    return payload;
  }

  // --------------------------------------------------------------------------
  // Download PDF Handler
  // --------------------------------------------------------------------------

  downloadPdfBtn.addEventListener('click', async () => {
    hideNotification();

    const payload = serializeResumeData();

    // Client-side Validation: Must have a name or at least one section
    if (!payload.full_name && !payload.summary && payload.experience.length === 0 && payload.education.length === 0) {
      showNotification('Please fill in your Full Name or at least one resume section before downloading.', 'error');
      fullNameInput.focus();
      return;
    }

    const originalBtnText = downloadPdfBtn.innerHTML;
    downloadPdfBtn.disabled = true;
    downloadPdfBtn.innerHTML = '<span>⏳ Building PDF...</span>';

    try {
      const response = await fetch('/api/builder/download-pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        let errMessage = 'Failed to generate PDF. Please verify your fields.';
        try {
          const errData = await response.json();
          if (errData.error) errMessage = errData.error;
        } catch (_) {}
        throw new Error(errMessage);
      }

      // Convert response stream to Blob and trigger safe download
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);

      // Determine filename from Content-Disposition header if available
      let filename = 'GOAT_Resume.pdf';
      const cdHeader = response.headers.get('Content-Disposition');
      if (cdHeader && cdHeader.includes('filename=')) {
        filename = cdHeader.split('filename=')[1].replace(/["']/g, '').trim();
      } else if (payload.full_name) {
        filename = `${payload.full_name.replace(/[^a-zA-Z0-9_-]/g, '_')}_Resume.pdf`;
      }

      const tempLink = document.createElement('a');
      tempLink.href = downloadUrl;
      tempLink.download = filename;
      document.body.appendChild(tempLink);
      tempLink.click();
      document.body.removeChild(tempLink);
      window.URL.revokeObjectURL(downloadUrl);

      showNotification('Resume PDF downloaded successfully!', 'success');
    } catch (err) {
      console.error(err);
      showNotification(`Download Error: ${err.message}`, 'error');
    } finally {
      downloadPdfBtn.disabled = false;
      downloadPdfBtn.innerHTML = originalBtnText;
    }
  });

  // --------------------------------------------------------------------------
  // Sample Data Pre-filling & Resetting
  // --------------------------------------------------------------------------

  prefillSampleBtn.addEventListener('click', () => {
    // Personal & Contact
    fullNameInput.value = SAMPLE_DATA.fullName;
    headlineInput.value = SAMPLE_DATA.headline;
    emailInput.value = SAMPLE_DATA.email;
    phoneInput.value = SAMPLE_DATA.phone;
    locationInput.value = SAMPLE_DATA.location;
    linkedinInput.value = SAMPLE_DATA.linkedin;
    githubInput.value = SAMPLE_DATA.github;
    portfolioInput.value = SAMPLE_DATA.portfolio;
    summaryInput.value = SAMPLE_DATA.summary;

    // Skills
    skillsLanguagesInput.value = SAMPLE_DATA.skillsLanguages;
    skillsFrameworksInput.value = SAMPLE_DATA.skillsFrameworks;
    skillsToolsInput.value = SAMPLE_DATA.skillsTools;
    skillsDatabasesInput.value = SAMPLE_DATA.skillsDatabases;

    // Clear dynamic containers
    experienceContainer.innerHTML = '';
    educationContainer.innerHTML = '';
    projectsContainer.innerHTML = '';
    certificationsContainer.innerHTML = '';
    languagesContainer.innerHTML = '';

    // Populate dynamic entries
    SAMPLE_DATA.experience.forEach(exp => addExperienceEntry(exp));
    SAMPLE_DATA.education.forEach(edu => addEducationEntry(edu));
    SAMPLE_DATA.projects.forEach(proj => addProjectEntry(proj));
    SAMPLE_DATA.certifications.forEach(cert => addCertificationEntry(cert));
    achievementsInput.value = SAMPLE_DATA.achievements;
    SAMPLE_DATA.languages.forEach(l => addLanguageEntry(l));

    updateLivePreview();
    showNotification('Sample Software Engineer resume loaded into studio.', 'success');
  });

    resetFormBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all resume sections?')) {
      document.getElementById('resumeBuilderForm').reset();
      experienceContainer.innerHTML = '';
      educationContainer.innerHTML = '';
      projectsContainer.innerHTML = '';
      certificationsContainer.innerHTML = '';
      languagesContainer.innerHTML = '';
      updateLivePreview();
      showNotification('Form cleared.', 'success');
    }
  });

  // --------------------------------------------------------------------------
  // Analyze with Existing GOAT AI Matching Engine
  // --------------------------------------------------------------------------

  if (analyzeMatchBtn) {
    analyzeMatchBtn.addEventListener('click', () => {
      const payload = serializeResumeData();

      // Check if resume has content
      if (!payload.full_name && !payload.summary && payload.experience.length === 0) {
        showNotification('Please fill in or load a resume before analyzing with the matching engine.', 'error');
        fullNameInput.focus();
        return;
      }

      // Convert structured resume payload into clean plain text for the matching engine
      const resumeLines = [];
      if (payload.full_name) resumeLines.push(payload.full_name);
      if (payload.headline) resumeLines.push(payload.headline);
      const contactInfo = [];
      if (payload.contact.email) contactInfo.push(payload.contact.email);
      if (payload.contact.phone) contactInfo.push(payload.contact.phone);
      if (payload.contact.location) contactInfo.push(payload.contact.location);
      if (payload.contact.linkedin) contactInfo.push(payload.contact.linkedin);
      if (payload.contact.github) contactInfo.push(payload.contact.github);
      if (contactInfo.length > 0) resumeLines.push(contactInfo.join(' | '));
      resumeLines.push('');

      if (payload.summary) {
        resumeLines.push('PROFESSIONAL SUMMARY');
        resumeLines.push(payload.summary);
        resumeLines.push('');
      }

      const skillCategories = [];
      if (payload.skills.languages) skillCategories.push(`Languages: ${payload.skills.languages}`);
      if (payload.skills.frameworks) skillCategories.push(`Frameworks: ${payload.skills.frameworks}`);
      if (payload.skills.cloud_devops) skillCategories.push(`Cloud & Tools: ${payload.skills.cloud_devops}`);
      if (payload.skills.databases) skillCategories.push(`Databases: ${payload.skills.databases}`);
      if (skillCategories.length > 0) {
        resumeLines.push('TECHNICAL SKILLS');
        resumeLines.push(skillCategories.join('\n'));
        resumeLines.push('');
      }

      if (payload.experience && payload.experience.length > 0) {
        resumeLines.push('EXPERIENCE');
        payload.experience.forEach(exp => {
          let dateStr = exp.start_date || '';
          if (exp.end_date) dateStr += ` - ${exp.end_date}`;
          resumeLines.push(`${exp.role} at ${exp.company} (${dateStr})`);
          if (exp.location) resumeLines.push(exp.location);
          if (exp.bullets) resumeLines.push(exp.bullets);
          resumeLines.push('');
        });
      }

      if (payload.education && payload.education.length > 0) {
        resumeLines.push('EDUCATION');
        payload.education.forEach(edu => {
          let eduLine = `${edu.degree} - ${edu.school}`;
          if (edu.graduation_year) eduLine += ` (${edu.graduation_year})`;
          if (edu.gpa) eduLine += ` [GPA: ${edu.gpa}]`;
          resumeLines.push(eduLine);
        });
        resumeLines.push('');
      }

      if (payload.projects && payload.projects.length > 0) {
        resumeLines.push('PROJECTS');
        payload.projects.forEach(p => {
          let pLine = p.title;
          if (p.technologies) pLine += ` (${p.technologies})`;
          resumeLines.push(pLine);
          if (p.bullets) resumeLines.push(p.bullets);
          resumeLines.push('');
        });
      }

      if (payload.certifications && payload.certifications.length > 0) {
        resumeLines.push('CERTIFICATIONS');
        payload.certifications.forEach(c => {
          let cLine = c.name;
          if (c.issuer) cLine += ` - ${c.issuer}`;
          if (c.date) cLine += ` (${c.date})`;
          resumeLines.push(cLine);
        });
        resumeLines.push('');
      }

      const plainTextResume = resumeLines.join('\n').trim();

      try {
        sessionStorage.setItem('goat_builder_resume_text', plainTextResume);
        window.location.href = '/#analyzer';
      } catch (err) {
        console.error('Failed to store resume text for analysis', err);
        showNotification('Unable to redirect automatically. Please copy resume text manually.', 'error');
      }
    });
  }

  // --------------------------------------------------------------------------
  // Add Entry Button Listeners
  // --------------------------------------------------------------------------

  addExperienceBtn.addEventListener('click', () => addExperienceEntry());
  addEducationBtn.addEventListener('click', () => addEducationEntry());
  addProjectBtn.addEventListener('click', () => addProjectEntry());
  addCertificationBtn.addEventListener('click', () => addCertificationEntry());
  addLanguageBtn.addEventListener('click', () => addLanguageEntry());

  // Attach live event listeners to all static inputs
  document.querySelectorAll('#resumeBuilderForm input, #resumeBuilderForm textarea').forEach(input => {
    input.addEventListener('input', updateLivePreview);
  });

  // Mobile Tab Switching
  if (tabBtnEditor && tabBtnPreview) {
    tabBtnEditor.addEventListener('click', () => {
      tabBtnEditor.classList.add('active');
      tabBtnPreview.classList.remove('active');
      tabBtnEditor.setAttribute('aria-selected', 'true');
      tabBtnPreview.setAttribute('aria-selected', 'false');
      builderFormPane.classList.remove('mobile-hidden');
      builderPreviewPane.classList.add('mobile-hidden');
    });

    tabBtnPreview.addEventListener('click', () => {
      tabBtnPreview.classList.add('active');
      tabBtnEditor.classList.remove('active');
      tabBtnPreview.setAttribute('aria-selected', 'true');
      tabBtnEditor.setAttribute('aria-selected', 'false');
      builderPreviewPane.classList.remove('mobile-hidden');
      builderFormPane.classList.add('mobile-hidden');
    });
  }

  // Pre-seed with default sample data on first load for immediate visual feedback
  prefillSampleBtn.click();
});

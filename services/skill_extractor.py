"""
Skill Extractor Service for GOAT AI.
Identifies technical and professional skills using boundary-safe regex, alias resolution,
and categorized domain mapping.
"""

import re
from typing import List, Set, Dict, Tuple

# Canonical Skill Taxonomy with Aliases and Domain Categories
SKILL_TAXONOMY: Dict[str, Dict] = {
    # Programming Languages
    "python": {"category": "Language", "aliases": ["python", "python3", "py"]},
    "javascript": {"category": "Language", "aliases": ["javascript", "js", "ecmascript"]},
    "typescript": {"category": "Language", "aliases": ["typescript", "ts"]},
    "java": {"category": "Language", "aliases": ["java", "core java"]},
    "c++": {"category": "Language", "aliases": ["c++", "cpp"]},
    "c#": {"category": "Language", "aliases": ["c#", "csharp", "c sharp"]},
    "c": {"category": "Language", "aliases": ["c language", "ansi c", "c"]},
    "go": {"category": "Language", "aliases": ["golang", "go language"]},
    "rust": {"category": "Language", "aliases": ["rust", "rustlang"]},
    "ruby": {"category": "Language", "aliases": ["ruby"]},
    "php": {"category": "Language", "aliases": ["php"]},
    "swift": {"category": "Language", "aliases": ["swift"]},
    "kotlin": {"category": "Language", "aliases": ["kotlin"]},
    "sql": {"category": "Language", "aliases": ["sql", "structured query language"]},
    "r": {"category": "Language", "aliases": ["r language", "r programming", "r"]},
    "html": {"category": "Language", "aliases": ["html", "html5"]},
    "css": {"category": "Language", "aliases": ["css", "css3"]},
    "bash": {"category": "Language", "aliases": ["bash", "shell scripting", "powershell", "zsh"]},

    # Web Frameworks & Libraries
    "flask": {"category": "Web Framework", "aliases": ["flask"]},
    "django": {"category": "Web Framework", "aliases": ["django", "django rest framework", "drf"]},
    "fastapi": {"category": "Web Framework", "aliases": ["fastapi", "fast api"]},
    "react": {"category": "Web Framework", "aliases": ["react", "react.js", "reactjs"]},
    "next.js": {"category": "Web Framework", "aliases": ["next.js", "nextjs"]},
    "node.js": {"category": "Web Framework", "aliases": ["node.js", "nodejs", "node"]},
    "express": {"category": "Web Framework", "aliases": ["express", "express.js", "expressjs"]},
    "angular": {"category": "Web Framework", "aliases": ["angular", "angularjs"]},
    "vue.js": {"category": "Web Framework", "aliases": ["vue", "vue.js", "vuejs"]},
    "spring boot": {"category": "Web Framework", "aliases": ["spring boot", "springboot", "spring framework"]},
    "asp.net": {"category": "Web Framework", "aliases": ["asp.net", "dotnet", ".net", ".net core"]},
    "rest api": {"category": "Web Architecture", "aliases": ["rest api", "restful api", "rest", "restful"]},
    "graphql": {"category": "Web Architecture", "aliases": ["graphql"]},
    "tailwind css": {"category": "Web Framework", "aliases": ["tailwind", "tailwind css", "tailwindcss"]},
    "bootstrap": {"category": "Web Framework", "aliases": ["bootstrap", "bootstrap5"]},

    # Databases & Storage
    "postgresql": {"category": "Database", "aliases": ["postgresql", "postgres", "psql"]},
    "mysql": {"category": "Database", "aliases": ["mysql"]},
    "sqlite": {"category": "Database", "aliases": ["sqlite", "sqlite3"]},
    "mongodb": {"category": "Database", "aliases": ["mongodb", "mongo"]},
    "redis": {"category": "Database", "aliases": ["redis"]},
    "oracle": {"category": "Database", "aliases": ["oracle db", "oracle database"]},
    "cassandra": {"category": "Database", "aliases": ["cassandra"]},
    "dynamodb": {"category": "Database", "aliases": ["dynamodb"]},
    "elasticsearch": {"category": "Database", "aliases": ["elasticsearch", "elastic search"]},

    # Cloud, DevOps & Tools
    "aws": {"category": "Cloud & DevOps", "aliases": ["aws", "amazon web services", "amazon ec2", "s3", "lambda"]},
    "azure": {"category": "Cloud & DevOps", "aliases": ["azure", "microsoft azure"]},
    "gcp": {"category": "Cloud & DevOps", "aliases": ["gcp", "google cloud", "google cloud platform"]},
    "docker": {"category": "Cloud & DevOps", "aliases": ["docker", "containerization", "containers"]},
    "kubernetes": {"category": "Cloud & DevOps", "aliases": ["kubernetes", "k8s"]},
    "git": {"category": "Cloud & DevOps", "aliases": ["git", "github", "gitlab", "version control"]},
    "ci/cd": {"category": "Cloud & DevOps", "aliases": ["ci/cd", "ci cd", "continuous integration", "github actions", "jenkins"]},
    "terraform": {"category": "Cloud & DevOps", "aliases": ["terraform", "iac", "infrastructure as code"]},
    "linux": {"category": "Cloud & DevOps", "aliases": ["linux", "ubuntu", "debian", "redhat", "centos"]},
    "prometheus": {"category": "Cloud & DevOps", "aliases": ["prometheus", "grafana", "monitoring"]},

    # Data Science, ML & AI
    "machine learning": {"category": "AI/Data", "aliases": ["machine learning", "ml"]},
    "deep learning": {"category": "AI/Data", "aliases": ["deep learning", "dl", "neural networks"]},
    "data analysis": {"category": "AI/Data", "aliases": ["data analysis", "data analytics"]},
    "pandas": {"category": "AI/Data", "aliases": ["pandas"]},
    "numpy": {"category": "AI/Data", "aliases": ["numpy"]},
    "scikit-learn": {"category": "AI/Data", "aliases": ["scikit-learn", "sklearn"]},
    "tensorflow": {"category": "AI/Data", "aliases": ["tensorflow", "tf"]},
    "pytorch": {"category": "AI/Data", "aliases": ["pytorch"]},
    "nlp": {"category": "AI/Data", "aliases": ["nlp", "natural language processing"]},
    "power bi": {"category": "AI/Data", "aliases": ["power bi", "powerbi"]},
    "tableau": {"category": "AI/Data", "aliases": ["tableau"]},
    "excel": {"category": "AI/Data", "aliases": ["excel", "microsoft excel", "spreadsheets", "advanced excel"]},
    "spark": {"category": "AI/Data", "aliases": ["apache spark", "spark", "pyspark"]},
    "hadoop": {"category": "AI/Data", "aliases": ["hadoop", "mapreduce"]},

    # Software Engineering & Soft Skills
    "data structures": {"category": "Core CS", "aliases": ["data structures", "dsa", "algorithms"]},
    "system design": {"category": "Core CS", "aliases": ["system design", "software architecture", "microservices"]},
    "object oriented programming": {"category": "Core CS", "aliases": ["object oriented programming", "oop", "oops"]},
    "unit testing": {"category": "Quality", "aliases": ["unit testing", "pytest", "jest", "tdd", "test driven development"]},
    "agile": {"category": "Methodology", "aliases": ["agile", "scrum", "kanban", "sprints"]},
    "problem solving": {"category": "Soft Skill", "aliases": ["problem solving", "analytical skills", "critical thinking"]},
    "communication": {"category": "Soft Skill", "aliases": ["communication", "verbal communication", "written communication", "presentation skills"]},
    "teamwork": {"category": "Soft Skill", "aliases": ["teamwork", "collaboration", "cross-functional teams"]},
    "leadership": {"category": "Soft Skill", "aliases": ["leadership", "mentoring", "team lead"]}
}


def build_alias_lookup() -> List[Tuple[re.Pattern, str]]:
    """
    Compile regex patterns for all aliases mapped to canonical skill names.
    Sort by alias length descending to ensure longer phrases (e.g. 'machine learning')
    are matched prior to single words.
    """
    patterns = []
    alias_to_canonical = []

    for canonical, data in SKILL_TAXONOMY.items():
        for alias in data.get("aliases", [canonical]):
            alias_to_canonical.append((alias.lower(), canonical))

    # Sort descending by length so compound phrases match first
    alias_to_canonical.sort(key=lambda x: len(x[0]), reverse=True)

    for alias, canonical in alias_to_canonical:
        escaped = re.escape(alias)
        # Handle special characters like c++, c#, .net gracefully
        # Boundaries: match start of string or non-alphanumeric, and end of string or non-alphanumeric
        pattern_str = r'(?<![a-zA-Z0-9#+])' + escaped + r'(?![a-zA-Z0-9#+])'
        pattern = re.compile(pattern_str, re.IGNORECASE)
        patterns.append((pattern, canonical))

    return patterns


COMPILED_PATTERNS = build_alias_lookup()


def extract_skills_from_text(text: str) -> List[str]:
    """
    Extract a deduplicated, ordered list of canonical skills found in the given text.
    """
    if not text:
        return []

    found_canonical: Set[str] = set()
    ordered_skills: List[str] = []

    for pattern, canonical in COMPILED_PATTERNS:
        if canonical not in found_canonical and pattern.search(text):
            found_canonical.add(canonical)
            ordered_skills.append(canonical)

    return ordered_skills


def get_skill_category(skill_name: str) -> str:
    """Return the high-level category of a canonical skill."""
    return SKILL_TAXONOMY.get(skill_name.lower(), {}).get("category", "Technical")

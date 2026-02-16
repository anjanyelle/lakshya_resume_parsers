from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

try:
    import spacy
    from spacy.matcher import PhraseMatcher
except Exception:  # noqa: BLE001
    spacy = None
    PhraseMatcher = None

logger = logging.getLogger(__name__)


SECTION_KEYS = [
    # ============================================
    # CORE SECTIONS (Essential)
    # ============================================
    "contact",
    "summary",
    "experience",
    "education",
    "skills",
    
    # ============================================
    # CREDENTIALS & QUALIFICATIONS
    # ============================================
    "certifications",
    "licenses",
    "credentials",
    "accreditations",
    
    # ============================================
    # ACHIEVEMENTS & RECOGNITION
    # ============================================
    "awards",
    "honors",
    "achievements",
    "accomplishments",
    "recognition",
    "distinctions",
    
    # ============================================
    # PROJECTS & CREATIVE WORK
    # ============================================
    "projects",
    "portfolio",
    "case_studies",
    "sample_work",
    
    # ============================================
    # RESEARCH & PUBLICATIONS
    # ============================================
    "publications",
    "patents",
    "research",
    "papers",
    "dissertations",
    "thesis",
    
    # ============================================
    # LANGUAGE & COMMUNICATION
    # ============================================
    "languages",
    "language_skills",
    
    # ============================================
    # TRAINING & DEVELOPMENT
    # ============================================
    "training",
    "courses",
    "professional_development",
    "continuing_education",
    "workshops",
    "seminars",
    "conferences_attended",
    
    # ============================================
    # PRESENTATIONS & SPEAKING
    # ============================================
    "presentations",
    "speaking_engagements",
    "public_speaking",
    "conferences",
    "talks",
    
    # ============================================
    # VOLUNTEER & COMMUNITY
    # ============================================
    "volunteer",
    "volunteer_experience",
    "volunteering",
    "community_service",
    "civic_engagement",
    "social_work",
    
    # ============================================
    # ACTIVITIES & INTERESTS
    # ============================================
    "extracurricular",
    "extracurricular_activities",
    "activities",
    "interests",
    "hobbies",
    "personal_interests",
    
    # ============================================
    # PROFESSIONAL ASSOCIATIONS
    # ============================================
    "memberships",
    "professional_memberships",
    "affiliations",
    "professional_affiliations",
    "professional_associations",
    "associations",
    "organizations",
    "societies",
    
    # ============================================
    # REFERENCES & TESTIMONIALS
    # ============================================
    "references",
    "professional_references",
    "recommendations",
    "testimonials",
    "referees",
    
    # ============================================
    # SPECIALIZED EXPERIENCE
    # ============================================
    "internships",
    "internship_experience",
    "teaching_experience",
    "research_experience",
    "leadership_experience",
    "management_experience",
    "consulting_experience",
    "entrepreneurship",
    "military_service",
    "military_experience",
    
    # ============================================
    # ACADEMIC SPECIFIC
    # ============================================
    "dissertation",
    "doctoral_dissertation",
    "masters_thesis",
    "thesis",
    "academic_projects",
    "coursework",
    "relevant_coursework",
    "major_coursework",
    "academic_achievements",
    "fellowships",
    "scholarships",
    "grants",
    "funding",
    
    # ============================================
    # TECHNICAL SKILLS (Detailed)
    # ============================================
    "technical_skills",
    "technical_expertise",
    "programming_skills",
    "programming_languages",
    "software_skills",
    "software",
    "tools",
    "tools_and_technologies",
    "technologies",
    "frameworks",
    "platforms",
    "tech_stack",
    "technical_proficiencies",
    
    # ============================================
    # COMPETENCIES & STRENGTHS
    # ============================================
    "competencies",
    "core_competencies",
    "key_competencies",
    "strengths",
    "core_strengths",
    "expertise",
    "areas_of_expertise",
    "specializations",
    "capabilities",
    
    # ============================================
    # BUSINESS & LEADERSHIP
    # ============================================
    "board_positions",
    "board_memberships",
    "advisory_roles",
    "advisory_boards",
    "consulting",
    "consulting_experience",
    "executive_experience",
    "directorship",
    
    # ============================================
    # CREATIVE & MEDIA
    # ============================================
    "exhibitions",
    "performances",
    "shows",
    "productions",
    "repertoire",
    "media_appearances",
    "press",
    "press_coverage",
    "portfolio_highlights",
    
    # ============================================
    # LEGAL & COMPLIANCE
    # ============================================
    "bar_admissions",
    "licenses_and_admissions",
    "clearances",
    "security_clearances",
    "work_authorization",
    "visa_status",
    "legal_status",
    
    # ============================================
    # PROFILE & SUMMARY VARIATIONS
    # ============================================
    "profile",
    "professional_profile",
    "career_profile",
    "executive_summary",
    "professional_summary",
    "career_summary",
    "objective",
    "career_objective",
    "professional_objective",
    "highlights",
    "career_highlights",
    "professional_highlights",
    "key_highlights",
    "qualifications_summary",
    "summary_of_qualifications",
    "value_proposition",
    
    # ============================================
    # INDUSTRY-SPECIFIC SECTIONS
    # ============================================
    # Healthcare
    "clinical_experience",
    "clinical_rotations",
    "clinical_training",
    "patient_care",
    "medical_procedures",
    
    # Legal
    "cases",
    "notable_cases",
    "practice_areas",
    "bar_admissions",
    
    # Entertainment/Media
    "productions",
    "credits",
    "filmography",
    "discography",
    
    # Music/Performing Arts
    "repertoire",
    "performances",
    "concerts",
    "recitals",
    
    # Visual Arts
    "exhibitions",
    "gallery_shows",
    "collections",
    "commissions",
    
    # Sales/Business Development
    "sales_achievements",
    "revenue_generated",
    "clients",
    "key_accounts",
    
    # Teaching/Academia
    "teaching_philosophy",
    "courses_taught",
    "student_supervision",
    "academic_service",
    
    # ============================================
    # ADDITIONAL INFORMATION
    # ============================================
    "additional_information",
    "additional_details",
    "additional",
    "other_information",
    "other",
    "miscellaneous",
    "supplementary_information",
    "supplementary",
    "further_information",
    "notes",
    
    # ============================================
    # PERSONAL (Less common in modern resumes)
    # ============================================
    "personal_information",
    "personal_details",
    "personal_data",
    "demographics",
    "availability",
    "location_preference",
    "relocation",
    "salary_expectations",
    "expected_salary",
]

SECTION_ALIASES: dict[str, list[str]] = {
    "contact": [
        # English
        "contact information", "contact info", "contact details", "contact",
        "personal information", "personal info", "personal details", "personal data",
        "contact & personal information", "personal & contact information",
        "get in touch", "reach me", "how to reach me", "find me",
        "details", "info", "information",
        
        # Spanish
        "datos personales", "información personal", "información de contacto",
        "detalles personales", "contacto", "datos de contacto",
        "información de contacto y personal", "detalles de contacto",
        
        # French
        "coordonnées", "informations personnelles", "détails personnels",
        "informations de contact", "contact", "renseignements personnels",
        "coordonnées personnelles", "mes coordonnées",
        
        # German
        "kontakt", "kontaktdaten", "kontaktinformationen",
        "persönliche daten", "persönliche informationen", "persönliches",
        "kontaktinformation", "angaben zur person",
        
        # Hindi
        "संपर्क जानकारी", "व्यक्तिगत विवरण", "संपर्क विवरण",
        "व्यक्तिगत जानकारी", "संपर्क", "विवरण",
        
        # Portuguese
        "informações de contato", "dados pessoais", "informações pessoais",
        "contato", "detalhes pessoais", "informação pessoal",
        
        # Italian
        "informazioni di contatto", "dati personali", "informazioni personali",
        "contatto", "dettagli personali", "recapiti",
        
        # Chinese
        "联系方式", "个人信息", "联系信息", "个人资料",
        
        # Japanese
        "連絡先", "個人情報", "連絡先情報",
        
        # Other variations
        "contact me", "about me", "personal", "bio", "biography"
    ],
    
    "summary": [
        # English
        "professional summary", "summary", "executive summary", "career summary",
        "profile", "professional profile", "career profile", "personal profile",
        "objective", "career objective", "professional objective", "career goal",
        "about", "about me", "introduction", "overview", "career overview",
        "personal statement", "professional statement", "statement",
        "qualifications summary", "summary of qualifications",
        "professional overview", "executive profile", "career highlights",
        "snapshot", "professional snapshot", "value proposition",
        "branding statement", "personal brand", "elevator pitch",
        "highlights", "career summary highlights", "professional highlights",
        
        # Spanish
        "resumen profesional", "resumen", "perfil profesional", "perfil",
        "objetivo", "objetivo profesional", "objetivo de carrera",
        "sobre mí", "acerca de", "declaración personal", "resumen ejecutivo",
        "presentación", "descripción profesional", "extracto",
        
        # French
        "résumé professionnel", "sommaire", "profil professionnel", "profil",
        "objectif", "objectif professionnel", "objectif de carrière",
        "à propos", "présentation", "aperçu", "déclaration personnelle",
        "synthèse", "résumé exécutif",
        
        # German
        "zusammenfassung", "berufliches profil", "profil", "karriereprofil",
        "zielsetzung", "berufsziel", "karriereziel", "über mich",
        "kurzprofil", "qualifikationsprofil", "berufliche zusammenfassung",
        "persönliche darstellung", "kurzvorstellung",
        
        # Hindi
        "सारांश", "पेशेवर सारांश", "प्रोफ़ाइल", "व्यावसायिक प्रोफ़ाइल",
        "उद्देश्य", "करियर उद्देश्य", "परिचय", "अवलोकन",
        "व्यक्तिगत विवरण", "करियर सारांश",
        
        # Portuguese
        "resumo profissional", "resumo", "perfil profissional", "perfil",
        "objetivo", "objetivo profissional", "objetivo de carreira",
        "sobre mim", "apresentação", "sumário executivo", "declaração pessoal",
        
        # Italian
        "riepilogo professionale", "profilo professionale", "profilo",
        "obiettivo", "obiettivo professionale", "obiettivo di carriera",
        "chi sono", "presentazione", "sommario", "profilo personale",
        
        # Chinese
        "个人简介", "职业概述", "求职意向", "个人陈述", "职业目标",
        
        # Japanese
        "プロフィール", "職務要約", "キャリアサマリー", "自己紹介", "志望動機"
    ],
    
    "experience": [
        # English
        "work experience", "professional experience", "experience",
        "employment history", "employment", "work history", "career history",
        "professional history", "career experience", "job history",
        "work", "relevant experience", "professional background",
        "employment record", "career", "work record", "positions held",
        "professional experience & achievements", "work experience & achievements",
        "experience summary", "career progression", "professional journey",
        "positions", "roles", "appointments", "engagements",
        
        # Spanish
        "experiencia profesional", "experiencia laboral", "experiencia",
        "historial laboral", "historial profesional", "trayectoria profesional",
        "historial de empleo", "experiencia de trabajo", "carrera profesional",
        "antecedentes laborales", "empleos anteriores", "cargos desempeñados",
        
        # French
        "expérience professionnelle", "expérience", "parcours professionnel",
        "historique professionnel", "carrière", "emplois précédents",
        "expérience de travail", "antécédents professionnels", "parcours",
        "historique d'emploi", "postes occupés", "expériences",
        
        # German
        "berufserfahrung", "erfahrung", "beruflicher werdegang",
        "beschäftigungsverlauf", "karriere", "berufliche laufbahn",
        "arbeitserfahrung", "berufliche stationen", "tätigkeiten",
        "bisherige tätigkeiten", "werdegang", "berufliche erfahrung",
        
        # Hindi
        "अनुभव", "कार्य अनुभव", "व्यावसायिक अनुभव", "पेशेवर अनुभव",
        "रोजगार इतिहास", "करियर इतिहास", "नौकरी का इतिहास",
        "व्यावसायिक पृष्ठभूमि", "कार्य इतिहास",
        
        # Portuguese
        "experiência profissional", "experiência", "histórico profissional",
        "histórico de trabalho", "experiência de trabalho", "carreira",
        "trajetória profissional", "empregos anteriores", "experiências",
        
        # Italian
        "esperienza professionale", "esperienza lavorativa", "esperienza",
        "storia lavorativa", "carriera", "percorso professionale",
        "esperienze professionali", "background professionale",
        
        # Chinese
        "工作经历", "工作经验", "职业经历", "从业经历", "任职经历",
        
        # Japanese
        "職務経歴", "経歴", "職歴", "キャリア", "実務経験"
    ],
    
    "education": [
        # English
        "education", "educational background", "academic background",
        "academic qualifications", "educational qualifications", "qualifications",
        "academic credentials", "academic history", "educational history",
        "education & training", "training & education", "education and qualifications",
        "degrees", "academic degrees", "educational credentials",
        "schooling", "academic experience", "educational experience",
        "university", "college", "academia", "studies", "academic record",
        
        # Spanish
        "educación", "formación académica", "formación", "estudios",
        "antecedentes académicos", "historial académico", "cualificaciones académicas",
        "títulos académicos", "formación educativa", "educación y formación",
        "estudios realizados", "trayectoria académica",
        
        # French
        "formation", "formation académique", "parcours académique",
        "études", "diplômes", "qualifications académiques",
        "éducation", "parcours scolaire", "formation et éducation",
        "cursus académique", "antécédents académiques", "scolarité",
        
        # German
        "ausbildung", "bildung", "schulbildung", "akademischer werdegang",
        "bildungsweg", "schulischer und beruflicher werdegang",
        "akademische qualifikationen", "akademischer hintergrund",
        "studium", "ausbildung und bildung", "qualifikationen",
        
        # Hindi
        "शिक्षा", "शैक्षिक योग्यता", "शैक्षिक पृष्ठभूमि",
        "शैक्षणिक योग्यता", "अकादमिक योग्यता", "शैक्षिक इतिहास",
        "शिक्षा और प्रशिक्षण", "अध्ययन", "डिग्री",
        
        # Portuguese
        "educação", "formação acadêmica", "formação", "histórico acadêmico",
        "qualificações acadêmicas", "histórico educacional", "estudos",
        "formação educacional", "titulação", "educação e treinamento",
        
        # Italian
        "istruzione", "formazione accademica", "formazione", "percorso di studi",
        "studi", "qualifiche accademiche", "background accademico",
        "titoli di studio", "istruzione e formazione",
        
        # Chinese
        "教育背景", "教育经历", "学历", "教育", "学习经历",
        
        # Japanese
        "学歴", "教育", "教育背景", "学歴・資格"
    ],
    
    "skills": [
        # English
        "skills", "technical skills", "professional skills", "core skills",
        "skills summary", "skill summary", "key skills", "areas of expertise",
        "expertise", "core competencies", "competencies", "capabilities",
        "skills & expertise", "skills and abilities", "abilities",
        "technical expertise", "technical proficiency", "proficiencies",
        "skills & tools", "tools & technologies", "technologies",
        "technical stack", "tech stack", "technology stack",
        "skills and competencies", "qualifications", "technical qualifications",
        "areas of proficiency", "specializations", "technical abilities",
        "skill set", "skillset", "technical skillset", "professional skillset",
        "what i bring", "what i offer", "core strengths", "strengths",
        
        # Spanish
        "habilidades", "habilidades técnicas", "habilidades profesionales",
        "competencias", "competencias técnicas", "competencias clave",
        "destrezas", "conocimientos", "conocimientos técnicos",
        "habilidades y competencias", "área de experiencia", "experiencia técnica",
        "capacidades", "aptitudes", "habilidades profesionales",
        
        # French
        "compétences", "compétences techniques", "compétences professionnelles",
        "savoir-faire", "expertise", "aptitudes", "capacités",
        "compétences clés", "domaines d'expertise", "qualifications techniques",
        "compétences et expertise", "connaissances techniques",
        
        # German
        "fähigkeiten", "kenntnisse", "fertigkeiten", "kompetenzen",
        "technische fähigkeiten", "fachkenntnisse", "qualifikationen",
        "expertise", "kernkompetenzen", "schlüsselqualifikationen",
        "technische kenntnisse", "fachwissen", "können",
        
        # Hindi
        "कौशल", "तकनीकी कौशल", "व्यावसायिक कौशल", "मुख्य कौशल",
        "दक्षता", "योग्यता", "क्षमताएं", "विशेषज्ञता",
        "तकनीकी योग्यता", "तकनीकी विशेषज्ञता",
        
        # Portuguese
        "habilidades", "habilidades técnicas", "competências",
        "competências técnicas", "expertise", "conhecimentos",
        "capacidades", "aptidões", "qualificações técnicas",
        "habilidades profissionais", "conhecimentos técnicos",
        
        # Italian
        "competenze", "competenze tecniche", "abilità", "capacità",
        "competenze professionali", "conoscenze", "conoscenze tecniche",
        "expertise", "qualifiche", "abilità tecniche",
        
        # Chinese
        "技能", "专业技能", "技术技能", "核心技能", "专长",
        
        # Japanese
        "スキル", "技術スキル", "専門スキル", "能力", "専門知識"
    ],
    
    "certifications": [
        # English
        "certifications", "certification", "certificates", "certificate",
        "licenses", "license", "licensing", "credentials", "accreditations",
        "professional certifications", "professional certificates",
        "licenses & certifications", "certifications & licenses",
        "licenses & credentials", "credentials & certifications",
        "courses & certifications", "training & certifications",
        "certifications and training", "professional credentials",
        "accreditation", "certified", "licensed", "qualifications",
        "professional licenses", "industry certifications",
        
        # Spanish
        "certificaciones", "certificación", "certificados", "certificado",
        "licencias", "licencia", "credenciales", "acreditaciones",
        "certificaciones profesionales", "licencias profesionales",
        "certificaciones y licencias", "cursos y certificaciones",
        "certificados y acreditaciones",
        
        # French
        "certifications", "certification", "certificats", "certificat",
        "licences", "licence", "accréditations", "habilitations",
        "certifications professionnelles", "diplômes professionnels",
        "certifications et licences", "qualifications professionnelles",
        
        # German
        "zertifizierungen", "zertifizierung", "zertifikate", "zertifikat",
        "lizenzen", "lizenz", "qualifikationen", "berechtigungen",
        "professionelle zertifizierungen", "berufliche qualifikationen",
        "zertifikate und lizenzen", "akkreditierungen",
        
        # Hindi
        "प्रमाणपत्र", "प्रमाणन", "लाइसेंस", "साख", "मान्यता",
        "व्यावसायिक प्रमाणपत्र", "व्यावसायिक लाइसेंस",
        "प्रमाण पत्र और लाइसेंस",
        
        # Portuguese
        "certificações", "certificação", "certificados", "certificado",
        "licenças", "licença", "credenciais", "acreditações",
        "certificações profissionais", "licenças profissionais",
        
        # Italian
        "certificazioni", "certificazione", "certificati", "certificato",
        "licenze", "licenza", "credenziali", "accreditamenti",
        "certificazioni professionali", "qualifiche professionali",
        
        # Chinese
        "证书", "认证", "资格证书", "执照", "专业认证",
        
        # Japanese
        "資格", "認定", "免許", "証明書", "ライセンス"
    ],
    
    "projects": [
        # English
        "projects", "project experience", "key projects", "notable projects",
        "portfolio", "work portfolio", "project portfolio", "portfolio projects",
        "case studies", "selected projects", "project highlights",
        "major projects", "significant projects", "projects & portfolio",
        "relevant projects", "academic projects", "personal projects",
        "professional projects", "project work", "project involvement",
        "sample projects", "featured projects", "project examples",
        
        # Spanish
        "proyectos", "proyectos destacados", "proyectos clave",
        "portfolio", "portafolio", "portafolio de proyectos",
        "estudios de caso", "proyectos relevantes", "proyectos importantes",
        "experiencia en proyectos", "proyectos profesionales",
        
        # French
        "projets", "projets clés", "projets notables", "réalisations",
        "portfolio", "portfolio de projets", "portefeuille",
        "études de cas", "projets importants", "projets professionnels",
        "expérience de projet", "projets majeurs",
        
        # German
        "projekte", "projektübersicht", "projekterfahrung",
        "portfolio", "projektportfolio", "referenzprojekte",
        "fallstudien", "wichtige projekte", "wesentliche projekte",
        "projektarbeit", "beispielprojekte",
        
        # Hindi
        "परियोजनाएं", "परियोजना अनुभव", "मुख्य परियोजनाएं",
        "पोर्टफोलियो", "केस स्टडी", "महत्वपूर्ण परियोजनाएं",
        "व्यावसायिक परियोजनाएं",
        
        # Portuguese
        "projetos", "projetos destacados", "projetos principais",
        "portfólio", "portfólio de projetos", "estudos de caso",
        "projetos relevantes", "experiência em projetos",
        
        # Italian
        "progetti", "progetti chiave", "progetti rilevanti",
        "portfolio", "portfolio progetti", "casi studio",
        "progetti importanti", "esperienza progettuale",
        
        # Chinese
        "项目经历", "项目经验", "项目作品", "作品集", "案例研究",
        
        # Japanese
        "プロジェクト", "プロジェクト経験", "ポートフォリオ", "実績"
    ],
    
    "awards": [
        # English
        "awards", "awards & honors", "honors", "honors & awards",
        "achievements", "key achievements", "accomplishments",
        "recognition", "recognitions", "professional recognition",
        "honors and distinctions", "distinctions", "accolades",
        "professional highlights", "career highlights", "notable achievements",
        "awards and recognition", "awards and achievements",
        "scholarships", "honors & scholarships", "prizes",
        "commendations", "distinctions and awards",
        
        # Spanish
        "premios", "honores", "premios y honores", "reconocimientos",
        "logros", "logros clave", "logros destacados", "distinciones",
        "reconocimientos profesionales", "honores y distinciones",
        "premios y reconocimientos", "galardones", "logros profesionales",
        
        # French
        "récompenses", "distinctions", "honneurs", "reconnaissances",
        "prix", "réalisations", "accomplissements", "prix et distinctions",
        "distinctions et récompenses", "reconnaissances professionnelles",
        "honneurs et récompenses", "mentions honorables",
        
        # German
        "auszeichnungen", "ehrungen", "anerkennungen", "preise",
        "leistungen", "erfolge", "ehrungen und auszeichnungen",
        "berufliche auszeichnungen", "anerkennungen und ehrungen",
        "preise und auszeichnungen", "besondere leistungen",
        
        # Hindi
        "पुरस्कार", "सम्मान", "पुरस्कार और सम्मान", "उपलब्धियां",
        "मान्यता", "प्रमुख उपलब्धियां", "व्यावसायिक सम्मान",
        "उपलब्धियों और पुरस्कार",
        
        # Portuguese
        "prêmios", "honrarias", "reconhecimentos", "conquistas",
        "realizações", "distinções", "prêmios e honrarias",
        "reconhecimentos profissionais", "prêmios e reconhecimentos",
        
        # Italian
        "premi", "riconoscimenti", "onorificenze", "distinzioni",
        "risultati", "premi e riconoscimenti", "onori", "traguardi",
        "riconoscimenti professionali",
        
        # Chinese
        "获奖情况", "荣誉奖项", "奖项", "荣誉", "成就",
        
        # Japanese
        "受賞歴", "表彰", "栄誉", "実績", "賞"
    ],
    
    "languages": [
        # English
        "languages", "language skills", "language proficiency",
        "languages spoken", "linguistic skills", "linguistic abilities",
        "foreign languages", "language competencies", "language capabilities",
        "multilingual skills", "language fluency",
        
        # Spanish
        "idiomas", "habilidades lingüísticas", "conocimiento de idiomas",
        "idiomas hablados", "competencias lingüísticas", "lenguas",
        
        # French
        "langues", "compétences linguistiques", "langues parlées",
        "maîtrise des langues", "connaissances linguistiques",
        
        # German
        "sprachen", "sprachkenntnisse", "fremdsprachen",
        "sprachliche fähigkeiten", "sprachkompetenzen",
        
        # Hindi
        "भाषाएँ", "भाषा कौशल", "भाषा दक्षता", "भाषा ज्ञान",
        
        # Portuguese
        "idiomas", "habilidades linguísticas", "conhecimento de idiomas",
        "competências linguísticas", "línguas",
        
        # Italian
        "lingue", "competenze linguistiche", "conoscenze linguistiche",
        "lingue parlate", "abilità linguistiche",
        
        # Chinese
        "语言能力", "语言技能", "掌握语言", "外语",
        
        # Japanese
        "言語", "語学力", "言語スキル", "外国語"
    ],
    
    "publications": [
        # English
        "publications", "publications & presentations", "research publications",
        "patents", "patents & publications", "papers", "research papers",
        "scholarly publications", "academic publications", "published works",
        "research output", "publications and patents", "papers & publications",
        "conference papers", "journal articles", "research contributions",
        "authored works", "written works", "intellectual property",
        
        # Spanish
        "publicaciones", "patentes", "publicaciones científicas",
        "artículos publicados", "trabajos publicados", "publicaciones académicas",
        "publicaciones y patentes", "artículos de investigación",
        
        # French
        "publications", "brevets", "publications scientifiques",
        "articles publiés", "travaux publiés", "publications académiques",
        "publications et brevets", "articles de recherche",
        
        # German
        "veröffentlichungen", "patente", "publikationen",
        "wissenschaftliche veröffentlichungen", "forschungsarbeiten",
        "veröffentlichungen und patente", "fachpublikationen",
        
        # Hindi
        "प्रकाशन", "पेटेंट", "शोध प्रकाशन", "अकादमिक प्रकाशन",
        "प्रकाशित कार्य", "प्रकाशन और पेटेंट",
        
        # Portuguese
        "publicações", "patentes", "publicações científicas",
        "artigos publicados", "publicações acadêmicas",
        "publicações e patentes", "trabalhos publicados",
        
        # Italian
        "pubblicazioni", "brevetti", "pubblicazioni scientifiche",
        "articoli pubblicati", "pubblicazioni accademiche",
        "pubblicazioni e brevetti", "lavori pubblicati",
        
        # Chinese
        "发表论文", "专利", "学术成果", "研究成果", "著作",
        
        # Japanese
        "論文", "特許", "研究業績", "学術論文", "発表論文"
    ],
    
    "volunteer": [
        # English
        "volunteer experience", "volunteer work", "volunteering",
        "community service", "community involvement", "civic engagement",
        "volunteer activities", "social work", "community activities",
        "volunteer & community service", "extracurricular activities",
        "social activities", "community engagement", "volunteer roles",
        
        # Spanish
        "experiencia de voluntariado", "voluntariado", "servicio comunitario",
        "trabajo voluntario", "actividades de voluntariado",
        "compromiso comunitario", "servicio social",
        
        # French
        "bénévolat", "expérience bénévole", "engagement communautaire",
        "service communautaire", "activités bénévoles", "travail bénévole",
        
        # German
        "ehrenamtliche tätigkeit", "freiwilligenarbeit", "ehrenamt",
        "gemeinnützige arbeit", "soziales engagement", "freiwilligendienst",
        
        # Hindi
        "स्वयंसेवी कार्य", "स्वयंसेवा", "सामुदायिक सेवा",
        "स्वयंसेवी अनुभव", "सामाजिक कार्य",
        
        # Portuguese
        "trabalho voluntário", "voluntariado", "serviço comunitário",
        "experiência voluntária", "atividades voluntárias",
        
        # Italian
        "volontariato", "esperienza di volontariato", "servizio comunitario",
        "attività di volontariato", "impegno sociale",
        
        # Chinese
        "志愿者经历", "志愿工作", "社区服务", "志愿活动",
        
        # Japanese
        "ボランティア活動", "ボランティア経験", "社会貢献活動"
    ],
    
    "interests": [
        # English
        "interests", "hobbies", "personal interests", "hobbies & interests",
        "activities", "extracurricular activities", "outside interests",
        "personal activities", "recreational activities", "leisure activities",
        "hobbies and interests", "interests & activities",
        
        # Spanish
        "intereses", "pasatiempos", "aficiones", "intereses personales",
        "hobbies", "actividades", "intereses y aficiones",
        
        # French
        "centres d'intérêt", "loisirs", "intérêts", "hobbies",
        "activités personnelles", "intérêts personnels",
        
        # German
        "interessen", "hobbys", "freizeitaktivitäten",
        "persönliche interessen", "hobbies und interessen",
        
        # Hindi
        "रुचियां", "शौक", "व्यक्तिगत रुचियां", "गतिविधियां",
        
        # Portuguese
        "interesses", "hobbies", "interesses pessoais", "atividades",
        "hobbies e interesses", "passatempos",
        
        # Italian
        "interessi", "hobby", "interessi personali", "attività",
        "hobby e interessi", "passatempi",
        
        # Chinese
        "兴趣爱好", "个人兴趣", "爱好", "业余活动",
        
        # Japanese
        "趣味", "興味", "趣味・特技", "課外活動"
    ],
    
    "references": [
        # English
        "references", "professional references", "reference",
        "recommendations", "referees", "testimonials",
        "references available upon request", "reference list",
        
        # Spanish
        "referencias", "referencias profesionales", "recomendaciones",
        "referencias laborales", "personas de referencia",
        
        # French
        "références", "références professionnelles", "recommandations",
        "personnes de référence", "références disponibles",
        
        # German
        "referenzen", "berufliche referenzen", "empfehlungen",
        "referenzpersonen", "referenzen auf anfrage",
        
        # Hindi
        "संदर्भ", "व्यावसायिक संदर्भ", "सिफारिशें",
        
        # Portuguese
        "referências", "referências profissionais", "recomendações",
        "referências disponíveis", "pessoas de referência",
        
        # Italian
        "referenze", "referenze professionali", "raccomandazioni",
        "referenze disponibili su richiesta",
        
        # Chinese
        "推荐人", "证明人", "推荐信", "参考人",
        
        # Japanese
        "推薦状", "参照", "推薦者", "照会先"
    ],
    
    "additional": [
        # English - catch-all sections
        "additional information", "additional", "other information",
        "miscellaneous", "other", "extras", "additional details",
        "supplementary information", "further information",
        "other activities", "other qualifications", "additional experience",
        "additional skills", "professional affiliations", "affiliations",
        "memberships", "professional memberships", "associations",
        "professional associations", "organizations",
        
        # Spanish
        "información adicional", "otros", "otra información",
        "información complementaria", "membresías", "afiliaciones",
        
        # French
        "informations complémentaires", "autres informations",
        "divers", "autres", "adhésions", "affiliations",
        
        # German
        "weitere informationen", "sonstiges", "zusätzliche informationen",
        "mitgliedschaften", "verbände",
        
        # Hindi
        "अतिरिक्त जानकारी", "अन्य", "अन्य जानकारी", "सदस्यता",
        
        # Portuguese
        "informações adicionais", "outras informações", "diversos",
        "membros", "afiliações",
        
        # Italian
        "informazioni aggiuntive", "altre informazioni", "varie",
        "appartenenze", "associazioni",
        
        # Chinese
        "其他信息", "附加信息", "其他", "会员资格",
        
        # Japanese
        "その他", "追加情報", "その他の情報", "所属"
    ]
}


_DATE_RANGE_RE = re.compile(
    r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}\b\s*(?:-|–|—|to)\s*\b(?:present|current|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{4}|\d{4})\b",
    re.IGNORECASE,
)
_YEAR_RANGE_RE = re.compile(
    r"\b\d{4}\b\s*(?:-|–|—|to)\s*\b(?:present|current|\d{4})\b",
    re.IGNORECASE,
)
_DEGREE_HINT_RE = re.compile(
    r"\b(bachelor|master|b\.\s?tech|m\.\s?tech|b\.\s?e|m\.\s?e|b\.\s?sc|m\.\s?sc|ph\.?d|mba|associate)\b",
    re.IGNORECASE,
)
_CONTACT_HINT_RE = re.compile(
    r"(@|\b(?:phone|mobile|email|linkedin|github|portfolio)\b|\b\+?\d[\d\s().-]{7,}\b)",
    re.IGNORECASE,
)


HEADER_FALSE_POSITIVE_VERBS = {
    # Development & Creation
    "developed", "developing", "develop", "develops",
    "built", "building", "build", "builds",
    "implemented", "implementing", "implement", "implements",
    "designed", "designing", "design", "designs",
    "created", "creating", "create", "creates",
    "engineered", "engineering", "engineer", "engineers",
    "constructed", "constructing", "construct", "constructs",
    "established", "establishing", "establish", "establishes",
    "founded", "founding", "found", "founds",
    "initiated", "initiating", "initiate", "initiates",
    "launched", "launching", "launch", "launches",
    "pioneered", "pioneering", "pioneer", "pioneers",
    "introduced", "introducing", "introduce", "introduces",
    "invented", "inventing", "invent", "invents",
    "formulated", "formulating", "formulate", "formulates",
    "drafted", "drafting", "draft", "drafts",
    "composed", "composing", "compose", "composes",
    "authored", "authoring", "author", "authors",
    "crafted", "crafting", "craft", "crafts",
    "generated", "generating", "generate", "generates",
    "produced", "producing", "produce", "produces",
    "fabricated", "fabricating", "fabricate", "fabricates",
    
    # Delivery & Completion
    "delivered", "delivering", "deliver", "delivers",
    "completed", "completing", "complete", "completes",
    "finished", "finishing", "finish", "finishes",
    "accomplished", "accomplishing", "accomplish", "accomplishes",
    "achieved", "achieving", "achieve", "achieves",
    "executed", "executing", "execute", "executes",
    "performed", "performing", "perform", "performs",
    "fulfilled", "fulfilling", "fulfill", "fulfills",
    "finalized", "finalizing", "finalize", "finalizes",
    "concluded", "concluding", "conclude", "concludes",
    "wrapped", "wrapping", "wrap", "wraps",
    
    # Optimization & Improvement
    "optimized", "optimizing", "optimize", "optimizes",
    "improved", "improving", "improve", "improves",
    "enhanced", "enhancing", "enhance", "enhances",
    "refined", "refining", "refine", "refines",
    "streamlined", "streamlining", "streamline", "streamlines",
    "modernized", "modernizing", "modernize", "modernizes",
    "upgraded", "upgrading", "upgrade", "upgrades",
    "revamped", "revamping", "revamp", "revamps",
    "restructured", "restructuring", "restructure", "restructures",
    "reorganized", "reorganizing", "reorganize", "reorganizes",
    "transformed", "transforming", "transform", "transforms",
    "revolutionized", "revolutionizing", "revolutionize", "revolutionizes",
    "overhauled", "overhauling", "overhaul", "overhauls",
    "renovated", "renovating", "renovate", "renovates",
    "revitalized", "revitalizing", "revitalize", "revitalizes",
    "strengthened", "strengthening", "strengthen", "strengthens",
    "boosted", "boosting", "boost", "boosts",
    "elevated", "elevating", "elevate", "elevates",
    "advanced", "advancing", "advance", "advances",
    "progressed", "progressing", "progress", "progresses",
    
    # Maintenance & Support
    "maintained", "maintaining", "maintain", "maintains",
    "supported", "supporting", "support", "supports",
    "sustained", "sustaining", "sustain", "sustains",
    "preserved", "preserving", "preserve", "preserves",
    "serviced", "servicing", "service", "services",
    "repaired", "repairing", "repair", "repairs",
    "fixed", "fixing", "fix", "fixes",
    "debugged", "debugging", "debug", "debugs",
    "resolved", "resolving", "resolve", "resolves",
    "troubleshot", "troubleshooting", "troubleshoot", "troubleshoots",
    "remediated", "remediating", "remediate", "remediates",
    "corrected", "correcting", "correct", "corrects",
    "addressed", "addressing", "address", "addresses",
    "patched", "patching", "patch", "patches",
    "updated", "updating", "update", "updates",
    
    # Analysis & Research
    "analyzed", "analyzing", "analyze", "analyzes",
    "assessed", "assessing", "assess", "assesses",
    "evaluated", "evaluating", "evaluate", "evaluates",
    "examined", "examining", "examine", "examines",
    "investigated", "investigating", "investigate", "investigates",
    "researched", "researching", "research", "researches",
    "studied", "studying", "study", "studies",
    "reviewed", "reviewing", "review", "reviews",
    "audited", "auditing", "audit", "audits",
    "inspected", "inspecting", "inspect", "inspects",
    "surveyed", "surveying", "survey", "surveys",
    "explored", "exploring", "explore", "explores",
    "probed", "probing", "probe", "probes",
    "diagnosed", "diagnosing", "diagnose", "diagnoses",
    "identified", "identifying", "identify", "identifies",
    "discovered", "discovering", "discover", "discovers",
    "uncovered", "uncovering", "uncover", "uncovers",
    "detected", "detecting", "detect", "detects",
    "measured", "measuring", "measure", "measures",
    "quantified", "quantifying", "quantify", "quantifies",
    "calculated", "calculating", "calculate", "calculates",
    "computed", "computing", "compute", "computes",
    "determined", "determining", "determine", "determines",
    "interpreted", "interpreting", "interpret", "interprets",
    "validated", "validating", "validate", "validates",
    "verified", "verifying", "verify", "verifies",
    "tested", "testing", "test", "tests",
    
    # Management & Leadership
    "managed", "managing", "manage", "manages",
    "led", "leading", "lead", "leads",
    "directed", "directing", "direct", "directs",
    "supervised", "supervising", "supervise", "supervises",
    "oversaw", "overseeing", "oversee", "oversees",
    "governed", "governing", "govern", "governs",
    "administered", "administering", "administer", "administers",
    "coordinated", "coordinating", "coordinate", "coordinates",
    "orchestrated", "orchestrating", "orchestrate", "orchestrates",
    "organized", "organizing", "organize", "organizes",
    "planned", "planning", "plan", "plans",
    "scheduled", "scheduling", "schedule", "schedules",
    "arranged", "arranging", "arrange", "arranges",
    "delegated", "delegating", "delegate", "delegates",
    "assigned", "assigning", "assign", "assigns",
    "allocated", "allocating", "allocate", "allocates",
    "distributed", "distributing", "distribute", "distributes",
    "controlled", "controlling", "control", "controls",
    "regulated", "regulating", "regulate", "regulates",
    "monitored", "monitoring", "monitor", "monitors",
    "tracked", "tracking", "track", "tracks",
    "oversaw", "overseeing", "oversee", "oversees",
    "commanded", "commanding", "command", "commands",
    "steered", "steering", "steer", "steers",
    "guided", "guiding", "guide", "guides",
    "piloted", "piloting", "pilot", "pilots",
    "chaired", "chairing", "chair", "chairs",
    "presided", "presiding", "preside", "presides",
    "headed", "heading", "head", "heads",
    "ran", "running", "run", "runs",
    "operated", "operating", "operate", "operates",
    "handled", "handling", "handle", "handles",
    
    # Collaboration & Communication
    "collaborated", "collaborating", "collaborate", "collaborates",
    "cooperated", "cooperating", "cooperate", "cooperates",
    "partnered", "partnering", "partner", "partners",
    "teamed", "teaming", "team", "teams",
    "worked", "working", "work", "works",
    "liaised", "liaising", "liaise", "liaises",
    "coordinated", "coordinating", "coordinate", "coordinates",
    "communicated", "communicating", "communicate", "communicates",
    "consulted", "consulting", "consult", "consults",
    "advised", "advising", "advise", "advises",
    "counseled", "counseling", "counsel", "counsels",
    "recommended", "recommending", "recommend", "recommends",
    "suggested", "suggesting", "suggest", "suggests",
    "proposed", "proposing", "propose", "proposes",
    "presented", "presenting", "present", "presents",
    "demonstrated", "demonstrating", "demonstrate", "demonstrates",
    "showcased", "showcasing", "showcase", "showcases",
    "exhibited", "exhibiting", "exhibit", "exhibits",
    "displayed", "displaying", "display", "displays",
    "reported", "reporting", "report", "reports",
    "briefed", "briefing", "brief", "briefs",
    "informed", "informing", "inform", "informs",
    "notified", "notifying", "notify", "notifies",
    "alerted", "alerting", "alert", "alerts",
    "apprised", "apprising", "apprise", "apprises",
    "updated", "updating", "update", "updates",
    "conveyed", "conveying", "convey", "conveys",
    "articulated", "articulating", "articulate", "articulates",
    "expressed", "expressing", "express", "expresses",
    "shared", "sharing", "share", "shares",
    "disseminated", "disseminating", "disseminate", "disseminates",
    "published", "publishing", "publish", "publishes",
    "broadcasted", "broadcasting", "broadcast", "broadcasts",
    "announced", "announcing", "announce", "announces",
    "proclaimed", "proclaiming", "proclaim", "proclaims",
    "declared", "declaring", "declare", "declares",
    
    # Training & Development
    "trained", "training", "train", "trains",
    "coached", "coaching", "coach", "coaches",
    "mentored", "mentoring", "mentor", "mentors",
    "taught", "teaching", "teach", "teaches",
    "educated", "educating", "educate", "educates",
    "instructed", "instructing", "instruct", "instructs",
    "tutored", "tutoring", "tutor", "tutors",
    "guided", "guiding", "guide", "guides",
    "developed", "developing", "develop", "develops",
    "cultivated", "cultivating", "cultivate", "cultivates",
    "nurtured", "nurturing", "nurture", "nurtures",
    "fostered", "fostering", "foster", "fosters",
    "grew", "growing", "grow", "grows",
    "expanded", "expanding", "expand", "expands",
    "broadened", "broadening", "broaden", "broadens",
    "enriched", "enriching", "enrich", "enriches",
    "empowered", "empowering", "empower", "empowers",
    "enabled", "enabling", "enable", "enables",
    "equipped", "equipping", "equip", "equips",
    "prepared", "preparing", "prepare", "prepares",
    "groomed", "grooming", "groom", "grooms",
    "shaped", "shaping", "shape", "shapes",
    "molded", "molding", "mold", "molds",
    "influenced", "influencing", "influence", "influences",
    "inspired", "inspiring", "inspire", "inspires",
    "motivated", "motivating", "motivate", "motivates",
    "encouraged", "encouraging", "encourage", "encourages",
    "stimulated", "stimulating", "stimulate", "stimulates",
    "energized", "energizing", "energize", "energizes",
    
    # Sales & Business Development
    "sold", "selling", "sell", "sells",
    "marketed", "marketing", "market", "markets",
    "promoted", "promoting", "promote", "promotes",
    "pitched", "pitching", "pitch", "pitches",
    "negotiated", "negotiating", "negotiate", "negotiates",
    "closed", "closing", "close", "closes",
    "secured", "securing", "secure", "secures",
    "acquired", "acquiring", "acquire", "acquires",
    "obtained", "obtaining", "obtain", "obtains",
    "procured", "procuring", "procure", "procures",
    "won", "winning", "win", "wins",
    "captured", "capturing", "capture", "captures",
    "attracted", "attracting", "attract", "attracts",
    "retained", "retaining", "retain", "retains",
    "converted", "converting", "convert", "converts",
    "engaged", "engaging", "engage", "engages",
    "cultivated", "cultivating", "cultivate", "cultivates",
    "nurtured", "nurturing", "nurture", "nurtures",
    "expanded", "expanding", "expand", "expands",
    "penetrated", "penetrating", "penetrate", "penetrates",
    "targeted", "targeting", "target", "targets",
    "prospected", "prospecting", "prospect", "prospects",
    "qualified", "qualifying", "qualify", "qualifies",
    "canvassed", "canvassing", "canvass", "canvasses",
    "sourced", "sourcing", "source", "sources",
    
    # Financial & Quantitative
    "increased", "increasing", "increase", "increases",
    "decreased", "decreasing", "decrease", "decreases",
    "reduced", "reducing", "reduce", "reduces",
    "saved", "saving", "save", "saves",
    "generated", "generating", "generate", "generates",
    "earned", "earning", "earn", "earns",
    "gained", "gaining", "gain", "gains",
    "profited", "profiting", "profit", "profits",
    "grew", "growing", "grow", "grows",
    "expanded", "expanding", "expand", "expands",
    "scaled", "scaling", "scale", "scales",
    "multiplied", "multiplying", "multiply", "multiplies",
    "doubled", "doubling", "double", "doubles",
    "tripled", "tripling", "triple", "triples",
    "maximized", "maximizing", "maximize", "maximizes",
    "minimized", "minimizing", "minimize", "minimizes",
    "cut", "cutting", "cuts",
    "slashed", "slashing", "slash", "slashes",
    "trimmed", "trimming", "trim", "trims",
    "lowered", "lowering", "lower", "lowers",
    "raised", "raising", "raise", "raises",
    "boosted", "boosting", "boost", "boosts",
    "accelerated", "accelerating", "accelerate", "accelerates",
    "expedited", "expediting", "expedite", "expedites",
    "surpassed", "surpassing", "surpass", "surpasses",
    "exceeded", "exceeding", "exceed", "exceeds",
    "outperformed", "outperforming", "outperform", "outperforms",
    "beat", "beating", "beats",
    
    # Integration & Implementation
    "integrated", "integrating", "integrate", "integrates",
    "incorporated", "incorporating", "incorporate", "incorporates",
    "merged", "merging", "merge", "merges",
    "combined", "combining", "combine", "combines",
    "unified", "unifying", "unify", "unifies",
    "consolidated", "consolidating", "consolidate", "consolidates",
    "synthesized", "synthesizing", "synthesize", "synthesizes",
    "amalgamated", "amalgamating", "amalgamate", "amalgamates",
    "blended", "blending", "blend", "blends",
    "fused", "fusing", "fuse", "fuses",
    "connected", "connecting", "connect", "connects",
    "linked", "linking", "link", "links",
    "joined", "joining", "join", "joins",
    "coupled", "coupling", "couple", "couples",
    "attached", "attaching", "attach", "attaches",
    "associated", "associating", "associate", "associates",
    "interfaced", "interfacing", "interface", "interfaces",
    "bridged", "bridging", "bridge", "bridges",
    "synchronized", "synchronizing", "synchronize", "synchronizes",
    "aligned", "aligning", "align", "aligns",
    "harmonized", "harmonizing", "harmonize", "harmonizes",
    
    # Documentation & Recording
    "documented", "documenting", "document", "documents",
    "recorded", "recording", "record", "records",
    "logged", "logging", "log", "logs",
    "catalogued", "cataloguing", "catalogue", "catalogues",
    "archived", "archiving", "archive", "archives",
    "registered", "registering", "register", "registers",
    "filed", "filing", "file", "files",
    "noted", "noting", "note", "notes",
    "chronicled", "chronicling", "chronicle", "chronicles",
    "transcribed", "transcribing", "transcribe", "transcribes",
    "captured", "capturing", "capture", "captures",
    "compiled", "compiling", "compile", "compiles",
    "collected", "collecting", "collect", "collects",
    "gathered", "gathering", "gather", "gathers",
    "assembled", "assembling", "assemble", "assembles",
    "aggregated", "aggregating", "aggregate", "aggregates",
    "accumulated", "accumulating", "accumulate", "accumulates",
    "amassed", "amassing", "amass", "amasses",
    "cataloged", "cataloging", "catalog", "catalogs",
    "indexed", "indexing", "index", "indexes",
    "classified", "classifying", "classify", "classifies",
    "categorized", "categorizing", "categorize", "categorizes",
    "sorted", "sorting", "sort", "sorts",
    "organized", "organizing", "organize", "organizes",
    "systematized", "systematizing", "systematize", "systematizes",
    
    # Deployment & Distribution
    "deployed", "deploying", "deploy", "deploys",
    "distributed", "distributing", "distribute", "distributes",
    "dispersed", "dispersing", "disperse", "disperses",
    "disseminated", "disseminating", "disseminate", "disseminates",
    "circulated", "circulating", "circulate", "circulates",
    "propagated", "propagating", "propagate", "propagates",
    "spread", "spreading", "spreads",
    "rolled", "rolling", "roll", "rolls",
    "released", "releasing", "release", "releases",
    "shipped", "shipping", "ship", "ships",
    "pushed", "pushing", "push", "pushes",
    "published", "publishing", "publish", "publishes",
    "issued", "issuing", "issue", "issues",
    "delivered", "delivering", "deliver", "delivers",
    "dispatched", "dispatching", "dispatch", "dispatches",
    "transmitted", "transmitting", "transmit", "transmits",
    "transferred", "transferring", "transfer", "transfers",
    "moved", "moving", "move", "moves",
    "migrated", "migrating", "migrate", "migrates",
    "ported", "porting", "port", "ports",
    "relocated", "relocating", "relocate", "relocates",
    
    # Compliance & Quality
    "ensured", "ensuring", "ensure", "ensures",
    "guaranteed", "guaranteeing", "guarantee", "guarantees",
    "certified", "certifying", "certify", "certifies",
    "approved", "approving", "approve", "approves",
    "authorized", "authorizing", "authorize", "authorizes",
    "sanctioned", "sanctioning", "sanction", "sanctions",
    "validated", "validating", "validate", "validates",
    "verified", "verifying", "verify", "verifies",
    "authenticated", "authenticating", "authenticate", "authenticates",
    "confirmed", "confirming", "confirm", "confirms",
    "substantiated", "substantiating", "substantiate", "substantiates",
    "corroborated", "corroborating", "corroborate", "corroborates",
    "attested", "attesting", "attest", "attests",
    "vouched", "vouching", "vouch", "vouches",
    "endorsed", "endorsing", "endorse", "endorses",
    "ratified", "ratifying", "ratify", "ratifies",
    "standardized", "standardizing", "standardize", "standardizes",
    "normalized", "normalizing", "normalize", "normalizes",
    "regulated", "regulating", "regulate", "regulates",
    "enforced", "enforcing", "enforce", "enforces",
    "policed", "policing", "police", "polices",
    "complied", "complying", "comply", "complies",
    "adhered", "adhering", "adhere", "adheres",
    "conformed", "conforming", "conform", "conforms",
    "followed", "following", "follow", "follows",
    "observed", "observing", "observe", "observes",
    "obeyed", "obeying", "obey", "obeys",
    "respected", "respecting", "respect", "respects",
    "honored", "honoring", "honor", "honors",
    
    # Prevention & Protection
    "prevented", "preventing", "prevent", "prevents",
    "protected", "protecting", "protect", "protects",
    "safeguarded", "safeguarding", "safeguard", "safeguards",
    "secured", "securing", "secure", "secures",
    "shielded", "shielding", "shield", "shields",
    "defended", "defending", "defend", "defends",
    "guarded", "guarding", "guard", "guards",
    "preserved", "preserving", "preserve", "preserves",
    "maintained", "maintaining", "maintain", "maintains",
    "sustained", "sustaining", "sustain", "sustains",
    "mitigated", "mitigating", "mitigate", "mitigates",
    "minimized", "minimizing", "minimize", "minimizes",
    "reduced", "reducing", "reduce", "reduces",
    "eliminated", "eliminating", "eliminate", "eliminates",
    "removed", "removing", "remove", "removes",
    "eradicated", "eradicating", "eradicate", "eradicates",
    "avoided", "avoiding", "avoid", "avoids",
    "circumvented", "circumventing", "circumvent", "circumvents",
    "averted", "averting", "avert", "averts",
    "forestalled", "forestalling", "forestall", "forestalls",
    "thwarted", "thwarting", "thwart", "thwarts",
    "blocked", "blocking", "block", "blocks",
    "stopped", "stopping", "stop", "stops",
    "halted", "halting", "halt", "halts",
    "ceased", "ceasing", "cease", "ceases",
    
    # Automation & Efficiency
    "automated", "automating", "automate", "automates",
    "mechanized", "mechanizing", "mechanize", "mechanizes",
    "digitized", "digitizing", "digitize", "digitizes",
    "computerized", "computerizing", "computerize", "computerizes",
    "systematized", "systematizing", "systematize", "systematizes",
    "rationalized", "rationalizing", "rationalize", "rationalizes",
    "expedited", "expediting", "expedite", "expedites",
    "accelerated", "accelerating", "accelerate", "accelerates",
    "hastened", "hastening", "hasten", "hastens",
    "quickened", "quickening", "quicken", "quickens",
    "sped", "speeding", "speed", "speeds",
    "facilitated", "facilitating", "facilitate", "facilitates",
    "eased", "easing", "ease", "eases",
    "simplified", "simplifying", "simplify", "simplifies",
    "clarified", "clarifying", "clarify", "clarifies",
    "demystified", "demystifying", "demystify", "demystifies",
    "illuminated", "illuminating", "illuminate", "illuminates",
    "elucidated", "elucidating", "elucidate", "elucidates",
    "explained", "explaining", "explain", "explains",
    
    # Influence & Persuasion
    "influenced", "influencing", "influence", "influences",
    "persuaded", "persuading", "persuade", "persuades",
    "convinced", "convincing", "convince", "convinces",
    "swayed", "swaying", "sway", "sways",
    "lobbied", "lobbying", "lobby", "lobbies",
    "advocated", "advocating", "advocate", "advocates",
    "championed", "championing", "champion", "champions",
    "promoted", "promoting", "promote", "promotes",
    "supported", "supporting", "support", "supports",
    "backed", "backing", "back", "backs",
    "endorsed", "endorsing", "endorse", "endorses",
    "sponsored", "sponsoring", "sponsor", "sponsors",
    "rallied", "rallying", "rally", "rallies",
    "mobilized", "mobilizing", "mobilize", "mobilizes",
    "galvanized", "galvanizing", "galvanize", "galvanizes",
    "activated", "activating", "activate", "activates",
    "stimulated", "stimulating", "stimulate", "stimulates",
    "provoked", "provoking", "provoke", "provokes",
    "incited", "inciting", "incite", "incites",
    "instigated", "instigating", "instigate", "instigates",
    "sparked", "sparking", "spark", "sparks",
    "triggered", "triggering", "trigger", "triggers",
    "catalyzed", "catalyzing", "catalyze", "catalyzes",
    
    # Customization & Configuration
    "customized", "customizing", "customize", "customizes",
    "configured", "configuring", "configure", "configures",
    "tailored", "tailoring", "tailor", "tailors",
    "adapted", "adapting", "adapt", "adapts",
    "adjusted", "adjusting", "adjust", "adjusts",
    "modified", "modifying", "modify", "modifies",
    "altered", "altering", "alter", "alters",
    "changed", "changing", "change", "changes",
    "revised", "revising", "revise", "revises",
    "amended", "amending", "amend", "amends",
    "edited", "editing", "edit", "edits",
    "refined", "refining", "refine", "refines",
    "tuned", "tuning", "tune", "tunes",
    "calibrated", "calibrating", "calibrate", "calibrates",
    "tweaked", "tweaking", "tweak", "tweaks",
    "personalized", "personalizing", "personalize", "personalizes",
    "individualized", "individualizing", "individualize", "individualizes",
    "specialized", "specializing", "specialize", "specializes",
    "particularized", "particularizing", "particularize", "particularizes",
}

SECTION_REGEX: dict[str, re.Pattern[str]] = {
    key: re.compile(
        r"^\s*[^A-Za-z0-9]*?(?:"
        + "|".join(re.escape(alias) for alias in aliases)
        + r")\s*[^A-Za-z0-9]*$",
        re.IGNORECASE,
    )
    for key, aliases in SECTION_ALIASES.items()
}


# KEYWORD_HINTS: dict[str, list[str]] = {
#     "experience": [
#         "company",
#         "employer",
#         "responsibilities",
#         "role",
#         "duration",
#         "project",
#         "client",
#     ],
#     "education": ["university", "college", "degree", "gpa", "b.sc", "m.sc"],
#     "skills": ["python", "java", "sql", "aws", "docker", "kubernetes"],
#     "certifications": ["certified", "license", "certification"],
#     "projects": ["project", "built", "developed", "implemented"],
#     "awards": ["award", "honor", "achievement"],
#     "languages": ["english", "spanish", "french", "german", "hindi"],
#     "publications": ["publication", "paper", "journal", "patent"],
# }


KEYWORD_HINTS: dict[str, list[str]] = {
    "experience": [
        # Job titles and positions
        "company", "employer", "responsibilities", "role", "duration", "project", "client",
        "position", "job", "work", "employment", "professional", "career", "tenure",
        "title", "designation", "occupation", "posting", "assignment", "placement",
        
        # Action verbs
        "worked", "served", "managed", "led", "supervised", "coordinated", "executed",
        "directed", "administered", "spearheaded", "orchestrated", "oversaw", "governed",
        "facilitated", "championed", "pioneered", "initiated", "launched", "established",
        "developed", "designed", "created", "built", "implemented", "deployed",
        "engineered", "architected", "programmed", "coded", "maintained", "optimized",
        "streamlined", "automated", "integrated", "migrated", "upgraded", "enhanced",
        "improved", "increased", "reduced", "decreased", "saved", "generated",
        "achieved", "delivered", "completed", "accomplished", "attained", "exceeded",
        "collaborated", "partnered", "cooperated", "liaised", "communicated", "presented",
        "trained", "mentored", "coached", "guided", "taught", "educated",
        "analyzed", "evaluated", "assessed", "researched", "investigated", "identified",
        "resolved", "troubleshot", "debugged", "fixed", "remediated", "mitigated",
        "negotiated", "persuaded", "influenced", "advocated", "consulted", "advised",
        
        # Organization types
        "organization", "firm", "corporation", "enterprise", "startup", "agency",
        "institution", "establishment", "business", "venture", "conglomerate",
        "multinational", "fortune 500", "sme", "unicorn", "scaleup", "fintech",
        "saas", "b2b", "b2c", "e-commerce", "consulting", "outsourcing",
        
        # Employment types
        "full-time", "part-time", "contract", "freelance", "consultant", "intern",
        "internship", "co-op", "temporary", "permanent", "seasonal", "remote",
        "hybrid", "on-site", "virtual", "telecommute", "contractor", "employee",
        
        # Organizational structure
        "team", "department", "division", "unit", "group", "squad", "pod",
        "cross-functional", "multidisciplinary", "agile team", "scrum team",
        "reports to", "direct reports", "dotted line", "stakeholders", "matrix",
        
        # Achievements and metrics
        "accomplishments", "achievements", "contributions", "impact", "results",
        "kpi", "metrics", "roi", "revenue", "profit", "growth", "scale",
        "performance", "productivity", "efficiency", "effectiveness", "quality",
        "customer satisfaction", "user engagement", "conversion rate", "retention",
        
        # Time indicators
        "present", "current", "ongoing", "to date", "since", "from", "until",
        "years", "months", "quarters", "yrs", "mos", "tenure of", "duration of",
        
        # Industry specific
        "industry", "sector", "domain", "vertical", "market", "field",
        "technology", "healthcare", "finance", "retail", "manufacturing",
        "telecommunications", "automotive", "aerospace", "energy", "pharmaceuticals"
    ],
    
    "education": [
        # Degrees
        "university", "college", "degree", "gpa", "b.sc", "m.sc",
        "bachelor", "master", "phd", "doctorate", "mba", "b.tech", "m.tech",
        "b.e", "m.e", "b.a", "m.a", "b.com", "m.com", "bba", "mca", "bca",
        "llb", "llm", "md", "mbbs", "dds", "pharmd", "jd", "ed.d",
        "undergraduate", "graduate", "postgraduate", "diploma", "associate",
        "advanced diploma", "post-doctoral", "postdoc", "fellow", "resident",
        
        # Academic achievements
        "honors", "cum laude", "magna cum laude", "summa cum laude", "dean's list",
        "distinction", "high distinction", "first class", "second class", "third class",
        "honors degree", "honours", "with distinction", "merit", "pass with merit",
        
        # GPA variations
        "cgpa", "percentage", "grade point average", "cumulative gpa", "major gpa",
        "out of 4.0", "out of 10", "percentile", "class rank", "top", "percent",
        
        # Fields of study
        "major", "minor", "concentration", "specialization", "coursework", "focus",
        "emphasis", "track", "stream", "branch", "discipline", "subject area",
        "computer science", "engineering", "business", "economics", "mathematics",
        "physics", "chemistry", "biology", "medicine", "law", "arts", "humanities",
        
        # Academic work
        "thesis", "dissertation", "capstone", "research project", "final year project",
        "senior project", "independent study", "research paper", "publication",
        
        # Time references
        "graduated", "studied", "attended", "completed", "earned", "received",
        "expected", "pursuing", "in progress", "candidate for", "graduating",
        "semester", "trimester", "quarter", "year", "academic year",
        
        # Institutions
        "academic", "institution", "school", "academy", "institute", "conservatory",
        "polytechnic", "technical school", "community college", "junior college",
        "state university", "private university", "public university", "ivy league",
        
        # Additional qualifications
        "certification", "certificate program", "professional development",
        "continuing education", "executive education", "online course", "mooc",
        "bootcamp", "training program", "workshop", "seminar", "short course",
        
        # International variations
        "a-levels", "o-levels", "gcse", "baccalaureate", "abitur", "leaving cert",
        "higher secondary", "intermediate", "matriculation", "10th grade", "12th grade"
    ],
    
    "skills": [
        # Programming languages
        "python", "java", "javascript", "typescript", "c++", "c#", "c", "golang", "go",
        "rust", "ruby", "php", "swift", "kotlin", "objective-c", "scala", "perl",
        "r", "matlab", "julia", "dart", "elixir", "haskell", "clojure", "erlang",
        "vb.net", "visual basic", "cobol", "fortran", "assembly", "lua", "groovy",
        
        # Frontend technologies
        "react", "angular", "vue", "vue.js", "svelte", "ember", "backbone",
        "jquery", "next.js", "nuxt.js", "gatsby", "remix", "astro", "qwik",
        "html", "html5", "css", "css3", "sass", "scss", "less", "stylus",
        "bootstrap", "tailwind", "tailwindcss", "material-ui", "mui", "chakra ui",
        "ant design", "semantic ui", "bulma", "foundation", "styled-components",
        "webpack", "vite", "parcel", "rollup", "gulp", "grunt", "babel",
        
        # Backend technologies
        "nodejs", "node.js", "express", "fastify", "koa", "nestjs", "hapi",
        "django", "flask", "fastapi", "pyramid", "tornado", "bottle",
        "spring", "spring boot", "hibernate", "struts", "jsf", "grails",
        "rails", "ruby on rails", "sinatra", "laravel", "symfony", "codeigniter",
        "asp.net", ".net core", "wcf", "web api", "blazor", "razor",
        
        # Databases
        "sql", "mysql", "postgresql", "postgres", "sqlite", "mariadb", "oracle",
        "sql server", "mssql", "db2", "sybase", "teradata", "snowflake",
        "mongodb", "cassandra", "couchdb", "couchbase", "redis", "memcached",
        "dynamodb", "cosmosdb", "firestore", "firebase", "realm", "neo4j",
        "elasticsearch", "solr", "influxdb", "timescaledb", "clickhouse",
        "database design", "data modeling", "orm", "sequelize", "sqlalchemy",
        "prisma", "typeorm", "mongoose", "entity framework", "dapper",
        
        # Cloud platforms
        "aws", "amazon web services", "ec2", "s3", "lambda", "rds", "dynamodb",
        "cloudformation", "cloudfront", "route53", "vpc", "iam", "cognito",
        "azure", "microsoft azure", "azure devops", "azure functions", "blob storage",
        "gcp", "google cloud", "google cloud platform", "compute engine", "app engine",
        "cloud run", "cloud functions", "bigquery", "cloud storage", "firebase",
        "heroku", "digitalocean", "linode", "vultr", "ibm cloud", "oracle cloud",
        "alibaba cloud", "tencent cloud", "cloudflare", "vercel", "netlify",
        
        # DevOps and tools
        "docker", "kubernetes", "k8s", "containerization", "podman", "containerd",
        "terraform", "ansible", "puppet", "chef", "saltstack", "pulumi",
        "jenkins", "gitlab ci", "github actions", "circleci", "travis ci", "bamboo",
        "ci/cd", "continuous integration", "continuous deployment", "continuous delivery",
        "git", "github", "gitlab", "bitbucket", "svn", "mercurial", "perforce",
        "jira", "confluence", "trello", "asana", "monday.com", "notion",
        "agile", "scrum", "kanban", "lean", "safe", "devops", "sre", "itil",
        "prometheus", "grafana", "datadog", "new relic", "splunk", "elk stack",
        "nagios", "zabbix", "pagerduty", "opsgenie", "sentry", "rollbar",
        
        # AI/ML/Data Science
        "machine learning", "deep learning", "artificial intelligence", "ai", "ml",
        "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "bokeh",
        "jupyter", "notebook", "colab", "kaggle", "hugging face", "transformers",
        "nlp", "natural language processing", "computer vision", "cv", "opencv",
        "yolo", "rcnn", "gan", "reinforcement learning", "neural networks",
        "convolutional neural networks", "cnn", "rnn", "lstm", "gru", "bert",
        "gpt", "llm", "large language models", "fine-tuning", "transfer learning",
        
        # Big Data
        "spark", "apache spark", "pyspark", "hadoop", "mapreduce", "hdfs",
        "kafka", "apache kafka", "flink", "storm", "hive", "pig", "hbase",
        "airflow", "luigi", "prefect", "dagster", "dbt", "etl", "elt",
        "data pipeline", "data engineering", "data warehousing", "data lake",
        
        # Mobile development
        "ios", "android", "react native", "flutter", "xamarin", "ionic",
        "swift", "swiftui", "objective-c", "kotlin", "java android", "jetpack compose",
        "mobile development", "app development", "mobile apps", "native apps",
        
        # Web technologies
        "rest", "restful", "api", "graphql", "grpc", "soap", "websocket",
        "microservices", "serverless", "service mesh", "istio", "linkerd",
        "oauth", "jwt", "saml", "openid", "authentication", "authorization",
        "nginx", "apache", "httpd", "tomcat", "iis", "load balancing",
        "reverse proxy", "cdn", "content delivery network", "caching",
        
        # Testing
        "testing", "test automation", "junit", "testng", "pytest", "unittest",
        "selenium", "cypress", "playwright", "puppeteer", "webdriver", "appium",
        "jest", "mocha", "chai", "jasmine", "karma", "vitest", "testing library",
        "tdd", "test-driven development", "bdd", "behavior-driven development",
        "integration testing", "unit testing", "e2e", "end-to-end testing",
        "load testing", "performance testing", "jmeter", "gatling", "locust",
        
        # Operating Systems
        "linux", "unix", "ubuntu", "debian", "centos", "rhel", "fedora", "arch",
        "macos", "windows", "windows server", "bash", "shell", "powershell",
        "command line", "terminal", "cli", "scripting", "automation",
        
        # Security
        "security", "cybersecurity", "infosec", "appsec", "devsecops", "penetration testing",
        "vulnerability assessment", "owasp", "ssl", "tls", "encryption", "cryptography",
        "firewall", "waf", "ids", "ips", "siem", "zero trust", "vpn",
        
        # Other technical skills
        "blockchain", "ethereum", "solidity", "web3", "cryptocurrency", "bitcoin",
        "iot", "internet of things", "embedded systems", "raspberry pi", "arduino",
        "game development", "unity", "unreal engine", "godot", "3d modeling",
        "blender", "maya", "autocad", "solidworks", "cad", "photoshop",
        "illustrator", "figma", "sketch", "adobe xd", "ui design", "ux design",
        "responsive design", "accessibility", "wcag", "seo", "sem", "analytics",
        "google analytics", "tag manager", "a/b testing", "conversion optimization",
        
        # Soft skill indicators in technical context
        "proficient", "experienced", "expertise", "expert", "knowledge", "familiar",
        "skilled", "advanced", "intermediate", "beginner", "working knowledge",
        "technical skills", "programming", "frameworks", "libraries", "tools",
        "technologies", "platforms", "systems", "applications", "solutions"
    ],
    
    "certifications": [
        # General terms
        "certified", "certification", "certificate", "license", "credential",
        "accreditation", "qualified", "professional", "chartered", "fellow",
        
        # Cloud certifications
        "aws certified", "solutions architect", "developer associate", "sysops",
        "cloud practitioner", "devops engineer", "security specialty", "advanced networking",
        "azure certified", "azure fundamentals", "azure administrator", "azure developer",
        "azure solutions architect", "azure devops engineer", "azure security engineer",
        "gcp certified", "associate cloud engineer", "professional cloud architect",
        "professional data engineer", "professional cloud developer",
        
        # IT certifications
        "cisco", "ccna", "ccnp", "ccie", "ccent", "devnet", "cyberops",
        "comptia", "a+", "network+", "security+", "linux+", "cloud+", "project+",
        "itil", "itil foundation", "itil practitioner", "itil expert", "itil master",
        "prince2", "pmp", "capm", "prince2 foundation", "prince2 practitioner",
        
        # Kubernetes and containers
        "kubernetes certified", "cka", "certified kubernetes administrator",
        "ckad", "certified kubernetes application developer", "cks", "kubernetes security",
        "docker certified", "terraform certified", "hashicorp certified",
        
        # Security certifications
        "cissp", "certified information systems security professional",
        "ceh", "certified ethical hacker", "oscp", "offensive security",
        "cism", "certified information security manager",
        "cisa", "certified information systems auditor",
        "crisc", "cgeit", "gsec", "giac", "sans", "comptia security+",
        
        # Development certifications
        "oracle certified", "java programmer", "java developer", "java architect",
        "ocp", "oca", "ocm", "mysql", "database administrator",
        "microsoft certified", "mcsa", "mcse", "mcsd", "mta", "azure certified",
        "google certified", "professional cloud developer", "associate android developer",
        "red hat certified", "rhcsa", "rhce", "rhca", "ansible automation",
        
        # Data and analytics
        "google data analytics", "google data engineer", "aws big data",
        "databricks certified", "cloudera certified", "hortonworks certified",
        "tableau certified", "power bi certified", "qlik certified",
        "sas certified", "certified analytics professional", "cap",
        
        # Project management
        "pmp", "project management professional", "capm", "certified associate",
        "scrum master", "csm", "certified scrum master", "psm", "professional scrum master",
        "pspo", "product owner", "cspo", "safe", "safe agilist", "safe scrum master",
        "safe practitioner", "pmi-acp", "agile certified practitioner",
        
        # Business and finance
        "cpa", "certified public accountant", "cfa", "chartered financial analyst",
        "frm", "financial risk manager", "caia", "chartered alternative investment",
        "cma", "certified management accountant", "cia", "certified internal auditor",
        "six sigma", "green belt", "black belt", "lean", "lean six sigma",
        
        # Sales and marketing
        "hubspot certified", "google ads", "google analytics", "facebook blueprint",
        "salesforce certified", "administrator", "developer", "consultant",
        "marketo certified", "hootsuite certified", "semrush certified",
        
        # Other professional certifications
        "togaf", "zachman", "enterprise architecture", "cobit", "cgeit",
        "pegasystems", "pega", "servicenow", "workday", "sap certified",
        
        # Status indicators
        "issued by", "issuing organization", "credential id", "license number",
        "expires", "expiration", "valid", "valid through", "renewed", "active",
        "in progress", "pursuing", "expected", "anticipated completion"
    ],
    
    "projects": [
        # Project types
        "project", "portfolio project", "personal project", "academic project",
        "capstone", "thesis project", "research project", "final year project",
        "side project", "open source", "open source project", "contribution",
        "freelance project", "client project", "professional project", "commercial project",
        
        # Action verbs
        "built", "developed", "created", "designed", "implemented", "deployed",
        "engineered", "architected", "constructed", "established", "launched",
        "delivered", "completed", "contributed", "collaborated", "participated",
        "led", "managed", "coordinated", "supervised", "directed", "spearheaded",
        
        # Project deliverables
        "application", "app", "system", "platform", "tool", "solution", "product",
        "website", "web application", "mobile app", "mobile application", "desktop app",
        "software", "program", "utility", "service", "api", "microservice",
        "prototype", "proof of concept", "poc", "mvp", "minimum viable product",
        "dashboard", "portal", "interface", "frontend", "backend", "full-stack",
        
        # Development aspects
        "features", "functionality", "capabilities", "modules", "components",
        "integration", "third-party integration", "api integration", "payment integration",
        "optimization", "performance optimization", "code optimization", "refactoring",
        "migration", "data migration", "cloud migration", "modernization",
        "automation", "automated", "scripting", "workflow automation",
        
        # Technologies and tools
        "technologies used", "tech stack", "technology stack", "built with",
        "framework", "library", "database", "frontend framework", "backend framework",
        "programming language", "cloud platform", "hosting", "deployment",
        
        # Project scale and impact
        "users", "active users", "downloads", "installations", "traffic",
        "scale", "performance", "scalability", "availability", "reliability",
        "metrics", "kpi", "impact", "results", "outcome", "achievements",
        
        # Collaboration
        "team project", "group project", "collaborative project", "pair programming",
        "collaborated on", "worked with", "partnered with", "contributed to",
        "maintained", "maintaining", "maintainer", "contributor", "co-creator",
        
        # Source code
        "github", "gitlab", "bitbucket", "repository", "repo", "codebase",
        "source code", "code", "open source", "public repository", "private repository",
        "fork", "forked", "pull request", "pr", "commit", "contribution",
        
        # Documentation
        "documented", "documentation", "readme", "wiki", "user guide",
        "technical documentation", "api documentation", "specifications",
        
        # Project status
        "completed", "ongoing", "in progress", "active", "maintained",
        "deprecated", "archived", "live", "production", "deployed", "published"
    ],
    
    "awards": [
        # General terms
        "award", "awards", "honor", "honors", "achievement", "achievements",
        "recognition", "recognitions", "prize", "prizes", "distinction", "distinctions",
        "accolade", "accolades", "commendation", "commendations", "decoration",
        
        # Academic awards
        "scholarship", "scholarships", "fellowship", "fellowships", "grant", "grants",
        "dean's list", "honor roll", "president's list", "academic excellence",
        "merit scholarship", "need-based scholarship", "full scholarship", "partial scholarship",
        "tuition waiver", "stipend", "research grant", "teaching assistantship",
        
        # Performance awards
        "employee of the month", "employee of the year", "team member of the month",
        "best performer", "top performer", "outstanding performer", "star performer",
        "exceeds expectations", "performance excellence", "quarterly award",
        "annual award", "spot award", "instant recognition", "peer recognition",
        
        # Achievement levels
        "winner", "first place", "second place", "third place", "runner-up",
        "finalist", "semifinalist", "quarterfinalist", "champion", "gold medal",
        "silver medal", "bronze medal", "platinum", "gold", "silver", "bronze",
        "best", "top", "leading", "outstanding", "exceptional", "excellent",
        
        # Competition awards
        "hackathon", "hackathon winner", "coding competition", "programming contest",
        "innovation challenge", "startup competition", "pitch competition",
        "case competition", "business plan competition", "design competition",
        "data science competition", "kaggle competition", "topcoder",
        
        # Professional awards
        "professional of the year", "industry award", "lifetime achievement",
        "innovation award", "excellence award", "leadership award", "mentor award",
        "customer service award", "sales achievement", "quota attainment",
        "president's club", "circle of excellence", "hall of fame",
        
        # Project and innovation awards
        "innovation", "innovator", "patent award", "invention", "breakthrough",
        "best project", "project of the year", "best paper", "best presentation",
        "best poster", "people's choice", "audience choice", "judge's choice",
        
        # Quality and service awards
        "quality award", "quality excellence", "zero defects", "six sigma",
        "customer satisfaction", "customer delight", "service excellence",
        "on-time delivery", "on-budget delivery", "efficiency award",
        
        # Status verbs
        "honored", "recognized", "awarded", "received", "earned", "achieved",
        "won", "selected", "chosen", "nominated", "finalist for", "recipient of",
        "conferred", "bestowed", "granted", "presented", "given",
        
        # Physical awards
        "medal", "trophy", "certificate", "plaque", "ribbon", "badge",
        "certificate of achievement", "certificate of excellence", "certificate of merit",
        "letter of commendation", "letter of appreciation", "citation",
        
        # Monetary awards
        "cash prize", "monetary award", "bonus", "incentive", "reward",
        "prize money", "grant funding", "seed funding", "prize fund"
    ],
    
    "languages": [
        # Major world languages
        "english", "mandarin", "chinese", "spanish", "hindi", "arabic",
        "bengali", "portuguese", "russian", "japanese", "punjabi", "german",
        "javanese", "wu", "malay", "telugu", "vietnamese", "korean", "french",
        "marathi", "tamil", "urdu", "turkish", "italian", "thai", "gujarati",
        
        # European languages
        "dutch", "polish", "ukrainian", "romanian", "greek", "czech", "swedish",
        "hungarian", "portuguese", "catalan", "finnish", "danish", "norwegian",
        "slovak", "irish", "croatian", "bulgarian", "lithuanian", "slovenian",
        
        # Asian languages
        "indonesian", "tagalog", "persian", "farsi", "kannada", "malayalam",
        "burmese", "nepali", "sinhalese", "khmer", "lao", "tibetan", "mongolian",
        "kazakh", "uzbek", "azerbaijani", "georgian", "armenian", "kurdish",
        
        # Middle Eastern and African languages
        "hebrew", "amharic", "tigrinya", "somali", "swahili", "yoruba",
        "igbo", "hausa", "zulu", "xhosa", "afrikaans", "berber", "pashto",
        
        # Other languages
        "latin", "sanskrit", "esperanto", "sign language", "asl", "bsl",
        "american sign language", "british sign language", "body language",
        
        # Proficiency levels
        "native", "native speaker", "native proficiency", "mother tongue", "first language",
        "bilingual", "multilingual", "polyglot", "trilingual", "quadrilingual",
        "fluent", "fluency", "near-native", "proficient", "proficiency",
        "advanced", "upper intermediate", "intermediate", "lower intermediate",
        "basic", "elementary", "beginner", "conversational", "working proficiency",
        "professional working proficiency", "full professional proficiency",
        "limited working proficiency", "elementary proficiency",
        
        # Skills breakdown
        "spoken", "speaking", "written", "writing", "reading", "listening",
        "comprehension", "oral", "verbal", "literacy", "literate",
        "can speak", "can read", "can write", "can understand",
        
        # Language learning and certification
        "second language", "third language", "foreign language", "learned",
        "studied", "self-taught", "immersive", "studied abroad",
        "toefl", "ielts", "cefr", "a1", "a2", "b1", "b2", "c1", "c2",
        "delf", "dalf", "dele", "jlpt", "hsk", "topik", "testdaf", "telc",
        
        # Context indicators
        "business", "technical", "medical", "legal", "academic",
        "translation", "interpretation", "localization", "transcription"
    ],
    
    "publications": [
        # General terms
        "publication", "publications", "published", "paper", "papers",
        "research", "research paper", "article", "articles", "author", "co-author",
        "contributor", "writer", "researcher", "investigator", "principal investigator",
        
        # Types of publications
        "journal", "journal article", "peer-reviewed", "peer reviewed article",
        "conference", "conference paper", "conference proceedings", "proceedings",
        "symposium", "workshop paper", "poster", "poster presentation",
        "abstract", "extended abstract", "short paper", "full paper",
        "thesis", "dissertation", "doctoral dissertation", "master's thesis",
        "undergraduate thesis", "phd thesis", "capstone paper",
        "white paper", "technical paper", "technical report", "research report",
        "working paper", "discussion paper", "position paper", "policy brief",
        "book", "book chapter", "edited volume", "monograph", "textbook",
        "review", "review article", "systematic review", "literature review",
        "meta-analysis", "survey paper", "tutorial", "case study", "report",
        
        # Patents and intellectual property
        "patent", "patents", "patent pending", "provisional patent", "utility patent",
        "design patent", "granted patent", "patent application", "patent filed",
        "invention", "intellectual property", "ip", "trademark", "copyright",
        "licensing", "licensed technology", "technology transfer",
        
        # Publication status
        "published", "accepted", "in press", "forthcoming", "under review",
        "submitted", "in preparation", "draft", "preprint", "postprint",
        
        # Identifiers
        "doi", "digital object identifier", "isbn", "issn", "arxiv",
        "pubmed", "pmid", "pmcid", "google scholar", "researchgate",
        "orcid", "researcher id", "scopus", "web of science",
        
        # Quality indicators
        "indexed", "scopus indexed", "sci indexed", "impact factor", "if",
        "cited", "citations", "highly cited", "h-index", "citation count",
        "quartile", "q1", "q2", "q3", "q4", "tier 1", "tier 2",
        
        # Publishers and venues
        "springer", "elsevier", "ieee", "acm", "wiley", "taylor & francis",
        "sage", "oxford", "cambridge", "nature", "science", "plos",
        "frontiers", "mdpi", "hindawi", "bmc", "lancet", "jama",
        
        # Roles
        "first author", "corresponding author", "senior author", "last author",
        "lead author", "sole author", "joint author", "equal contribution",
        "editor", "associate editor", "guest editor", "reviewer", "referee",
        
        # Presentation
        "presented", "oral presentation", "keynote", "invited talk", "seminar",
        "colloquium", "lecture", "talk", "presentation", "speaker", "panelist",
        
        # Impact and reach
        "open access", "public domain", "creative commons", "cc-by", "preprint server",
        "repository", "institutional repository", "archive", "database",
        "accessed", "viewed", "downloaded", "read", "shared", "disseminated"
    ],
    
    "contact": [
        # Contact information
        "email", "e-mail", "mail", "email address", "contact email",
        "phone", "telephone", "mobile", "cell", "cell phone", "mobile number",
        "phone number", "contact number", "tel", "fax", "landline",
        
        # Location
        "address", "location", "city", "state", "country", "zip", "postal code",
        "pin code", "region", "area", "district", "province", "county",
        "street", "avenue", "road", "lane", "based in", "located in",
        "residing", "residence", "domicile", "hometown", "current location",
        
        # Professional networks
        "linkedin", "linkedin profile", "github", "github profile", "stackoverflow",
        "stack overflow", "portfolio", "website", "personal website", "blog",
        "twitter", "x", "medium", "dev.to", "hashnode", "substack",
        
        # Other profiles
        "profile", "social media", "facebook", "instagram", "youtube",
        "behance", "dribbble", "codepen", "codesandbox", "kaggle",
        "researchgate", "google scholar", "orcid", "publons",
        
        # Availability
        "contact", "reach", "available", "availability", "reachable",
        "willing to relocate", "open to relocation", "remote",
        "open to remote", "hybrid", "visa status", "work authorization",
        "authorized to work", "citizen", "permanent resident", "green card",
        
        # Preferred contact
        "preferred contact", "best way to reach", "contact preference",
        "available for", "respond to", "reply to"
    ],
    
    "summary": [
        # Section headers
        "summary", "professional summary", "executive summary", "career summary",
        "profile", "professional profile", "career profile", "personal profile",
        "objective", "career objective", "professional objective", "goal",
        "about", "about me", "overview", "introduction", "bio", "biography",
        
        # Experience indicators
        "years of experience", "yrs experience", "years in", "experience in",
        "background in", "expertise in", "specialized in", "specialization",
        "focus on", "focused on", "concentrating on", "dedicated to",
        
        # Career aspirations
        "seeking", "looking for", "searching for", "pursuing", "interested in",
        "aspiring", "goal-oriented", "career goal", "professional goal",
        "objective is", "aim to", "desire to", "hope to", "wish to",
        
        # Personal qualities
        "passionate", "passionate about", "enthusiastic", "motivated", "driven",
        "dedicated", "committed", "devoted", "diligent", "hardworking",
        "results-oriented", "detail-oriented", "goal-oriented", "team player",
        "self-starter", "proactive", "innovative", "creative", "analytical",
        
        # Professional descriptors
        "experienced", "skilled", "talented", "accomplished", "seasoned",
        "veteran", "expert", "professional", "qualified", "certified",
        "competent", "proficient", "adept", "versed", "knowledgeable",
        
        # Role descriptors
        "engineer", "developer", "designer", "manager", "analyst", "consultant",
        "specialist", "expert", "architect", "lead", "senior", "junior",
        "associate", "staff", "principal", "director", "coordinator",
        
        # Value propositions
        "proven track record", "track record of", "demonstrated ability",
        "strong background", "extensive experience", "comprehensive knowledge",
        "in-depth understanding", "thorough knowledge", "well-versed",
        "successful history", "history of success", "consistent performance"
    ],
    
    "volunteer": [
        # General terms
        "volunteer", "volunteered", "volunteering", "volunteer work",
        "community service", "social service", "public service", "civic engagement",
        
        # Organization types
        "non-profit", "nonprofit", "ngo", "not-for-profit", "charity",
        "charitable organization", "foundation", "social enterprise",
        "community organization", "grassroots", "advocacy group",
        
        # Activities
        "mentorship", "mentor", "mentored", "mentoring", "coach", "coached",
        "coaching", "tutor", "tutored", "tutoring", "teach", "taught", "teaching",
        "train", "trained", "training", "guide", "guided", "advise", "advised",
        
        # Causes and areas
        "education", "literacy", "stem education", "youth development",
        "environment", "environmental", "conservation", "sustainability",
        "health", "healthcare", "medical", "mental health", "wellness",
        "poverty", "homelessness", "hunger", "food security", "food bank",
        "humanitarian", "disaster relief", "emergency response", "crisis",
        "human rights", "civil rights", "social justice", "equality", "inclusion",
        "animal welfare", "animal rights", "wildlife", "rescue",
        
        # Roles and positions
        "volunteer coordinator", "volunteer leader", "board member", "trustee",
        "committee member", "ambassador", "advocate", "organizer", "facilitator",
        
        # Types of work
        "pro bono", "pro bono work", "unpaid", "donated time", "contributed",
        "community", "community work", "outreach", "outreach program",
        "awareness", "fundraising", "fundraiser", "campaign", "drive",
        "activism", "activist", "advocate", "advocacy", "lobbying",
        
        # Time commitment
        "ongoing", "regular", "weekly", "monthly", "occasional", "seasonal",
        "long-term", "short-term", "one-time", "recurring", "continuous",
        
        # Impact
        "served", "helped", "assisted", "supported", "contributed to",
        "participated in", "organized", "coordinated", "led", "managed",
        "impact", "beneficiaries", "community impact", "social impact"
    ],
    
    "interests": [
        # General terms
        "interests", "hobbies", "activities", "pursuits", "passions",
        "passionate about", "enjoy", "love", "like", "fond of",
        "enthusiast", "aficionado", "fan of", "interested in",
        
        # Intellectual interests
        "reading", "books", "literature", "poetry", "writing", "blogging",
        "journalism", "creative writing", "technical writing", "documentation",
        "research", "learning", "continuous learning", "self-improvement",
        "philosophy", "history", "politics", "current affairs", "science",
        
        # Creative interests
        "art", "painting", "drawing", "sketching", "sculpture", "pottery",
        "photography", "videography", "filmmaking", "cinematography",
        "music", "playing music", "singing", "composing", "instrument",
        "guitar", "piano", "drums", "violin", "production", "dj",
        "design", "graphic design", "ui design", "ux design", "web design",
        "crafts", "diy", "woodworking", "knitting", "sewing", "quilting",
        
        # Physical activities
        "sports", "athletics", "fitness", "exercise", "workout", "gym",
        "running", "jogging", "marathon", "cycling", "biking", "swimming",
        "yoga", "pilates", "meditation", "mindfulness", "martial arts",
        "hiking", "trekking", "mountaineering", "climbing", "rock climbing",
        "camping", "backpacking", "outdoors", "nature", "adventure",
        "team sports", "basketball", "football", "soccer", "tennis", "cricket",
        "badminton", "volleyball", "baseball", "golf", "skiing", "snowboarding",
        
        # Technology interests
        "gaming", "video games", "board games", "chess", "esports",
        "coding", "programming", "open source", "hackathons", "maker",
        "robotics", "electronics", "arduino", "raspberry pi", "3d printing",
        "virtual reality", "vr", "augmented reality", "ar", "blockchain",
        
        # Travel and culture
        "travel", "traveling", "exploring", "wanderlust", "backpacking",
        "culture", "cultural exchange", "languages", "language learning",
        "cuisine", "cooking", "baking", "culinary", "food", "gastronomy",
        "wine", "coffee", "tea", "brewing", "mixology", "cocktails",
        
        # Social activities
        "volunteering", "community service", "networking", "socializing",
        "public speaking", "toastmasters", "debate", "discussion", "forums",
        "meetups", "conferences", "events", "concerts", "theater", "cinema",
        
        # Other interests
        "gardening", "plants", "horticulture", "agriculture", "farming",
        "pets", "animals", "dogs", "cats", "aquarium", "bird watching",
        "astronomy", "stargazing", "space", "aviation", "flying", "drones",
        "automobiles", "cars", "motorcycles", "mechanics", "restoration",
        "fashion", "style", "interior design", "home decor", "architecture",
        "entrepreneurship", "startups", "innovation", "investing", "finance",
        "sustainability", "environment", "climate", "renewable energy"
    ],
    
    "references": [
        # Section headers
        "references", "professional references", "reference", "recommendation",
        "recommendations", "testimonials", "endorsements", "referees",
        
        # Availability statements
        "available upon request", "available on request", "provided upon request",
        "furnished upon request", "supplied upon request", "can be provided",
        "will be provided", "references attached", "listed below",
        
        # Reference types
        "professional reference", "academic reference", "personal reference",
        "character reference", "employment reference", "supervisor reference",
        "colleague reference", "client reference", "mentor reference",
        
        # Reference information
        "name", "title", "relationship", "company", "organization",
        "contact information", "phone", "email", "known for", "worked with",
        "supervised by", "managed by", "collaborated with", "professor"
    ],
    
    "achievements": [
        # Performance metrics
        "increased", "decreased", "improved", "enhanced", "optimized",
        "reduced", "saved", "generated", "grew", "expanded", "scaled",
        "achieved", "delivered", "exceeded", "surpassed", "outperformed",
        
        # Quantifiable results
        "revenue", "sales", "profit", "margin", "roi", "return on investment",
        "cost savings", "efficiency", "productivity", "performance",
        "growth", "growth rate", "market share", "customer satisfaction",
        "retention", "conversion", "engagement", "traffic", "users",
        
        # Scale indicators
        "million", "billions", "thousands", "hundreds", "percent", "%",
        "x growth", "fold increase", "times", "multiple", "doubled", "tripled",
        
        # Leadership achievements
        "led team of", "managed team of", "directed", "oversaw", "supervised",
        "built team", "hired", "trained", "developed", "mentored",
        "cross-functional", "multidisciplinary", "stakeholder management",
        
        # Innovation achievements
        "pioneered", "introduced", "launched", "established", "created",
        "first", "first-ever", "groundbreaking", "innovative", "novel",
        "patent", "invention", "breakthrough", "disrupted", "transformed"
    ],
    
    "soft_skills": [
        # Communication
        "communication", "written communication", "verbal communication",
        "presentation", "public speaking", "active listening", "articulate",
        "persuasion", "negotiation", "interpersonal", "storytelling",
        
        # Leadership
        "leadership", "team leadership", "strategic leadership", "vision",
        "decision making", "delegation", "motivation", "influence",
        "conflict resolution", "change management", "people management",
        
        # Collaboration
        "teamwork", "collaboration", "cooperative", "team player",
        "cross-functional", "stakeholder management", "relationship building",
        "partnership", "consensus building", "facilitation",
        
        # Problem solving
        "problem solving", "analytical", "critical thinking", "troubleshooting",
        "creative", "innovation", "strategic thinking", "research",
        "root cause analysis", "logical", "systematic",
        
        # Work ethic
        "reliable", "dependable", "accountable", "responsible", "integrity",
        "honest", "ethical", "professional", "punctual", "diligent",
        "self-motivated", "driven", "proactive", "initiative",
        
        # Adaptability
        "adaptable", "flexible", "versatile", "resilient", "agile",
        "quick learner", "fast learner", "open-minded", "embracing change",
        
        # Organization
        "organized", "time management", "prioritization", "planning",
        "multitasking", "attention to detail", "detail-oriented", "efficient",
        
        # Emotional intelligence
        "empathy", "empathetic", "emotional intelligence", "self-aware",
        "patient", "positive attitude", "optimistic", "enthusiastic"
    ]
}

@dataclass(frozen=True)
class SectionResult:
    content: str
    confidence: float


class SectionParser:
    def __init__(self, use_spacy: bool = True) -> None:
        self.use_spacy = use_spacy and spacy is not None
        self._nlp = None
        self._matcher = None
        self._last_header_matches: list[dict[str, object]] = []
        self._last_header_confidence: dict[int, float] = {}
        self._last_section_header_confidence: dict[str, float] = {}
        if self.use_spacy:
            self._nlp = spacy.blank("xx")
            self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
            for key, aliases in SECTION_ALIASES.items():
                patterns = [self._nlp.make_doc(alias) for alias in aliases]
                self._matcher.add(key, patterns)

    def parse(self, raw_text: str) -> dict[str, SectionResult]:
        lines, blank_context = self._prepare_lines(raw_text)
        header_map = self._detect_headers(lines, blank_context)
        if not header_map:
            sections = self._infer_sections_no_headers(lines)
        else:
            sections = self._slice_sections(lines, header_map)
        sections = self._canonicalize_sections(sections)
        sections = self._postprocess_sections(sections)
        scored = self._score_sections(sections)
        return scored

    def get_detected_headers(self) -> list[dict[str, object]]:
        return list(self._last_header_matches)

    def _prepare_lines(self, text: str) -> tuple[list[str], dict[int, bool]]:
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        raw_lines = [line.strip() for line in cleaned.split("\n")]
        kept_raw_indexes: list[int] = []
        lines: list[str] = []
        for idx, line in enumerate(raw_lines):
            if not line:
                continue
            kept_raw_indexes.append(idx)
            lines.append(self._normalize_table_row(line))

        blank_context: dict[int, bool] = {}
        for j, raw_idx in enumerate(kept_raw_indexes):
            before_blank = raw_idx > 0 and not raw_lines[raw_idx - 1]
            after_blank = raw_idx + 1 < len(raw_lines) and not raw_lines[raw_idx + 1]
            blank_context[j] = bool(before_blank and after_blank)

        return lines, blank_context

    @staticmethod
    def _normalize_table_row(line: str) -> str:
        if "  " in line:
            parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
            if len(parts) > 1:
                return " | ".join(parts)
        return line

    def _detect_headers(self, lines: list[str], blank_context: dict[int, bool]) -> dict[int, str]:
        self._last_header_matches = []
        self._last_header_confidence = {}
        self._last_section_header_confidence = {}

        header_map: dict[int, str] = {}
        for idx, line in enumerate(lines):
            match = self._match_header_line(line, blank_context.get(idx, False))
            if match is None:
                continue
            key, confidence = match
            header_map[idx] = key
            self._last_header_matches.append(
                {"section": key, "line_index": idx, "confidence": confidence}
            )
            self._last_header_confidence[idx] = confidence
            current_best = self._last_section_header_confidence.get(key, 0.0)
            if confidence > current_best:
                self._last_section_header_confidence[key] = confidence

        if self.use_spacy and self._nlp and self._matcher:
            doc = self._nlp("\n".join(lines))
            matches = self._matcher(doc)
            for match_id, start, end in matches:
                match_text = doc[start:end].text.strip()
                for idx, line in enumerate(lines):
                    if match_text.lower() == line.lower():
                        key = self._nlp.vocab.strings[match_id]
                        if idx not in header_map:
                            header_map[idx] = key
                            confidence = 1.0
                            self._last_header_matches.append(
                                {"section": key, "line_index": idx, "confidence": confidence}
                            )
                            self._last_header_confidence[idx] = confidence
                            current_best = self._last_section_header_confidence.get(key, 0.0)
                            if confidence > current_best:
                                self._last_section_header_confidence[key] = confidence
        return header_map

    def _match_header_line(
        self, line: str, blank_surrounded: bool
    ) -> tuple[str, float] | None:
        if not line:
            return None
        if len(line) > 80:
            return None
        if self._looks_like_bullet(line):
            return None
        if self._looks_like_sentence(line):
            return None
        lowered = line.lower().strip()
        if not lowered:
            return None
        has_digits = bool(re.search(r"\d", lowered))

        casing_bonus = 0.0
        if self._is_uppercase_header(line) or self._is_titlecase_header(line):
            casing_bonus = 0.05
        length_bonus = 0.0
        token_count = len([t for t in re.split(r"\s+", line.strip()) if t])
        if 1 <= token_count <= 4:
            length_bonus = 0.05
        elif token_count == 5:
            length_bonus = 0.02
        blank_bonus = 0.05 if blank_surrounded else 0.0

        for key, pattern in SECTION_REGEX.items():
            if pattern.match(line):
                return key, min(1.0, 1.0 + casing_bonus + length_bonus + blank_bonus)

        if any(re.search(rf"\b{re.escape(v)}\b", lowered) for v in HEADER_FALSE_POSITIVE_VERBS):
            return None

        normalized_line = self._normalize_header_text(line)
        if not normalized_line:
            return None

        if has_digits:
            normalized_digitless = self._normalize_header_text(re.sub(r"\d+", " ", line))
            if not normalized_digitless:
                return None
            digitless_haystack = f" {normalized_digitless} "
            digitless_best: tuple[str, float] | None = None
            for key, aliases in SECTION_ALIASES.items():
                for alias in aliases:
                    alias_norm = self._normalize_header_text(alias)
                    if not alias_norm:
                        continue
                    if normalized_digitless == alias_norm or f" {alias_norm} " in digitless_haystack:
                        digitless_best = (key, min(1.0, 0.8 + casing_bonus + length_bonus + blank_bonus))
                        break
                if digitless_best is not None:
                    break
            if digitless_best is None:
                return None
            return digitless_best
        haystack = f" {normalized_line} "

        best: tuple[str, float] | None = None
        for key, aliases in SECTION_ALIASES.items():
            for alias in aliases:
                alias_norm = self._normalize_header_text(alias)
                if not alias_norm:
                    continue
                if normalized_line == alias_norm:
                    base = 0.85 + casing_bonus + length_bonus + blank_bonus
                    return key, min(1.0, base)
                if f" {alias_norm} " in haystack:
                    candidate = (key, min(1.0, 0.85 + casing_bonus + length_bonus + blank_bonus))
                    if best is None or candidate[1] > best[1]:
                        best = candidate
                    continue
        return best

    def _postprocess_sections(self, sections: dict[str, list[str]]) -> dict[str, list[str]]:
        if not sections:
            return sections

        certifications = list(sections.get("certifications", []) or [])
        skills = list(sections.get("skills", []) or [])

        if certifications:
            kept_certs: list[str] = []
            moved_to_skills: list[str] = []
            for line in certifications:
                if self._looks_like_skill_line(line) and not self._looks_like_cert_line(line):
                    moved_to_skills.append(line)
                else:
                    kept_certs.append(line)
            certifications = kept_certs
            skills.extend(moved_to_skills)

        if skills:
            kept_skills: list[str] = []
            moved_to_certs: list[str] = []
            for line in skills:
                if self._looks_like_cert_line(line) and not self._looks_like_skill_line(line):
                    moved_to_certs.append(line)
                else:
                    kept_skills.append(line)
            skills = kept_skills
            certifications.extend(moved_to_certs)

        if certifications or "certifications" in sections:
            sections["certifications"] = self._dedupe_preserve_order(certifications)
        if skills or "skills" in sections:
            sections["skills"] = self._dedupe_preserve_order(skills)

        return sections

    @staticmethod
    def _dedupe_preserve_order(lines: list[str]) -> list[str]:
        seen: set[str] = set()
        output: list[str] = []
        for line in lines:
            key = (line or "").strip().lower()
            if not key:
                continue
            if key in seen:
                continue
            seen.add(key)
            output.append(line)
        return output

    @staticmethod
    def _looks_like_cert_line(line: str) -> bool:
        lowered = (line or "").lower()
        if not lowered:
            return False
        if len(lowered) > 220:
            return False
        if re.search(r"\b(certified|certification|certificate|license|licen[cs]e|credential|issued by|issuer|expires|expiry|valid until)\b", lowered):
            return True
        if re.search(r"\b(aws certified|azure fundamentals|google cloud certified|certified kubernetes|ckad|cka|pmp)\b", lowered):
            return True
        return False

    @staticmethod
    def _looks_like_bullet(line: str) -> bool:
        return bool(re.match(r"^\s*(?:[-*•\u2022]|\d+\.)\s+", line))

    @staticmethod
    def _looks_like_sentence(line: str) -> bool:
        words = [w for w in re.split(r"\s+", line.strip()) if w]
        if len(words) >= 8:
            return True
        if "," in line or ";" in line:
            return True
        if line.strip().endswith("."):
            return True
        if re.search(r"\b(?:and|with|that|which|using)\b", line.lower()) and len(words) >= 6:
            return True
        return False

    @staticmethod
    def _is_uppercase_header(line: str) -> bool:
        letters = [c for c in line if c.isalpha()]
        if not letters:
            return False
        upper = sum(1 for c in letters if c.isupper())
        return (upper / max(1, len(letters))) >= 0.85

    @staticmethod
    def _is_titlecase_header(line: str) -> bool:
        tokens = [t for t in re.split(r"\s+", re.sub(r"[^A-Za-z ]+", " ", line).strip()) if t]
        if not tokens or len(tokens) > 6:
            return False
        titled = sum(1 for t in tokens if t[:1].isupper())
        return titled / max(1, len(tokens)) >= 0.75

    def _infer_sections_no_headers(self, lines: list[str]) -> dict[str, list[str]]:
        self._last_section_header_confidence = {}
        sections: dict[str, list[str]] = {}
        if not lines:
            return {"unknown": []}

        contact_end = -1
        for idx, line in enumerate(lines[:15]):
            if _CONTACT_HINT_RE.search(line):
                contact_end = idx
        if contact_end >= 0:
            sections["contact"] = lines[: contact_end + 1]
            self._last_section_header_confidence["contact"] = 0.7

        start_idx = max(contact_end + 1, 0)
        markers: dict[str, int] = {}
        for idx in range(start_idx, len(lines)):
            line = lines[idx]
            lowered = line.lower()
            if "skills" not in markers and self._looks_like_skill_line(line):
                markers["skills"] = idx
            if "experience" not in markers and (_DATE_RANGE_RE.search(line) or _YEAR_RANGE_RE.search(line)):
                markers["experience"] = idx
            if "education" not in markers and (_DEGREE_HINT_RE.search(line) or "university" in lowered or "college" in lowered):
                markers["education"] = idx
            if "certifications" not in markers and re.search(r"\b(certified|certification|certificate|license|licence)\b", lowered):
                markers["certifications"] = idx
            if "projects" not in markers and re.search(r"\bprojects?\b", lowered):
                markers["projects"] = idx

        if "summary" not in markers:
            upper_bound = min([v for v in markers.values()] + [len(lines)])
            for idx in range(start_idx, upper_bound):
                line = lines[idx]
                words = [w for w in re.split(r"\s+", line.strip()) if w]
                if len(words) >= 12 and not self._looks_like_bullet(line):
                    markers["summary"] = idx
                    break

        ordered = sorted(((idx, key) for key, idx in markers.items()), key=lambda it: it[0])
        if not ordered:
            remaining = lines[start_idx:]
            if remaining:
                sections["unknown"] = remaining
            return sections

        last_cursor = start_idx
        for pos, (idx, key) in enumerate(ordered):
            if idx > last_cursor and "summary" not in sections and "summary" not in markers:
                pass
            if idx > last_cursor and last_cursor == start_idx and start_idx > 0:
                pass
            next_idx = ordered[pos + 1][0] if pos + 1 < len(ordered) else len(lines)
            content = lines[idx:next_idx]
            sections[key] = content
            self._last_section_header_confidence[key] = 0.65
            last_cursor = next_idx

        if start_idx < ordered[0][0]:
            pre = lines[start_idx : ordered[0][0]]
            if pre and "summary" not in sections:
                sections["summary"] = pre
                self._last_section_header_confidence["summary"] = 0.6

        return sections

    @staticmethod
    def _looks_like_skill_line(line: str) -> bool:
        lowered = line.lower()
        if ":" in line and re.search(
            r"\b(languages|frontend|backend|tools|testing|frameworks|databases|cloud|apis)\b",
            lowered,
        ):
            return True
        comma_count = line.count(",")
        if comma_count >= 3 and len(line) <= 120:
            return True
        hits = sum(1 for hint in KEYWORD_HINTS.get("skills", []) if hint in lowered)
        return hits >= 2

    @staticmethod
    def _normalize_header_text(value: str) -> str:
        normalized = re.sub(r"[:|/&\\\-]+", " ", value.lower())
        normalized = re.sub(r"[^a-z0-9 ]+", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _slice_sections(
        self, lines: list[str], header_map: dict[int, str]
    ) -> dict[str, list[str]]:
        if not header_map:
            return {"unknown": lines}

        sorted_headers = sorted(header_map.items(), key=lambda item: item[0])
        sections: dict[str, list[str]] = {}
        for i, (idx, key) in enumerate(sorted_headers):
            start = idx + 1
            end = sorted_headers[i + 1][0] if i + 1 < len(sorted_headers) else len(lines)
            content = lines[start:end]
            sections.setdefault(key, []).extend(content)
        return sections

    def _canonicalize_sections(self, sections: dict[str, list[str]]) -> dict[str, list[str]]:
        if not isinstance(sections, dict) or not sections:
            return sections

        canonical: dict[str, list[str]] = {}
        header_conf: dict[str, float] = {}
        for key, lines in sections.items():
            canonical_key = self._canonical_section_key(str(key or ""))
            canonical.setdefault(canonical_key, []).extend(lines or [])
            if self._last_section_header_confidence:
                existing = header_conf.get(canonical_key, 0.0)
                header_conf[canonical_key] = max(
                    existing,
                    float(self._last_section_header_confidence.get(key, 0.0) or 0.0),
                )

        if header_conf:
            self._last_section_header_confidence = header_conf

        return canonical

    @staticmethod
    def _canonical_section_key(key: str) -> str:
        normalized = (key or "").strip().lower()
        if not normalized:
            return "unknown"

        if normalized in {
            "technical_skills",
            "technical_expertise",
            "programming_skills",
            "programming_languages",
            "software_skills",
            "software",
            "tools",
            "tools_and_technologies",
            "technologies",
            "frameworks",
            "platforms",
            "tech_stack",
            "technical_proficiencies",
            "competencies",
            "core_competencies",
            "key_competencies",
            "strengths",
            "expertise",
            "areas_of_expertise",
            "capabilities",
        }:
            return "skills"

        if normalized in {
            "licenses",
            "credentials",
            "accreditations",
            "security_clearances",
            "clearances",
        }:
            return "certifications"

        if normalized in {
            "profile",
            "professional_profile",
            "career_profile",
            "executive_summary",
            "professional_summary",
            "career_summary",
            "objective",
            "career_objective",
            "professional_objective",
            "highlights",
            "career_highlights",
            "professional_highlights",
            "qualifications_summary",
            "summary_of_qualifications",
            "value_proposition",
        }:
            return "summary"

        if normalized in {
            "employment",
            "employment_history",
            "work_history",
            "career_history",
            "job_history",
            "internships",
            "internship_experience",
            "consulting_experience",
            "management_experience",
            "leadership_experience",
            "teaching_experience",
            "research_experience",
        }:
            return "experience"

        if normalized in {
            "training",
            "courses",
            "professional_development",
            "continuing_education",
            "workshops",
            "seminars",
        }:
            return "education"

        return normalized

    def _score_sections(
        self, sections: dict[str, list[str]]
    ) -> dict[str, SectionResult]:
        results: dict[str, SectionResult] = {}
        for key, content_lines in sections.items():
            text = "\n".join(content_lines).strip()
            header_confidence = float(self._last_section_header_confidence.get(key, 0.0) or 0.0)
            confidence = max(self._base_confidence(key), header_confidence)
            confidence += self._keyword_boost(key, text)
            confidence = min(confidence, 1.0)
            results[key] = SectionResult(content=text, confidence=confidence)
        return results

    def _base_confidence(self, key: str) -> float:
        if key in SECTION_KEYS:
            return 0.6
        return 0.3

    def _keyword_boost(self, key: str, text: str) -> float:
        hints = KEYWORD_HINTS.get(key, [])
        if not hints or not text:
            return 0.0
        hits = sum(1 for hint in hints if hint.lower() in text.lower())
        return min(0.1 * hits, 0.3)

"""
Resume section detector and splitter for parsing resume structure.
Identifies and splits resume into logical sections like experience, education, skills, etc.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class SectionSplitter:
    """
    Advanced resume / CV section detector and splitter.
    Supports worldwide naming conventions:
    English (US, UK, AU, CA, NZ, ZA, IN, SG, PH, NG, GH, KE, MY, BD, PK, LK, NP),
    European-English, Middle-East-English, East-Asian-English,
    Latin-American-English, and every major industry vertical.
    ~2000+ keyword variants across 25 section types.
    """
    
    # Section keywords for detection
    SECTION_KEYWORDS = {

        # ════════════════════════════════════════════════════════════════════════
        # 1. EXPERIENCE
        # ════════════════════════════════════════════════════════════════════════
        'experience': [
            # ── Core English ──
            'experience', 'experiences',
            'work experience', 'work experiences',
            'work history', 'work histories',
            'professional experience', 'professional experiences',
            'professional background',
            'employment history', 'employment histories',
            'employment', 'employments',
            'career history', 'career histories',
            'career', 'careers',
            'job history', 'job histories',
            'job experience', 'job experiences',
            'relevant experience', 'related experience',
            'industry experience', 'industry background',
            'work', 'positions held', 'positions',
            'roles held', 'roles and responsibilities',
            'roles', 'job roles',
            'previous experience', 'prior experience',
            'past experience', 'current experience',
            'recent experience', 'global experience',
            'international experience', 'cross-functional experience',
            'practical experience', 'applied experience',
            'hands-on experience', 'field experience',
            'operational experience', 'staff experience',
            'service history', 'service experience',
            # ── Industry verticals ──
            'business experience', 'corporate experience', 'executive experience',
            'management experience', 'leadership experience', 'technical experience',
            'engineering experience', 'software experience', 'it experience',
            'clinical experience', 'medical experience', 'nursing experience',
            'healthcare experience', 'hospital experience', 'patient care experience',
            'research experience', 'laboratory experience', 'lab experience',
            'teaching experience', 'academic experience', 'faculty experience',
            'consulting experience', 'advisory experience', 'legal experience',
            'freelance experience', 'contract experience', 'contractual experience',
            'internship experience', 'intern experience', 'trainee experience',
            'apprenticeship experience', 'graduate experience',
            'volunteer experience', 'voluntary experience', 'community experience',
            'military experience', 'defense experience', 'armed forces experience',
            'government experience', 'public sector experience', 'civil service experience',
            'nonprofit experience', 'ngo experience', 'social sector experience',
            'finance experience', 'banking experience', 'investment experience',
            'sales experience', 'marketing experience', 'retail experience',
            'customer service experience', 'hospitality experience',
            'construction experience', 'manufacturing experience',
            'logistics experience', 'supply chain experience',
            'media experience', 'creative experience', 'design experience',
            'data experience', 'analytics experience', 'ai experience',
            'devops experience', 'cloud experience', 'security experience',
            # ── UK / Commonwealth ──
            'career overview', 'career summary',
            'employment record', 'employment background',
            'work placements', 'placements', 'work-based learning',
            'sandwich placement', 'industrial placement', 'year in industry',
            # ── Australia / NZ ──
            'previous roles', 'prior roles', 'current and previous roles',
            'employment profile',
            # ── Canada ──
            'occupational history', 'occupational background',
            # ── South Africa ──
            'work background', 'professional record', 'career record',
            # ── India / South Asia ──
            'professional history', 'professional journey', 'work profile',
            'assignment history', 'assignments', 'professional assignments',
            'project assignments', 'work synopsis', 'employment synopsis',
            'career synopsis', 'career details', 'employment details',
            'work details', 'job details', 'professional details',
            # ── Singapore / Malaysia / Philippines ──
            'working experience', 'career experiences',
            'employment experiences',
            # ── Nigeria / Ghana / Kenya ──
            'working history', 'career background', 'occupational experience',
            # ── Middle East / Gulf ──
            'work tenure', 'tenure', 'professional tenure',
            'career track', 'career path',
            # ── East Asia ──
            'working career', 'career development',
            # ── European English ──
            'professional career', 'working experience',
            'professional activities', 'working life', 'professional life',
            # ── Latin American English ──
            'labor experience', 'labour experience',
            'professional trajectory',
            # ── Academic CVs ──
            'academic employment', 'academic positions', 'academic appointments',
            'faculty positions', 'research positions', 'postdoctoral experience',
            'research appointments', 'professional appointments',
            'academic career', 'teaching positions', 'research roles',
            'academic roles', 'scholarly positions',
            # ── Healthcare CVs ──
            'clinical positions', 'clinical appointments', 'hospital appointments',
            'medical positions', 'residency experience', 'fellowship experience',
            'clinical rotations', 'rotations',
            # ── Legal CVs ──
            'legal career', 'practice history', 'law experience',
            # ── Creative / Media ──
            'professional credits', 'credits', 'production experience',
            # ── Military / Government ──
            'military service', 'government service',
            'public service', 'federal experience',
            # ── General catch-alls ──
            'additional experience', 'other experience', 'other roles',
            'relevant roles', 'notable roles', 'key roles',
            'selected experience', 'featured experience',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 2. EDUCATION
        # ════════════════════════════════════════════════════════════════════════
        'education': [
            # ── Core English ──
            'education', 'educational background', 'educational history',
            'educational details', 'educational profile', 'educational summary',
            'educational qualifications', 'educational credentials',
            'educational achievements', 'educational attainment',
            'educational information', 'education background',
            'academic background', 'academic history', 'academic qualifications',
            'academic credentials', 'academic achievements', 'academic record',
            'academic profile', 'academic summary', 'academic overview',
            'academic details', 'academic information',
            'qualifications', 'formal qualifications',
            'degrees', 'degrees earned', 'degrees conferred', 'degrees awarded',
            'degree details', 'academic degrees',
            'schooling', 'studies', 'academic studies',
            'training and education', 'academic training',
            'learning', 'formal education', 'formal learning', 'formal training',
            # ── UK / Commonwealth ──
            'further education', 'higher education', 'secondary education',
            'post-secondary education', 'tertiary education',
            'tertiary qualifications', 'higher qualifications',
            'a-levels', 'gcses', 'o-levels', 'btec', 'nvq', 'hnc', 'hnd',
            'foundation degree', 'access course', 'national diploma',
            # ── USA ──
            'academic preparation', 'college education', 'university education',
            'graduate education', 'undergraduate education', 'postgraduate education',
            'doctoral education', 'professional education', 'continuing education',
            'degree programs', 'graduate studies', 'undergraduate studies',
            'doctoral studies', 'postdoctoral training', 'postdoctoral studies',
            'graduate training',
            # ── Australia / NZ ──
            'tafe', 'technical and further education', 'vocational qualifications',
            # ── Canada ──
            'cegep', 'college diploma', 'college certificate',
            'post-secondary credentials',
            # ── India ──
            'scholastic background', 'scholastics',
            'academic career', 'school career', 'college details',
            'university details', 'educational synopsis',
            # ── Pakistan / Bangladesh / Sri Lanka / Nepal ──
            'educational record', 'qualification details',
            'academic qualifications and training',
            # ── Singapore / Malaysia / Philippines ──
            'study background', 'school background',
            # ── Nigeria / Kenya / Ghana ──
            'academic training', 'school history', 'educational experience',
            # ── Middle East / Gulf ──
            'education and training', 'educational pathway',
            # ── European English ──
            'educational career', 'study history',
            # ── Latin American English ──
            'academic formation', 'formation', 'academic instruction',
            # ── Academic CVs ──
            'advanced degrees', 'professional degrees',
            'graduate certificates', 'postgraduate certificates',
            # ── Medical / Health ──
            'medical education', 'medical training', 'nursing education',
            'clinical training', 'residency', 'fellowship',
            'internship education', 'medical school',
            # ── Vocational / Trade ──
            'vocational training', 'vocational education', 'apprenticeship',
            'trade qualifications', 'trade training', 'technical training',
            'technical education', 'professional training',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 3. SKILLS
        # ════════════════════════════════════════════════════════════════════════
        'skills': [
            # ── Core English ──
            'skills', 'skill set', 'skillset', 'skills summary',
            'skills overview', 'skills profile', 'skills and expertise',
            'expertise', 'areas of expertise', 'domain expertise',
            'domain knowledge', 'subject matter expertise',
            'competencies', 'core competencies', 'key competencies',
            'professional competencies', 'technical competencies',
            'abilities', 'skills and abilities', 'capabilities',
            'key capabilities', 'professional capabilities',
            'proficiencies', 'technical proficiencies',
            'technical skills', 'technical expertise',
            'key skills', 'core skills', 'primary skills',
            'specialized skills', 'specializations', 'specialties',
            'professional skills',
            # ── Technology-specific ──
            'programming languages', 'languages and frameworks',
            'frameworks and libraries', 'frameworks', 'libraries',
            'technologies', 'technologies and tools',
            'tools and technologies', 'tools',
            'platforms', 'platforms and tools', 'platforms and technologies',
            'software', 'software skills', 'software proficiency',
            'it skills', 'computer skills', 'digital skills',
            'technical toolbox', 'tech stack', 'stack',
            'development skills', 'engineering skills', 'coding skills',
            'programming skills', 'scripting skills',
            'tools and frameworks', 'tools and platforms', 'tools and software',
            'software and tools', 'software and technologies',
            'systems', 'systems and tools', 'applications',
            # ── Non-technical ──
            'soft skills', 'interpersonal skills', 'communication skills',
            'leadership skills', 'management skills', 'analytical skills',
            'transferable skills', 'functional skills', 'general skills',
            'personal skills', 'people skills', 'social skills',
            'organizational skills', 'planning skills', 'strategic skills',
            # ── UK / Commonwealth ──
            'knowledge and skills', 'skills and knowledge',
            # ── India / South Asia ──
            'technical knowledge', 'area of expertise', 'areas of knowledge',
            'expertise and skills', 'skill highlights',
            'skills and competencies', 'competencies and skills',
            'technical stack', 'tech skills',
            'skills and tools', 'tools and skills',
            'value-added skills', 'additional skills', 'other skills',
            'relevant skills',
            # ── East Asia ──
            'technical abilities', 'professional abilities',
            # ── Academic / research ──
            'research skills', 'laboratory skills', 'lab skills',
            'methodological skills', 'quantitative skills', 'qualitative skills',
            'analytical competencies', 'statistical skills', 'data skills',
            # ── Healthcare ──
            'clinical skills', 'medical skills', 'nursing skills',
            'patient care skills', 'surgical skills', 'procedural skills',
            # ── Creative / Design ──
            'design skills', 'creative skills', 'artistic skills',
            'design tools', 'creative tools', 'visual skills', 'multimedia skills',
            # ── Languages (foreign) ──
            'languages', 'language skills', 'foreign languages',
            'language proficiency', 'linguistic skills', 'bilingual', 'multilingual',
            'language competencies', 'language abilities', 'language knowledge',
            'spoken languages', 'languages spoken', 'natural languages',
            # ── Broader catch-alls ──
            'knowledge', 'skills and experience',
            'strengths', 'core strengths', 'key strengths',
            'highlights', 'skill highlights', 'key highlights',
            'qualifications and competencies',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 4. SUMMARY / OBJECTIVE
        # ════════════════════════════════════════════════════════════════════════
        'summary': [
            # ── Core English ──
            'summary', 'professional summary', 'career summary',
            'executive summary', 'personal summary',
            'objective', 'career objective', 'job objective',
            'professional objective',
            'profile', 'professional profile', 'career profile',
            'personal profile', 'candidate profile', 'applicant profile',
            'about me', 'about myself', 'about',
            'who i am', 'who am i',
            'overview', 'professional overview', 'career overview',
            'introduction', 'professional introduction', 'brief introduction',
            'bio', 'biography', 'short bio', 'professional bio',
            'background', 'professional background summary',
            'statement', 'professional statement', 'career statement',
            'personal statement', 'brand statement', 'personal brand statement',
            # ── UK / Commonwealth ──
            'covering statement', 'covering summary',
            'executive profile', 'leadership profile',
            # ── USA ──
            'resume summary', 'resume objective',
            'qualifications summary', 'summary of qualifications',
            'highlights of qualifications',
            # ── India / South Asia ──
            'career synopsis', 'career abstract', 'synopsis',
            'professional synopsis', 'brief profile', 'profile summary',
            'snapshot', 'career snapshot', 'professional snapshot',
            'profile overview', 'career brief',
            # ── East Asia ──
            'self introduction', 'self-introduction', 'career introduction',
            # ── Middle East / Gulf ──
            'professional abstract', 'professional outline', 'career highlights',
            # ── Academic CVs ──
            'research interests', 'research statement',
            'teaching statement', 'teaching philosophy',
            'statement of purpose', 'statement of interest',
            'research summary', 'academic summary', 'scholarly interests',
            # ── Creative / media ──
            'creative statement', 'artist statement', 'designer statement',
            # ── Entry-level / student ──
            'objective statement', 'career goal', 'career goals',
            'goals', 'aims', 'mission statement',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 5. PROJECTS
        # ════════════════════════════════════════════════════════════════════════
        'projects': [
            # ── Core English ──
            'projects', 'project work', 'project experience',
            'key projects', 'featured projects', 'notable projects',
            'selected projects', 'major projects', 'significant projects',
            'relevant projects', 'recent projects',
            'independent projects', 'personal projects',
            'side projects', 'side work',
            'open source', 'open source contributions', 'open source projects',
            'portfolio', 'work portfolio',
            # ── Academic ──
            'academic projects', 'student projects',
            'capstone project', 'capstone projects',
            'thesis project', 'dissertation project',
            'research project', 'research projects',
            'final year project', 'final year projects',
            'fyp', 'degree project', 'degree projects',
            'course projects', 'class projects', 'university projects',
            'college projects', 'school projects',
            'semester projects', 'term projects',
            # ── Industry / tech ──
            'engineering projects', 'technical projects',
            'software projects', 'coding projects', 'programming projects',
            'web projects', 'mobile projects', 'app projects',
            'data projects', 'ml projects', 'ai projects',
            'cloud projects', 'devops projects', 'security projects',
            'design projects', 'creative projects', 'ui/ux projects',
            # ── Professional ──
            'client projects', 'consulting projects', 'freelance projects',
            'contract projects', 'professional projects',
            'collaborative projects', 'team projects', 'group projects',
            'corporate projects', 'enterprise projects', 'business projects',
            # ── India / South Asia ──
            'project details', 'project list', 'project summary',
            'project overview', 'live projects', 'industry projects',
            'it projects', 'development projects',
            # ── General ──
            'work samples', 'samples', 'deliverables', 'outcomes',
            'contributions', 'github projects', 'gitlab projects',
            'case studies', 'initiatives', 'ventures',
            'startup projects', 'entrepreneurial projects',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 6. CERTIFICATIONS
        # ════════════════════════════════════════════════════════════════════════
        'certifications': [
            # ── Core English ──
            'certifications', 'certification', 'certificates', 'certificate',
            'professional certifications', 'professional certificates',
            'technical certifications', 'industry certifications',
            'it certifications', 'cloud certifications',
            'relevant certifications', 'key certifications',
            'notable certifications', 'selected certifications',
            'credentials', 'professional credentials', 'industry credentials',
            'technical credentials',
            'licenses', 'license', 'professional licenses',
            'licenses and certifications', 'certifications and licenses',
            'certificates and diplomas',
            'accreditations', 'accreditation',
            'continuing education', 'continuing professional development', 'cpd',
            'professional development', 'professional development courses',
            'courses', 'online courses', 'e-learning', 'moocs',
            'training', 'training programs', 'training courses',
            'workshops attended', 'workshops', 'seminars', 'seminars attended',
            'bootcamps', 'bootcamp', 'coding bootcamp',
            'coursework', 'relevant coursework', 'additional coursework',
            # ── UK / Commonwealth ──
            'professional memberships', 'memberships',
            'chartered status', 'chartered qualifications', 'nvq', 'hnc', 'hnd',
            # ── India / South Asia ──
            'additional qualifications', 'value-added courses',
            'certification details', 'training and certifications',
            'professional courses', 'short courses',
            'online certifications', 'e-certifications',
            # ── Healthcare ──
            'medical licenses', 'clinical licenses', 'board certifications',
            'specialty certifications', 'nursing certifications',
            'cpr certification', 'bls', 'acls', 'pals',
            # ── Finance / Legal ──
            'regulatory licenses', 'bar admissions', 'bar membership',
            'cpa', 'cfa', 'frm', 'acca', 'cima', 'ca', 'cs',
            # ── IT specific ──
            'aws certifications', 'azure certifications', 'google certifications',
            'cisco certifications', 'microsoft certifications',
            'comptia certifications', 'pmp', 'prince2', 'itil',
            'scrum certifications', 'agile certifications',
            # ── General ──
            'diplomas', 'diploma', 'short courses completed',
            'online learning', 'e-courses',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 7. AWARDS & ACHIEVEMENTS
        # ════════════════════════════════════════════════════════════════════════
        'awards': [
            # ── Core English ──
            'awards', 'award', 'achievements', 'achievement',
            'honors', 'honour', 'honours', 'honor',
            'recognition', 'recognitions',
            'awards and honors', 'awards and honours',
            'awards and recognition', 'honors and awards',
            'achievements and awards', 'achievements and recognition',
            'professional awards', 'industry awards',
            'academic awards', 'academic honors', 'academic honours',
            'academic achievements', 'academic distinctions',
            'distinctions', 'distinction',
            'commendations', 'commendation', 'merits', 'merit',
            'accolades', 'accolade',
            'prizes', 'prize',
            'accomplishments', 'key accomplishments', 'notable accomplishments',
            'professional achievements', 'career achievements',
            'notable achievements', 'key achievements',
            # ── Scholarships / Fellowships ──
            'scholarships', 'scholarship', 'fellowships', 'fellowship',
            'grants', 'grant', 'bursaries', 'bursary',
            'scholarships and fellowships', 'scholarships and grants',
            # ── Academic honors ──
            "dean's list", 'dean list', 'honor roll', 'honours list',
            'graduated with honors', 'summa cum laude', 'magna cum laude',
            'cum laude', 'first class honors', 'first class honours',
            'distinction', 'merit award', 'gold medal', 'silver medal',
            'university gold medal', 'president gold medal',
            'chancellor award', 'vice chancellor award',
            'topper', 'class topper', 'batch topper', 'rank holder',
            # ── Competition ──
            'competitions', 'competition wins', 'contest wins',
            'hackathon wins', 'hackathon awards',
            'olympiad', 'olympiad awards', 'olympiad medals',
            # ── Corporate ──
            'employee awards', 'employee of the month', 'employee of the year',
            'best performer', 'star performer', 'outstanding performer',
            'performance awards', 'excellence awards',
            'leadership awards', 'innovation awards',
            # ── Regional ──
            'national awards', 'international awards', 'regional awards',
            'state awards', 'district awards',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 8. PUBLICATIONS
        # ════════════════════════════════════════════════════════════════════════
        'publications': [
            'publications', 'publication', 'published works', 'published work',
            'published papers', 'papers', 'paper',
            'research publications', 'academic publications',
            'scholarly publications', 'scientific publications',
            'peer-reviewed publications', 'peer reviewed publications',
            'refereed publications',
            'journal articles', 'journal publications', 'journal papers',
            'articles', 'article',
            'conference papers', 'conference publications',
            'conference proceedings', 'proceedings',
            'books', 'book', 'authored books', 'co-authored books',
            'book chapters', 'chapter', 'chapters',
            'edited volumes', 'edited books',
            'technical reports', 'reports', 'report',
            'working papers', 'discussion papers',
            'preprints', 'arxiv papers', 'manuscripts',
            'patents', 'patent', 'patent applications', 'intellectual property',
            'white papers', 'whitepapers', 'industry reports',
            'case studies published', 'published case studies',
            'media publications', 'press coverage', 'press',
            'blog posts', 'blog articles', 'technical blog posts',
            'technical writing', 'published articles', 'written works',
            'selected publications', 'recent publications', 'key publications',
            'notable publications',
            'dissertation', 'thesis', 'doctoral thesis', 'masters thesis',
            'research output', 'research outputs', 'scholarly output',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 9. PRESENTATIONS & TALKS
        # ════════════════════════════════════════════════════════════════════════
        'presentations': [
            'presentations', 'presentation', 'talks', 'talk',
            'speaking engagements', 'speaking engagement',
            'public speaking', 'public talks',
            'conference presentations', 'conference talks',
            'keynotes', 'keynote', 'keynote talks', 'keynote speeches',
            'keynote addresses', 'keynote speaker',
            'invited talks', 'invited lectures', 'invited presentations',
            'invited speaker', 'guest lectures', 'guest talks', 'guest speaker',
            'panel discussions', 'panels', 'panel appearances',
            'workshops delivered', 'workshops facilitated',
            'webinars', 'webinar presentations', 'online talks',
            'virtual presentations', 'virtual talks',
            'podcast appearances', 'podcasts', 'media appearances',
            'interviews', 'media interviews', 'press interviews',
            'lectures', 'lecture', 'lecturing',
            'seminars delivered', 'seminar presentations',
            'training delivered', 'training sessions delivered',
            'speaking', 'technical talks', 'lightning talks',
            'ted talks', 'tedx talks',
            'community talks', 'meetup talks', 'meetup presentations',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 10. RESEARCH
        # ════════════════════════════════════════════════════════════════════════
        'research': [
            'research', 'research experience', 'research work',
            'research background', 'research history',
            'research interests', 'current research', 'research overview',
            'research projects', 'research areas', 'areas of research',
            'research profile', 'research summary',
            'research contributions', 'research outputs',
            'scholarly work', 'academic research',
            'applied research', 'industry research', 'clinical research',
            'laboratory research', 'lab work', 'lab research',
            'experimental work', 'experimental research',
            'investigations', 'studies conducted', 'field research',
            'funded research', 'grant-funded research',
            'collaborative research', 'ongoing research',
            'completed research', 'research portfolio',
            'research activities', 'scholarly activities',
            'scientific research', 'medical research', 'biomedical research',
            'social research', 'market research', 'user research',
            'qualitative research', 'quantitative research',
            'mixed methods research',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 11. VOLUNTEERING / COMMUNITY
        # ════════════════════════════════════════════════════════════════════════
        'volunteering': [
            'volunteering', 'volunteer work', 'volunteer experience',
            'voluntary work', 'voluntary experience', 'voluntary service',
            'community involvement', 'community service', 'community work',
            'community engagement', 'community contributions',
            'civic engagement', 'civic involvement', 'civic activities',
            'social work', 'social activities',
            'nonprofit work', 'ngo work', 'charity work',
            'pro bono work', 'pro bono activities',
            'social responsibility', 'csr activities', 'csr',
            'outreach', 'outreach activities', 'outreach programs',
            'mentorship', 'mentoring', 'coaching activities',
            # ── Student ──
            'extracurricular activities', 'extracurricular', 'activities',
            'campus activities', 'campus involvement',
            'student leadership', 'student activities',
            'student organizations', 'student societies', 'student clubs',
            'clubs and activities', 'clubs and societies',
            'societies', 'clubs', 'organizations',
            'leadership activities', 'co-curricular activities', 'co-curricular',
            # ── UK / Commonwealth ──
            'voluntary and community work',
            'duke of edinburgh', 'national citizen service',
            # ── India / South Asia ──
            'social service', 'nss', 'ncc',
            'national service scheme', 'national cadet corps',
            'youth activities',
            # ── General ──
            'giving back', 'service', 'community leadership',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 12. LANGUAGES
        # ════════════════════════════════════════════════════════════════════════
        'languages': [
            'languages', 'language skills', 'foreign languages',
            'language proficiency', 'language abilities',
            'language competencies', 'language knowledge',
            'languages spoken', 'spoken languages',
            'bilingual', 'multilingual', 'trilingual',
            'natural languages', 'human languages',
            'linguistic skills', 'linguistic abilities',
            'languages known', 'known languages',
            'verbal languages', 'languages and proficiency',
            'language and communication skills',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 13. INTERESTS & HOBBIES
        # ════════════════════════════════════════════════════════════════════════
        'interests': [
            'interests', 'hobbies', 'hobbies and interests',
            'interests and hobbies', 'personal interests',
            'professional interests', 'areas of interest',
            'passions', 'activities', 'leisure activities',
            'personal activities', 'outside interests',
            'extracurricular interests', 'other interests',
            'sports and interests', 'sports and hobbies',
            'recreational activities', 'social interests',
            'personal pursuits', 'personal development interests',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 14. REFERENCES
        # ════════════════════════════════════════════════════════════════════════
        'references': [
            'references', 'reference', 'referees', 'referee',
            'professional references', 'character references',
            'personal references', 'academic references',
            'references available', 'references available on request',
            'references available upon request',
            'available upon request', 'upon request',
            'reference list', 'contact references',
            'referees available', 'referees available on request',
            'referees available upon request',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 15. CONTACT / PERSONAL INFORMATION
        # ════════════════════════════════════════════════════════════════════════
        'contact': [
            'contact', 'contact information', 'contact details', 'contact info',
            'personal information', 'personal details', 'personal data',
            'personal info', 'personal profile',
            'basic information', 'basic details',
            'candidate details', 'applicant details',
            'contact and personal', 'address', 'location',
            'my details', 'my information',
            'general information', 'general details',
            'profile information', 'profile details',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 16. AFFILIATIONS & MEMBERSHIPS
        # ════════════════════════════════════════════════════════════════════════
        'affiliations': [
            'affiliations', 'affiliation', 'professional affiliations',
            'memberships', 'membership',
            'professional memberships', 'industry memberships',
            'association memberships', 'society memberships',
            'board memberships', 'advisory roles', 'advisory positions',
            'committee memberships', 'committee roles',
            'organizations', 'professional organizations',
            'industry affiliations', 'academic affiliations',
            'institutional affiliations', 'research affiliations',
            'professional associations', 'professional bodies',
            'chartered bodies', 'regulatory bodies',
            'trade associations', 'industry bodies',
            'networks', 'professional networks',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 17. PATENTS & INTELLECTUAL PROPERTY
        # ════════════════════════════════════════════════════════════════════════
        'patents': [
            'patents', 'patent', 'patent applications',
            'intellectual property', 'ip',
            'inventions', 'invention',
            'trademarks', 'trademark',
            'copyrights', 'copyright',
            'patents and publications',
            'patents filed', 'patents granted',
            'patent portfolio',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 18. TEACHING & MENTORING
        # ════════════════════════════════════════════════════════════════════════
        'teaching': [
            'teaching', 'teaching experience', 'teaching history',
            'teaching positions', 'teaching roles',
            'courses taught', 'subjects taught', 'modules taught',
            'teaching and mentoring', 'mentoring',
            'mentoring experience', 'mentorship',
            'coaching', 'coaching experience',
            'tutoring', 'tutoring experience',
            'academic teaching', 'university teaching',
            'college teaching', 'school teaching',
            'faculty teaching', 'lecturing',
            'guest lecturing', 'guest teaching',
            'training and coaching',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 19. GRANTS & FUNDING
        # ════════════════════════════════════════════════════════════════════════
        'grants': [
            'grants', 'grant', 'funding', 'research funding',
            'research grants', 'grants and funding',
            'grants and fellowships', 'fellowships and grants',
            'awards and grants', 'grants awarded',
            'funded projects', 'externally funded projects',
            'research awards', 'competitive grants',
            'industry funding', 'government grants',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 20. PROFESSIONAL DEVELOPMENT
        # ════════════════════════════════════════════════════════════════════════
        'professional_development': [
            'professional development', 'personal development',
            'continuing professional development', 'cpd',
            'continuing education', 'ongoing education',
            'learning and development', 'l&d',
            'training and development', 't&d',
            'upskilling', 'reskilling',
            'self development', 'self-development',
            'growth', 'personal growth', 'professional growth',
            'career development', 'career learning',
            'workshops and seminars', 'conferences attended',
            'events attended',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 21. LEADERSHIP & MANAGEMENT
        # ════════════════════════════════════════════════════════════════════════
        'leadership': [
            'leadership', 'leadership experience', 'leadership roles',
            'leadership positions', 'management', 'management experience',
            'management roles', 'management positions',
            'team leadership', 'team management',
            'people management', 'staff management',
            'executive leadership', 'senior leadership',
            'organizational leadership', 'strategic leadership',
            'leadership and management',
            'supervisory experience', 'supervision experience',
            'line management', 'direct management',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 22. ADDITIONAL / MISCELLANEOUS
        # ════════════════════════════════════════════════════════════════════════
        'additional': [
            'additional information', 'additional details',
            'other information', 'other details',
            'miscellaneous', 'misc',
            'supplementary information', 'supplementary details',
            'extra information', 'extra details',
            'further information', 'further details',
            'appendix', 'notes', 'remarks',
            'other', 'others',
            'additional skills', 'other skills',
            'additional experience', 'other experience',
            'additional qualifications', 'other qualifications',
            'additional achievements',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 23. OBJECTIVE / CAREER GOALS
        # ════════════════════════════════════════════════════════════════════════
        'objective': [
            'objective', 'career objective', 'job objective',
            'professional objective', 'personal objective',
            'career goals', 'career goal', 'goals',
            'aims', 'aims and objectives',
            'mission', 'mission statement',
            'vision', 'career vision',
            'aspiration', 'aspirations', 'career aspiration',
            'what i am looking for', 'what i am seeking',
            'seeking', 'looking for',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 24. PORTFOLIO / WORK SAMPLES
        # ════════════════════════════════════════════════════════════════════════
        'portfolio': [
            'portfolio', 'work portfolio', 'design portfolio',
            'creative portfolio', 'professional portfolio',
            'work samples', 'samples', 'sample work',
            'selected works', 'selected work', 'representative work',
            'creative works', 'creative work', 'art work', 'artwork',
            'showreel', 'reel', 'demo reel', 'creative reel',
            'case studies', 'case study',
            'featured work', 'key work', 'notable work',
            'gallery', 'exhibit', 'exhibition',
            'writing samples', 'code samples',
        ],

        # ════════════════════════════════════════════════════════════════════════
        # 25. MILITARY SERVICE
        # ════════════════════════════════════════════════════════════════════════
        'military': [
            'military service', 'military experience', 'military history',
            'armed forces', 'armed forces service',
            'defense service', 'national service',
            'military background', 'service record',
            'military career', 'army', 'navy', 'air force',
            'marines', 'coast guard',
            'military awards', 'service medals',
            'deployment history', 'deployments',
            'military training', 'military education',
        ],
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pre-compile patterns for better performance
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex patterns for section detection."""
        
        # Pattern for section headers (ALL CAPS or with special formatting)
        self.section_header_pattern = re.compile(
            r'^\s*([A-Z][A-Z\s]{2,}|[A-Za-z][A-Za-z\s&/-]{3,})\s*[:\-=_]*\s*$',
            re.MULTILINE
        )
        
        # Pattern for dates in experience sections
        self.date_pattern = re.compile(
            r'\b(?:\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s*\d{4}|\d{4})\b',
            re.IGNORECASE
        )
        
        # Pattern for company indicators
        self.company_pattern = re.compile(
            r'(?:at|@)\s+([A-Za-z0-9\s&.,\-]+)|^([A-Za-z0-9\s&.,\-]{3,})\s*[\|\-•]',
            re.MULTILINE
        )
        
        # Pattern for bullet points and descriptions
        self.bullet_pattern = re.compile(
            r'^[\s]*[•\-\*\+]\s*(.+)$',
            re.MULTILINE
        )
    
    def _clean_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts that break section detection."""
        # Remove cid: font encoding artifacts
        text = re.sub(r'\(cid:\d+\)', '', text)
        # Normalize runs of 3+ spaces to newlines (multi-column PDF artifacts)
        text = re.sub(r' {3,}', '\n', text)
        # Remove zero-width and other invisible characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        return text

    def split_sections(self, text: str) -> Dict[str, str]:
        """
        Detect section headers and split text into named sections.
        
        Args:
            text: Resume text to split into sections
            
        Returns:
            Dictionary with section names as keys and section text as values
        """
        try:
            text = self._clean_pdf_artifacts(text)
            sections = {}
            current_section = 'other'
            current_content = []
            
            lines = text.split('\n')
            
            for line in lines:
                stripped_line = line.strip()
                
                # Check if this line is a section header
                section_name = self.detect_section_header(stripped_line)
                
                if section_name:
                    # Save previous section content
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    self.logger.debug(f"Found section header: {section_name}")
                    
                else:
                    # Add line to current section content
                    if stripped_line or current_content:  # Preserve empty lines within sections
                        current_content.append(line)
            
            # Save the last section
            if current_content:
                sections[current_section] = '\n'.join(current_content).strip()
            
            # Log section detection results
            self.logger.info(f"Split resume into {len(sections)} sections: {list(sections.keys())}")
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Error splitting sections: {e}")
            return {'other': text}
    
    def detect_section_header(self, line: str) -> Optional[str]:
        """
        Check if a line is a section header and return the section name.
        
        Args:
            line: Line to check for section header
            
        Returns:
            Matched section name or None
        """
        try:
            if not line or len(line.strip()) < 3:
                return None
            
            # Remove extra whitespace and check patterns
            clean_line = line.strip()
            
            # Check for ALL CAPS headers (more permissive)
            if clean_line.isupper() and len(clean_line) > 2:
                return self._match_section_keywords(clean_line.lower())
            
            # Check for headers with special characters
            if any(char in clean_line for char in [':', '-', '=', '_', '|']):
                header_text = re.sub(r'[:\-=_\|\s]+$', '', clean_line).strip()
                return self._match_section_keywords(header_text.lower())
            
            # Check for Title Case headers with common section words
            if any(word in clean_line.lower() for word in ['experience', 'education', 'skills', 'summary', 'projects', 'certifications']):
                return self._match_section_keywords(clean_line.lower())
            
            # Check for title case headers
            if clean_line.istitle() and len(clean_line.split()) <= 5:
                return self._match_section_keywords(clean_line.lower())
            
            # Check against section keywords directly
            keyword_result = self._match_section_keywords(clean_line.lower())
            if keyword_result:
                return keyword_result
            
            # No keyword matched — try semantic matching as fallback
            semantic_result = self.detect_section_header_semantic(clean_line)
            if semantic_result:
                return semantic_result

            return None
            
        except Exception as e:
            self.logger.error(f"Error detecting section header: {e}")
            return None
    
    def detect_section_header_semantic(self, line: str) -> str | None:
        """
        Fallback: when no keyword matches, use sentence similarity
        to classify the heading against section prototypes.
        """
        try:
            from sentence_transformers import SentenceTransformer, util
            import torch

            # Lazy load — only instantiate once
            if not hasattr(self, '_semantic_model'):
                self._semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                self._section_prototypes = {
                    'experience':            'Work experience employment career history jobs positions',
                    'education':             'Education academic degree university college school qualifications',
                    'skills':                'Technical skills tools technologies competencies expertise abilities',
                    'summary':               'Professional summary objective profile about me introduction overview',
                    'projects':              'Projects portfolio personal work open source contributions capstone',
                    'certifications':        'Certifications licenses training courses certificates credentials',
                    'awards':                'Awards honors achievements recognition distinctions scholarships prizes',
                    'publications':          'Publications papers articles books patents research outputs',
                    'presentations':         'Presentations talks conferences keynotes speaking engagements',
                    'research':              'Research laboratory experiments investigations scholarly work',
                    'volunteering':          'Volunteering community service extracurricular activities',
                    'languages':             'Languages spoken foreign bilingual multilingual proficiency',
                    'interests':             'Hobbies interests personal activities passions leisure',
                    'references':            'References referees contact available upon request',
                    'contact':               'Contact personal information address phone email details',
                    'affiliations':          'Affiliations memberships organizations professional societies',
                    'patents':               'Patents inventions intellectual property trademarks',
                    'teaching':              'Teaching mentoring tutoring coaching lecturing courses taught',
                    'grants':                'Grants funding fellowships research funding awarded',
                    'professional_development': 'Professional development CPD continuing education learning',
                    'leadership':            'Leadership management team management executive roles',
                    'additional':            'Additional information miscellaneous other details',
                    'objective':             'Career objective goals aims mission aspirations seeking',
                    'portfolio':             'Portfolio work samples creative works showreel gallery',
                    'military':              'Military service armed forces national service defense',
                }
                self._prototype_embeddings = {
                    k: self._semantic_model.encode(v, convert_to_tensor=True)
                    for k, v in self._section_prototypes.items()
                }

            line_embedding = self._semantic_model.encode(line, convert_to_tensor=True)
            best_section = None
            best_score = 0.0

            for section_name, proto_emb in self._prototype_embeddings.items():
                score = float(util.cos_sim(line_embedding, proto_emb))
                if score > best_score:
                    best_score = score
                    best_section = section_name

            # Only use semantic match if confidence is high enough
            if best_score > 0.55:
                return best_section

            return None

        except Exception:
            return None
    
    def _match_section_keywords(self, text: str) -> Optional[str]:
        """
        Match text against section keywords.
        
        Args:
            text: Text to match against keywords
            
        Returns:
            Section name if matched, None otherwise
        """
        # Clean the input text - strip whitespace and punctuation
        clean_text = text.strip()
        clean_text = re.sub(r'[:\-=_\s]+$', '', clean_text)  # Remove trailing punctuation
        text_lower = clean_text.lower()
        
        for section_name, keywords in self.SECTION_KEYWORDS.items():
            for keyword in keywords:
                keyword_clean = keyword.lower().strip()
                # Check for exact match or partial match
                if keyword_clean == text_lower or keyword_clean in text_lower or text_lower in keyword_clean:
                    return section_name
        
        return None
    
    def extract_experience_blocks(self, experience_text: str) -> List[Dict[str, str]]:
        """
        Split experience section into individual job blocks.
        
        Args:
            experience_text: Text from the experience section
            
        Returns:
            List of job experience dictionaries
        """
        try:
            if not experience_text or not experience_text.strip():
                return []
            
            jobs = []
            
            # Split by common job separators
            job_blocks = self._split_into_job_blocks(experience_text)
            
            for block in job_blocks:
                job_info = self._parse_job_block(block)
                if job_info:
                    jobs.append(job_info)
            
            self.logger.info(f"Extracted {len(jobs)} job blocks from experience section")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error extracting experience blocks: {e}")
            return []
    
    def _split_into_job_blocks(self, text: str) -> List[str]:
        """
        Split experience text into individual job blocks.
        
        Args:
            text: Experience section text
            
        Returns:
            List of job blocks
        """
        # Common patterns that indicate new job entries
        job_separators = [
            r'\n\s*[A-Z][a-z]+\s+\d{4}\s*[-–—]\s*(?:Present|Current|\d{4})',  # Date ranges
            r'\n\s*[A-Z][A-Za-z\s&.,\-]{3,}\s*\n',  # Company names
            r'\n\s*[\w\s]+(?:Engineer|Developer|Manager|Director|Analyst|Specialist|Consultant)',  # Job titles
        ]
        
        # Create combined pattern
        combined_pattern = '|'.join(job_separators)
        
        # Split by the pattern, keeping the separators
        parts = re.split(combined_pattern, text, flags=re.MULTILINE)
        
        # Filter out empty parts and trim
        job_blocks = [part.strip() for part in parts if part.strip()]
        
        return job_blocks
    
    def _parse_job_block(self, block: str) -> Optional[Dict[str, str]]:
        """
        Parse a single job block into structured information.
        
        Args:
            block: Job block text
            
        Returns:
            Dictionary with job information
        """
        try:
            lines = block.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                return None
            
            job_info = {
                'title': '',
                'company': '',
                'dates': '',
                'description': ''
            }
            
            # Extract job title (usually first line)
            if lines:
                job_info['title'] = lines[0]
            
            # Extract dates and company from remaining lines
            description_lines = []
            
            for i, line in enumerate(lines[1:], 1):
                # Check for dates
                if self.date_pattern.search(line) and not job_info['dates']:
                    job_info['dates'] = line
                    continue
                
                # Check for company (usually contains "at" or is in all caps)
                if ('at' in line.lower() or line.isupper()) and not job_info['company']:
                    # Clean up company name
                    company = re.sub(r'^(?:at|@)\s*', '', line, flags=re.IGNORECASE)
                    company = re.sub(r'[\|\-•].*$', '', company).strip()
                    if company:
                        job_info['company'] = company
                        continue
                
                # Add to description
                description_lines.append(line)
            
            # Combine description lines
            job_info['description'] = '\n'.join(description_lines)
            
            # If no company found, try to extract from title line
            if not job_info['company'] and job_info['title']:
                company_match = re.search(r'(?:at|@)\s+([A-Za-z0-9\s&.,\-]+)', job_info['title'], re.IGNORECASE)
                if company_match:
                    job_info['company'] = company_match.group(1).strip()
                    # Remove company from title
                    job_info['title'] = re.sub(r'\s*(?:at|@)\s+[A-Za-z0-9\s&.,\-]+', '', job_info['title'], flags=re.IGNORECASE).strip()
            
            return job_info if job_info['title'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing job block: {e}")
            return None
    
    def extract_education_blocks(self, education_text: str) -> List[Dict[str, str]]:
        """
        Split education section into individual education blocks.
        
        Args:
            education_text: Text from the education section
            
        Returns:
            List of education dictionaries
        """
        try:
            if not education_text or not education_text.strip():
                return []
            
            education_items = []
            
            # Split by common education separators
            edu_blocks = re.split(r'\n(?=[A-Z][a-zA-Z\s]+(?:University|College|Institute|School))', education_text)
            
            for block in edu_blocks:
                edu_info = self._parse_education_block(block)
                if edu_info:
                    education_items.append(edu_info)
            
            self.logger.info(f"Extracted {len(education_items)} education blocks")
            return education_items
            
        except Exception as e:
            self.logger.error(f"Error extracting education blocks: {e}")
            return []
    
    def _parse_education_block(self, block: str) -> Optional[Dict[str, str]]:
        """
        Parse a single education block into structured information.
        
        Args:
            block: Education block text
            
        Returns:
            Dictionary with education information
        """
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            
            if not lines:
                return None
            
            edu_info = {
                'degree': '',
                'institution': '',
                'dates': '',
                'details': ''
            }
            
            # Extract institution (usually contains University, College, etc.)
            for line in lines:
                if any(keyword in line.lower() for keyword in ['university', 'college', 'institute', 'school']):
                    edu_info['institution'] = line
                    break
            
            # Extract degree (usually first line or contains degree keywords)
            degree_keywords = ['bachelor', 'master', 'phd', 'doctor', 'associate', 'diploma', 'certificate']
            for line in lines:
                if any(keyword in line.lower() for keyword in degree_keywords):
                    edu_info['degree'] = line
                    break
            
            # Extract dates
            for line in lines:
                if self.date_pattern.search(line):
                    edu_info['dates'] = line
                    break
            
            # Remaining lines go to details
            details = [line for line in lines if line not in [
                edu_info['degree'], edu_info['institution'], edu_info['dates']
            ]]
            edu_info['details'] = '\n'.join(details)
            
            return edu_info if edu_info['institution'] or edu_info['degree'] else None
            
        except Exception as e:
            self.logger.error(f"Error parsing education block: {e}")
            return None
    
    def extract_skills_from_section(self, skills_text: str) -> List[str]:
        """
        Extract individual skills from skills section.
        
        Args:
            skills_text: Text from the skills section
            
        Returns:
            List of individual skills
        """
        try:
            if not skills_text:
                return []
            
            skills = []
            
            # Split by common separators
            skill_parts = re.split(r'[,;•\n]', skills_text)
            
            for part in skill_parts:
                skill = part.strip()
                
                # Remove common prefixes
                skill = re.sub(r'^(?:•|\-|\*|\+)\s*', '', skill)
                skill = re.sub(r'^(?:skills?|technologies?|tools?|competencies?):\s*', '', skill, flags=re.IGNORECASE)
                
                # Clean up and filter
                if skill and len(skill) > 1 and len(skill) < 50:
                    skills.append(skill)
            
            # Remove duplicates and sort
            unique_skills = sorted(list(set(skill.lower() for skill in skills)))
            
            self.logger.info(f"Extracted {len(unique_skills)} skills from skills section")
            return unique_skills
            
        except Exception as e:
            self.logger.error(f"Error extracting skills from section: {e}")
            return []
    
    def get_section_statistics(self, sections: Dict[str, str]) -> Dict[str, int]:
        """
        Get statistics about the parsed sections.
        
        Args:
            sections: Dictionary of sections
            
        Returns:
            Dictionary with section statistics
        """
        try:
            stats = {}
            
            for section_name, section_text in sections.items():
                if section_text:
                    word_count = len(section_text.split())
                    char_count = len(section_text)
                    line_count = len(section_text.split('\n'))
                    
                    stats[section_name] = {
                        'word_count': word_count,
                        'char_count': char_count,
                        'line_count': line_count
                    }
                else:
                    stats[section_name] = {
                        'word_count': 0,
                        'char_count': 0,
                        'line_count': 0
                    }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error calculating section statistics: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    # Sample resume text for testing
    sample_resume = """
    John Doe
    Software Engineer
    
    SUMMARY
    Experienced software engineer with 5+ years of experience in full-stack development.
    
    EXPERIENCE
    Senior Software Engineer at Tech Corp
    Jan 2020 - Present
    • Developed scalable web applications using React and Node.js
    • Led a team of 3 junior developers
    • Improved application performance by 40%
    
    Software Developer at StartupXYZ
    Jun 2018 - Dec 2019
    • Built RESTful APIs and microservices
    • Worked with Agile methodology
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology
    2014 - 2018
    
    SKILLS
    • JavaScript, Python, Java
    • React, Node.js, Express
    • MongoDB, PostgreSQL
    • Docker, AWS, Git
    """
    
    splitter = SectionSplitter()
    
    # Test section splitting
    sections = splitter.split_sections(sample_resume)
    print("Sections found:", list(sections.keys()))
    
    # Test experience extraction
    if 'experience' in sections:
        experience_blocks = splitter.extract_experience_blocks(sections['experience'])
        print(f"\nExperience blocks ({len(experience_blocks)}):")
        for i, job in enumerate(experience_blocks, 1):
            print(f"{i}. {job['title']} at {job['company']}")
    
    # Test education extraction
    if 'education' in sections:
        education_blocks = splitter.extract_education_blocks(sections['education'])
        print(f"\nEducation blocks ({len(education_blocks)}):")
        for i, edu in enumerate(education_blocks, 1):
            print(f"{i}. {edu['degree']} from {edu['institution']}")
    
    # Test skills extraction
    if 'skills' in sections:
        skills = splitter.extract_skills_from_section(sections['skills'])
        print(f"\nSkills ({len(skills)}): {', '.join(skills)}")
    
    # Test section statistics
    stats = splitter.get_section_statistics(sections)
    print(f"\nSection statistics:")
    for section, stat in stats.items():
        print(f"{section}: {stat['word_count']} words, {stat['line_count']} lines")

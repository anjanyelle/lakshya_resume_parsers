"""
Education Normalizer with Abbreviation Handling and Institution Matching
Provides intelligent education institution normalization and degree classification
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set
from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

class EducationNormalizer:
    """
    Advanced education normalizer with abbreviation handling,
    institution matching, and degree classification
    """
    
    def __init__(self, education_data: Dict):
        self.education_data = education_data
        
        # Build search indexes
        self.institution_index = self._build_institution_index()
        self.country_index = self._build_country_index()
        
        # University abbreviations and variations
        self.abbreviations = self._build_abbreviations()
        self.variations = self._build_variations()
        
        # Degree patterns and classifications
        self.degree_patterns = self._build_degree_patterns()
        self.degree_levels = self._build_degree_levels()
        
        # Common misspellings and corrections
        self.misspellings = self._build_misspellings()
        
        # Geographic and ranking patterns
        self.geographic_patterns = self._build_geographic_patterns()
        
        logger.info(f"EducationNormalizer initialized with {len(education_data)} institutions")
    
    def _build_institution_index(self) -> List[str]:
        """Build searchable index of institution names"""
        return list(self.education_data.keys())
    
    def _build_country_index(self) -> Dict[str, List[str]]:
        """Build index of institutions by country"""
        country_index = {}
        
        for institution_key, institution_data in self.education_data.items():
            country = institution_data.get('country', '').lower()
            if country:
                if country not in country_index:
                    country_index[country] = []
                country_index[country].append(institution_key)
        
        return country_index
    
    def _build_abbreviations(self) -> Dict[str, str]:
        """Build comprehensive abbreviation mappings"""
        return {
            # US Universities
            'mit': 'Massachusetts Institute of Technology',
            'caltech': 'California Institute of Technology',
            'ucla': 'University of California Los Angeles',
            'uc berkeley': 'University of California Berkeley',
            'ucsd': 'University of California San Diego',
            'uc davis': 'University of California Davis',
            'uc irvine': 'University of California Irvine',
            'ucsb': 'University of California Santa Barbara',
            'ucr': 'University of California Riverside',
            'ucsc': 'University of California Santa Cruz',
            'ucsf': 'University of California San Francisco',
            'ucsb': 'University of California Santa Barbara',
            'ucm': 'University of California Merced',
            'ut austin': 'University of Texas Austin',
            'ut dallas': 'University of Texas Dallas',
            'ut houston': 'University of Texas Houston',
            'ut arlington': 'University of Texas Arlington',
            'ut san antonio': 'University of Texas San Antonio',
            'uw madison': 'University of Wisconsin Madison',
            'uw milwaukee': 'University of Wisconsin Milwaukee',
            'um ann arbor': 'University of Michigan Ann Arbor',
            'msu': 'Michigan State University',
            'uiuc': 'University of Illinois Urbana-Champaign',
            'uic': 'University of Illinois Chicago',
            'unc chapel hill': 'University of North Carolina Chapel Hill',
            'unc charlotte': 'University of North Carolina Charlotte',
            'unc greensboro': 'University of North Carolina Greensboro',
            'um twin cities': 'University of Minnesota Twin Cities',
            'um duluth': 'University of Minnesota Duluth',
            'cu boulder': 'University of Colorado Boulder',
            'cu colorado springs': 'University of Colorado Colorado Springs',
            'umd college park': 'University of Maryland College Park',
            'um baltimore': 'University of Maryland Baltimore',
            'ua tucson': 'University of Arizona',
            'asu': 'Arizona State University',
            'uf gainesville': 'University of Florida',
            'fsu': 'Florida State University',
            'ucf': 'University of Central Florida',
            'usf': 'University of South Florida',
            'fiu': 'Florida International University',
            'ur rochester': 'University of Rochester',
            'ub buffalo': 'University at Buffalo',
            'usc los angeles': 'University of Southern California',
            'uva charlottesville': 'University of Virginia',
            'vt blacksburg': 'Virginia Tech',
            'w&m': 'William & Mary',
            'u utah': 'University of Utah',
            'usu': 'Utah State University',
            'upitt': 'University of Pittsburgh',
            'penn state': 'Pennsylvania State University',
            'temple': 'Temple University',
            'drexel': 'Drexel University',
            'bu boston': 'Boston University',
            'bc': 'Boston College',
            'northeastern': 'Northeastern University',
            'tufts': 'Tufts University',
            'brandeis': 'Brandeis University',
            'osu columbus': 'Ohio State University',
            'ou': 'Ohio University',
            'miami university': 'Miami University',
            'uga athens': 'University of Georgia',
            'georgia tech': 'Georgia Institute of Technology',
            'ua tuscaloosa': 'University of Alabama',
            'auburn': 'Auburn University',
            'u arkansas': 'University of Arkansas',
            'u hawaii': 'University of Hawaii',
            'u idaho': 'University of Idaho',
            'u iowa': 'University of Iowa',
            'iowa state': 'Iowa State University',
            'u kansas': 'University of Kansas',
            'ku': 'University of Kansas',
            'kansas state': 'Kansas State University',
            'u kentucky': 'University of Kentucky',
            'uk': 'University of Kentucky',
            'u louisiana': 'Louisiana State University',
            'lsu': 'Louisiana State University',
            'u maine': 'University of Maine',
            'u mass': 'University of Massachusetts',
            'umass amherst': 'University of Massachusetts Amherst',
            'umiss': 'University of Mississippi',
            'ole miss': 'University of Mississippi',
            'u missouri': 'University of Missouri',
            'mizzou': 'University of Missouri',
            'u montana': 'University of Montana',
            'unl': 'University of Nebraska Lincoln',
            'u nevada': 'University of Nevada',
            'unr': 'University of Nevada Reno',
            'u new hampshire': 'University of New Hampshire',
            'dartmouth': 'Dartmouth College',
            'u new mexico': 'University of New Mexico',
            'unm': 'University of New Mexico',
            'u north dakota': 'University of North Dakota',
            'u oklahoma': 'University of Oklahoma',
            'u oregon': 'University of Oregon',
            'osu': 'Oregon State University',
            'u rhode island': 'University of Rhode Island',
            'u south carolina': 'University of South Carolina',
            'u south dakota': 'University of South Dakota',
            'u tennessee': 'University of Tennessee',
            'ut': 'University of Tennessee',
            'u vermont': 'University of Vermont',
            'u virginia': 'University of Virginia',
            'u washington': 'University of Washington',
            'washington state': 'Washington State University',
            'u west virginia': 'University of West Virginia',
            'wvu': 'West Virginia University',
            'u wyoming': 'University of Wyoming',
            'u alaska': 'University of Alaska',
            'u connecticut': 'University of Connecticut',
            'u delaware': 'University of Delaware',
            'georgetown': 'Georgetown University',
            'gw': 'George Washington University',
            'american': 'American University',
            'howard': 'Howard University',
            'catholic': 'Catholic University',
            
            # Ivy League
            'harvard': 'Harvard University',
            'yale': 'Yale University',
            'princeton': 'Princeton University',
            'columbia': 'Columbia University',
            'brown': 'Brown University',
            'dartmouth': 'Dartmouth College',
            'cornell': 'Cornell University',
            'upenn': 'University of Pennsylvania',
            
            # UK Universities
            'oxford': 'University of Oxford',
            'cambridge': 'University of Cambridge',
            'ucl': 'University College London',
            'imperial': 'Imperial College London',
            'lse': 'London School of Economics',
            'kcl': "King's College London",
            'edinburgh': 'University of Edinburgh',
            'manchester': 'University of Manchester',
            'warwick': 'University of Warwick',
            'bristol': 'University of Bristol',
            'glasgow': 'University of Glasgow',
            'nottingham': 'University of Nottingham',
            'sheffield': 'University of Sheffield',
            'leeds': 'University of Leeds',
            'birmingham': 'University of Birmingham',
            'southampton': 'University of Southampton',
            'liverpool': 'University of Liverpool',
            'newcastle': 'University of Newcastle',
            'durham': 'University of Durham',
            'exeter': 'University of Exeter',
            'york': 'University of York',
            'queen mary': 'Queen Mary University of London',
            
            # Canadian Universities
            'toronto': 'University of Toronto',
            'ubc': 'University of British Columbia',
            'mcgill': 'McGill University',
            'mcmaster': 'McMaster University',
            'waterloo': 'University of Waterloo',
            'western': 'Western University',
            'queen': "Queen's University",
            'alberta': 'University of Alberta',
            'calgary': 'University of Calgary',
            'ottawa': 'University of Ottawa',
            'simon fraser': 'Simon Fraser University',
            'victoria': 'University of Victoria',
            'dalhousie': 'Dalhousie University',
            'memorial': 'Memorial University',
            
            # Australian Universities
            'anu': 'Australian National University',
            'melbourne': 'University of Melbourne',
            'sydney': 'University of Sydney',
            'unsw': 'University of New South Wales',
            'uq': 'University of Queensland',
            'monash': 'Monash University',
            'uwa': 'University of Western Australia',
            'adelaide': 'University of Adelaide',
            'uts': 'University of Technology Sydney',
            'rmit': 'RMIT University',
            'deakin': 'Deakin University',
            'griffith': 'Griffith University',
            'latrobe': 'La Trobe University',
            'newcastle': 'University of Newcastle',
            'wollongong': 'University of Wollongong',
            'queensland': 'Queensland University of Technology',
            'curtin': 'Curtin University',
            'flinders': 'Flinders University',
            'bond': 'Bond University',
            'notre dame': 'University of Notre Dame Australia',
            
            # Asian Universities
            'nus': 'National University of Singapore',
            'ntu': 'Nanyang Technological University',
            'smu': 'Singapore Management University',
            'tsinghua': 'Tsinghua University',
            'peking': 'Peking University',
            'fudan': 'Fudan University',
            'shanghai jiao tong': 'Shanghai Jiao Tong University',
            'zhejiang': 'Zhejiang University',
            'nanjing': 'Nanjing University',
            'wuhan': 'Wuhan University',
            'hkust': 'Hong Kong University of Science and Technology',
            'hku': 'University of Hong Kong',
            'cuhk': 'Chinese University of Hong Kong',
            'cityu': 'City University of Hong Kong',
            'hkbu': 'Hong Kong Baptist University',
            'tokyo': 'University of Tokyo',
            'kyoto': 'Kyoto University',
            'osaka': 'Osaka University',
            'tohoku': 'Tohoku University',
            'nagoya': 'Nagoya University',
            'hokkaido': 'Hokkaido University',
            'kaist': 'Korea Advanced Institute of Science and Technology',
            'seoul national': 'Seoul National University',
            'yonsei': 'Yonsei University',
            'korea university': 'Korea University',
            'nctu': 'National Chiao Tung University',
            'ntu': 'National Taiwan University',
            'thammasat': 'Thammasat University',
            'chulalongkorn': 'Chulalongkorn University',
            'mahidol': 'Mahidol University',
            'iit': 'Indian Institute of Technology',
            'iit bombay': 'Indian Institute of Technology Bombay',
            'iit delhi': 'Indian Institute of Technology Delhi',
            'iit madras': 'Indian Institute of Technology Madras',
            'iit kanpur': 'Indian Institute of Technology Kanpur',
            'iit kharagpur': 'Indian Institute of Technology Kharagpur',
            
            # European Universities
            'eth zurich': 'ETH Zurich',
            'epfl': 'École Polytechnique Fédérale de Lausanne',
            'sorbonne': 'Sorbonne University',
            'paris-saclay': 'Paris-Saclay University',
            'lmu munich': 'Ludwig Maximilian University of Munich',
            'heidelberg': 'Heidelberg University',
            'tum': 'Technical University of Munich',
            'humboldt': 'Humboldt University of Berlin',
            'frei universität': 'Free University of Berlin',
            'tu berlin': 'Technical University of Berlin',
            'leiden': 'Leiden University',
            'utrecht': 'Utrecht University',
            'wageningen': 'Wageningen University',
            'erasmus': 'Erasmus University Rotterdam',
            'tilburg': 'Tilburg University',
            'groningen': 'University of Groningen',
            'amsterdam': 'University of Amsterdam',
            'lund': 'Lund University',
            'uppsala': 'Uppsala University',
            'stockholm': 'Stockholm University',
            'chalmers': 'Chalmers University of Technology',
            'kth': 'KTH Royal Institute of Technology',
            'helsinki': 'University of Helsinki',
            'aalto': 'Aalto University',
            'copenhagen': 'University of Copenhagen',
            'aarhus': 'Aarhus University',
            'technical university of denmark': 'Technical University of Denmark',
            'warsaw': 'University of Warsaw',
            'jagiellonian': 'Jagiellonian University',
            'charles': 'Charles University',
            'masaryk': 'Masaryk University',
            'comenius': 'Comenius University',
            'eötvös loránd': 'Eötvös Loránd University',
            'university of barcelona': 'University of Barcelona',
            'autonomous university of barcelona': 'Autonomous University of Barcelona',
            'complutense': 'Complutense University of Madrid',
            'autonomous university of madrid': 'Autonomous University of Madrid',
            'university of lisbon': 'University of Lisbon',
            'university of porto': 'University of Porto',
            'university of coimbra': 'University of Coimbra',
            'sapienza': 'Sapienza University of Rome',
            'university of milan': 'University of Milan',
            'university of bologna': 'University of Bologna',
            'university of padua': 'University of Padua',
            'university of naples': 'University of Naples',
            'university of turin': 'University of Turin',
            'university of pisa': 'University of Pisa',
            'politecnico di milano': 'Politecnico di Milano',
            'politecnico di torino': 'Politecnico di Torino'
        }
    
    def _build_variations(self) -> Dict[str, List[str]]:
        """Build common institution name variations"""
        return {
            'state university': ['state university', 'state u', 'state college'],
            'university of': ['university of', 'u of', 'univ of'],
            'college of': ['college of', 'college'],
            'institute of': ['institute of', 'institute', 'inst of'],
            'polytechnic': ['polytechnic', 'polytech'],
            'technical': ['technical', 'tech', 'technical university'],
            'national': ['national', 'nat\'l'],
            'international': ['international', 'intl', 'int\'l'],
            'community': ['community', 'comm'],
            'junior': ['junior', 'jr'],
            'liberal arts': ['liberal arts', 'liberal arts college'],
            'medical': ['medical', 'med', 'medical school'],
            'law': ['law', 'law school', 'school of law'],
            'business': ['business', 'business school', 'school of business'],
            'engineering': ['engineering', 'eng', 'school of engineering'],
            'arts': ['arts', 'school of arts'],
            'science': ['science', 'school of science'],
            'medicine': ['medicine', 'school of medicine'],
            'education': ['education', 'school of education'],
            'nursing': ['nursing', 'school of nursing'],
            'pharmacy': ['pharmacy', 'school of pharmacy'],
            'public health': ['public health', 'school of public health'],
            'social work': ['social work', 'school of social work'],
            'architecture': ['architecture', 'school of architecture'],
            'design': ['design', 'school of design'],
            'music': ['music', 'school of music', 'conservatory'],
            'fine arts': ['fine arts', 'school of fine arts'],
            'journalism': ['journalism', 'school of journalism'],
            'communication': ['communication', 'school of communication']
        }
    
    def _build_degree_patterns(self) -> Dict[str, str]:
        """Build degree pattern mappings"""
        return {
            'bachelor': r'\b(bachelor|b\.|b\.s\.|bs|b\.a\.|ba|beng|bcom|bba|bsc|btech|b\.tech|b\.eng|b\.arch|b\.des|b\.fa|b\.mus|b\.ed|b\.sw|b\.pharm|b\.nurs|ll\.b)\b',
            'master': r'\b(master|m\.|m\.s\.|ms|m\.a\.|ma|meng|mcom|mba|msc|mtech|m\.tech|m\.eng|m\.arch|m\.des|m\.fa|m\.mus|m\.ed|m\.sw|m\.pharm|m\.nurs|ll\.m|m\.phil|m\.res|m\.cs|m\.eng|m\.math|m\.phys|m\.chem|m\.bio|m\.geol|m\.psych|m\.sociol|m\.econ|m\.pol|m\.hist|m\.phil|m\.lit|m\.ling|m\.comp|m\.bus|m\.acc|m\.fin|m\.hr|m\.mkt|m\.ib|m\.is|m\.pm|m\.ha|m\.t|m\.env|m\.urb|m\.plan|m\.arch|m\.des|m\.fa|m\.mus|m\.ed|m\.sw|m\.pharm|m\.nurs|pgdm|pgdbm)\b',
            'doctorate': r'\b(doctor|ph\.d|phd|doctorate|doctoral|d\.phil|d\.tech|d\.eng|d\.arch|d\.des|d\.fa|d\.mus|d\.ed|d\.sw|d\.pharm|d\.nurs|j\.d|j\.d\.|md|m\.d|m\.d\.|d\.b\.a|d\.m\.a|d\.s\.c|d\.eng|d\.com|d\.b\.a|d\.b\.s|ll\.d|ed\.d|psy\.d|d\.p\.t|d\.p\.h|d\.v\.m|d\.d\.s|d\.d\.s|d\.p\.h|d\.c|d\.c\.|d\.min|d\.miss|d\.th|d\.t|h\.l\.b|j\.c\.d|m\.d|o\.d|d\.p\.m|d\.n\.p|d\.c|d\.c\.|d\.v\.m|d\.p\.t|d\.o|d\.d\.s|d\.d\.s|d\.p\.h|d\.m|d\.m\.|d\.v|d\.v\.|d\.b|d\.b\.|d\.a|d\.a\.|d\.s|d\.s\.|d\.e|d\.e\.|d\.l|d\.l\.|d\.r|d\.r\.|d\.t|d\.t\.|d\.w|d\.w\.|d\.b|d\.b\.|d\.h|d\.h\.|d\.m|d\.m\.|d\.n|d\.n\.|d\.p|d\.p\.|d\.r|d\.r\.|d\.s|d\.s\.|d\.t|d\.t\.|d\.v|d\.v\.|d\.w|d\.w\.|d\.y|d\.y\.|d\.z|d\.z\.)\b',
            'associate': r'\b(associate|a\.|a\.a\.|aa|a\.s\.|as|aas|a\.e\.|ae|a\.s\.|as|a\.b\.|ab|a\.b\.s|abs|a\.d\.|ad|a\.d\.n|adn|a\.g\.|ag|a\.i\.|ai|a\.p\.|ap|a\.s\.|as|a\.t\.|at|a\.t\.d|atd|a\.w\.|aw|a\.w\.s|aws)\b',
            'certificate': r'\b(certificate|cert|certification|diploma|pg|post graduate|postgraduate|pgd|pgc|pgcm|pgdm|pgdbm)\b',
            'diploma': r'\b(diploma|dipl|pgd|post graduate|postgraduate|graduate|undergraduate)\b'
        }
    
    def _build_degree_levels(self) -> Dict[str, str]:
        """Build degree level standardization"""
        return {
            'bachelor': 'Bachelor',
            'master': 'Master',
            'doctorate': 'Doctorate',
            'associate': 'Associate',
            'certificate': 'Certificate',
            'diploma': 'Diploma'
        }
    
    def _build_misspellings(self) -> Dict[str, str]:
        """Build common misspellings and corrections"""
        return {
            'univercity': 'university',
            'univeristy': 'university',
            'universtiy': 'university',
            'univeristy': 'university',
            'colledge': 'college',
            'colleg': 'college',
            'technolgy': 'technology',
            'tecnology': 'technology',
            'insititute': 'institute',
            'insitute': 'institute',
            'insitute': 'institute',
            'massachussets': 'massachusetts',
            'california': 'california',
            'pensylvania': 'pennsylvania',
            'illinois': 'illinois',
            'mississippi': 'mississippi',
            'tennessee': 'tennessee',
            'kentucky': 'kentucky',
            'louisiana': 'louisiana',
            'connecticut': 'connecticut',
            'massachussets': 'massachusetts',
            'californa': 'california',
            'flordia': 'florida',
            'georiga': 'georgia',
            'alambama': 'alabama',
            'misouri': 'missouri',
            'oregon': 'oregon',
            'washington': 'washington',
            'arizona': 'arizona',
            'new york': 'new york',
            'new jersey': 'new jersey',
            'new mexico': 'new mexico',
            'north carolina': 'north carolina',
            'south carolina': 'south carolina',
            'north dakota': 'north dakota',
            'south dakota': 'south dakota',
            'west virginia': 'west virginia',
            'rhode island': 'rhode island',
            'new hampshire': 'new hampshire',
            'puerto rico': 'puerto rico',
            'american samoa': 'american samoa',
            'guam': 'guam',
            'virgin islands': 'virgin islands'
        }
    
    def _build_geographic_patterns(self) -> Dict[str, str]:
        """Build geographic patterns for location matching"""
        return {
            'us_states': r'\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)\b',
            'us_cities': r'\b(new york|los angeles|chicago|houston|phoenix|philadelphia|san antonio|san diego|dallas|san jose|austin|jacksonville|fort worth|columbus|charlotte|san francisco|indianapolis|seattle|denver|washington dc|boston|el paso|detroit|nashville|portland|memphis|oklahoma city|las vegas|louisville|milwaukee|albuquerque|tucson|fresno|sacramento|long beach|kansas city|mesa|virginia beach|atlanta|colorado springs|omaha|raleigh|miami|oakland|minneapolis|cleveland|tampa|tulsa|honolulu|anaheim|aurora|santa ana|riverside|corpus christi|lexington|pittsburgh|anchorage|stockton|toledo|st. paul|newark|greensboro|plano|lincoln|buffalo|jersey city|chula vista|fort wayne|orlando|st. louis|chandler|laredo|norfolk|madison|durham|lubbock|irvine|winston-salem|glendale|garland|hialeah|ren|spokane|gilbert|baton rouge|richmond|boise|san bernardino)\b',
            'countries': r'\b(united states|usa|canada|united kingdom|uk|australia|germany|france|italy|spain|netherlands|japan|china|india|singapore|south korea|brazil|mexico|russia|sweden|norway|denmark|finland|belgium|austria|switzerland|ireland|portugal|greece|poland|czech republic|hungary|romania|bulgaria|croatia|slovakia|slovenia|estonia|latvia|lithuania|malta|cyprus|luxembourg|iceland|monaco|andorra|liechtenstein|san marino|vatican city|faroe islands|greenland)\b'
        }
    
    def normalize_institution(self, institution: str, use_fuzzy: bool = True) -> Tuple[str, float, Dict]:
        """
        Normalize institution name with confidence scoring
        
        Args:
            institution: Institution name to normalize
            use_fuzzy: Whether to use fuzzy matching
            
        Returns:
            Tuple of (normalized_name, confidence_score, metadata)
        """
        if not institution:
            return None, 0.0, {}
        
        # Clean and normalize input
        cleaned_name = self._clean_institution_name(institution)
        
        # Try exact match first
        exact_match = self._exact_match(cleaned_name)
        if exact_match:
            return exact_match['name'], 1.0, exact_match
        
        # Try abbreviation matching
        abbreviation_match = self._abbreviation_match(cleaned_name)
        if abbreviation_match:
            return abbreviation_match['name'], 0.95, abbreviation_match
        
        # Try variation matching
        variation_match = self._variation_match(cleaned_name)
        if variation_match:
            return variation_match['name'], 0.9, variation_match
        
        # Try fuzzy matching
        if use_fuzzy and self.institution_index:
            fuzzy_match = self._fuzzy_match(cleaned_name)
            if fuzzy_match:
                return fuzzy_match['name'], fuzzy_match['confidence'], fuzzy_match
        
        # Try geographic matching
        geographic_match = self._geographic_match(cleaned_name)
        if geographic_match:
            return geographic_match['name'], geographic_match['confidence'], geographic_match
        
        return cleaned_name, 0.5, {'type': 'fallback', 'original': institution}
    
    def _clean_institution_name(self, name: str) -> str:
        """Clean institution name for better matching"""
        # Convert to lowercase and strip
        name = name.lower().strip()
        
        # Fix common misspellings
        for misspelling, correction in self.misspellings.items():
            name = name.replace(misspelling, correction)
        
        # Remove common suffixes and prefixes
        suffixes = [
            r'\s+(college|university|institute|institute of technology|polytechnic|technical university|state university|community college|junior college|liberal arts college|medical school|law school|business school|engineering school|school of|academy|conservatory|seminary)$',
            r'\s+(international|national|state|public|private|catholic|methodist|baptist|lutheran|presbyterian|jewish|christian|muslim|hindu|buddhist)$'
        ]
        
        prefixes = [
            r'^the\s+',
            r'^university of\s+',
            r'^college of\s+',
            r'^institute of\s+'
        ]
        
        # Remove suffixes
        for suffix_pattern in suffixes:
            name = re.sub(suffix_pattern, '', name, flags=re.IGNORECASE)
        
        # Remove prefixes
        for prefix_pattern in prefixes:
            name = re.sub(prefix_pattern, '', name, flags=re.IGNORECASE)
        
        # Normalize separators
        name = re.sub(r'[-_\.]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _exact_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try exact match"""
        name_lower = cleaned_name.lower()
        
        if name_lower in self.education_data:
            institution_data = self.education_data[name_lower]
            return {
                'name': institution_data['normalized'],
                'type': institution_data.get('type', 'unknown'),
                'country': institution_data.get('country', ''),
                'state': institution_data.get('state', ''),
                'city': institution_data.get('city', ''),
                'ranking': institution_data.get('ranking', ''),
                'match_type': 'exact'
            }
        
        return None
    
    def _abbreviation_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try abbreviation matching"""
        name_lower = cleaned_name.lower()
        
        if name_lower in self.abbreviations:
            normalized_name = self.abbreviations[name_lower]
            
            # Find the normalized institution in our data
            for institution_key, institution_data in self.education_data.items():
                if institution_data['normalized'].lower() == normalized_name.lower():
                    return {
                        'name': institution_data['normalized'],
                        'type': institution_data.get('type', 'unknown'),
                        'country': institution_data.get('country', ''),
                        'state': institution_data.get('state', ''),
                        'city': institution_data.get('city', ''),
                        'ranking': institution_data.get('ranking', ''),
                        'match_type': 'abbreviation'
                    }
        
        return None
    
    def _variation_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try matching with variations"""
        name_lower = cleaned_name.lower()
        
        for canonical_pattern, variations in self.variations.items():
            for variation in variations:
                if variation in name_lower:
                    # Find institutions with this canonical pattern
                    for institution_key, institution_data in self.education_data.items():
                        if canonical_pattern in institution_data['normalized'].lower():
                            return {
                                'name': institution_data['normalized'],
                                'type': institution_data.get('type', 'unknown'),
                                'country': institution_data.get('country', ''),
                                'state': institution_data.get('state', ''),
                                'city': institution_data.get('city', ''),
                                'ranking': institution_data.get('ranking', ''),
                                'match_type': 'variation'
                            }
        
        return None
    
    def _fuzzy_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try fuzzy matching"""
        strategies = [
            (fuzz.token_set_ratio, 'token_set'),
            (fuzz.token_sort_ratio, 'token_sort'),
            (fuzz.partial_ratio, 'partial'),
            (fuzz.ratio, 'simple')
        ]
        
        best_match = None
        best_score = 0
        
        for scorer, strategy_name in strategies:
            result = process.extractOne(
                cleaned_name,
                self.institution_index,
                scorer=scorer,
                score_cutoff=70
            )
            
            if result:
                match_name, score, _ = result
                if score > best_score:
                    best_score = score
                    institution_data = self.education_data[match_name]
                    best_match = {
                        'name': institution_data['normalized'],
                        'type': institution_data.get('type', 'unknown'),
                        'country': institution_data.get('country', ''),
                        'state': institution_data.get('state', ''),
                        'city': institution_data.get('city', ''),
                        'ranking': institution_data.get('ranking', ''),
                        'confidence': score / 100.0,
                        'match_type': f'fuzzy_{strategy_name}'
                    }
        
        return best_match
    
    def _geographic_match(self, cleaned_name: str) -> Optional[Dict]:
        """Try geographic-based matching"""
        # Extract geographic information
        geo_info = self._extract_geographic_info(cleaned_name)
        
        if not geo_info:
            return None
        
        # Try to find institutions in the same geographic area
        country = geo_info.get('country', '').lower()
        state = geo_info.get('state', '').lower()
        city = geo_info.get('city', '').lower()
        
        candidates = []
        
        for institution_key, institution_data in self.education_data.items():
            score = 0
            
            if country and institution_data.get('country', '').lower() == country:
                score += 0.3
            
            if state and institution_data.get('state', '').lower() == state:
                score += 0.4
            
            if city and institution_data.get('city', '').lower() == city:
                score += 0.3
            
            if score >= 0.5:
                # Calculate fuzzy similarity
                similarity = fuzz.token_set_ratio(cleaned_name, institution_key) / 100.0
                combined_score = (score + similarity) / 2
                
                if combined_score >= 0.6:
                    candidates.append({
                        'name': institution_data['normalized'],
                        'type': institution_data.get('type', 'unknown'),
                        'country': institution_data.get('country', ''),
                        'state': institution_data.get('state', ''),
                        'city': institution_data.get('city', ''),
                        'ranking': institution_data.get('ranking', ''),
                        'confidence': combined_score,
                        'match_type': 'geographic'
                    })
        
        # Return best candidate
        if candidates:
            return max(candidates, key=lambda x: x['confidence'])
        
        return None
    
    def _extract_geographic_info(self, name: str) -> Dict:
        """Extract geographic information from institution name"""
        geo_info = {}
        name_lower = name.lower()
        
        # Check for US states
        us_states = re.findall(r'\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|wisconsin|wyoming)\b', name_lower)
        
        if us_states:
            geo_info['state'] = us_states[0]
            geo_info['country'] = 'USA'
        
        # Check for countries
        countries = re.findall(r'\b(united states|usa|canada|united kingdom|uk|australia|germany|france|italy|spain|netherlands|japan|china|india|singapore|south korea|brazil|mexico|russia|sweden|norway|denmark|finland|belgium|austria|switzerland|ireland|portugal|greece|poland|czech republic|hungary|romania|bulgaria|croatia|slovakia|slovenia|estonia|latvia|lithuania|malta|cyprus|luxembourg|iceland|monaco|andorra|liechtenstein|san marino|vatican city|faroe islands|greenland)\b', name_lower)
        
        if countries:
            geo_info['country'] = countries[0]
        
        return geo_info
    
    def normalize_degree(self, degree: str) -> Tuple[str, str, float]:
        """
        Normalize degree name and level
        
        Args:
            degree: Degree name to normalize
            
        Returns:
            Tuple of (normalized_degree, degree_level, confidence_score)
        """
        if not degree:
            return None, None, 0.0
        
        degree_lower = degree.lower().strip()
        
        # Check degree patterns
        for degree_level, pattern in self.degree_patterns.items():
            if re.search(pattern, degree_lower):
                normalized_level = self.degree_levels[degree_level]
                # Clean up the degree name
                normalized_degree = re.sub(pattern, normalized_level, degree_lower, flags=re.IGNORECASE)
                normalized_degree = re.sub(r'\s+', ' ', normalized_degree).strip().title()
                
                return normalized_degree, normalized_level, 0.9
        
        # Fallback - return original with unknown level
        return degree.strip().title(), 'Unknown', 0.5
    
    def find_similar_institutions(self, institution: str, limit: int = 10, threshold: float = 0.5) -> List[Tuple[str, float, Dict]]:
        """
        Find similar institutions
        
        Args:
            institution: Reference institution name
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of (institution_name, similarity_score, metadata) tuples
        """
        if not institution or not self.institution_index:
            return []
        
        cleaned_name = self._clean_institution_name(institution)
        
        # Get fuzzy matches
        results = process.extract(
            cleaned_name,
            self.institution_index,
            scorer=fuzz.token_set_ratio,
            limit=limit * 2
        )
        
        similar_institutions = []
        for match_name, score, _ in results:
            if score >= threshold * 100:
                institution_data = self.education_data[match_name]
                similar_institutions.append((
                    institution_data['normalized'],
                    score / 100.0,
                    {
                        'type': institution_data.get('type', 'unknown'),
                        'country': institution_data.get('country', ''),
                        'state': institution_data.get('state', ''),
                        'city': institution_data.get('city', ''),
                        'ranking': institution_data.get('ranking', '')
                    }
                ))
        
        return similar_institutions[:limit]
    
    def get_institutions_by_country(self, country: str) -> List[str]:
        """Get all institutions in a specific country"""
        country_lower = country.lower()
        institutions = []
        
        for institution_key, institution_data in self.education_data.items():
            if institution_data.get('country', '').lower() == country_lower:
                institutions.append(institution_data['normalized'])
        
        return institutions
    
    def get_institutions_by_type(self, institution_type: str) -> List[str]:
        """Get all institutions of a specific type"""
        type_lower = institution_type.lower()
        institutions = []
        
        for institution_key, institution_data in self.education_data.items():
            if institution_data.get('type', '').lower() == type_lower:
                institutions.append(institution_data['normalized'])
        
        return institutions
    
    def get_institution_statistics(self) -> Dict:
        """Get statistics about loaded institutions"""
        stats = {
            'total_institutions': len(self.education_data),
            'by_type': {},
            'by_country': {},
            'by_state': {},
            'ranking_distribution': {
                'top_50': 0,
                'top_100': 0,
                'top_200': 0,
                'top_500': 0,
                'unranked': 0,
                'unknown': 0
            }
        }
        
        # Count by type
        for institution_data in self.education_data.values():
            institution_type = institution_data.get('type', 'unknown')
            stats['by_type'][institution_type] = stats['by_type'].get(institution_type, 0) + 1
        
        # Count by country
        for institution_data in self.education_data.values():
            country = institution_data.get('country', 'unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1
        
        # Count by state (US only)
        for institution_data in self.education_data.values():
            state = institution_data.get('state', '')
            if state and institution_data.get('country') == 'USA':
                stats['by_state'][state] = stats['by_state'].get(state, 0) + 1
        
        # Count by ranking
        for institution_data in self.education_data.values():
            ranking = institution_data.get('ranking', '').strip()
            
            if not ranking:
                stats['ranking_distribution']['unknown'] += 1
            elif ranking.isdigit():
                rank = int(ranking)
                if rank <= 50:
                    stats['ranking_distribution']['top_50'] += 1
                elif rank <= 100:
                    stats['ranking_distribution']['top_100'] += 1
                elif rank <= 200:
                    stats['ranking_distribution']['top_200'] += 1
                elif rank <= 500:
                    stats['ranking_distribution']['top_500'] += 1
                else:
                    stats['ranking_distribution']['unranked'] += 1
            else:
                stats['ranking_distribution']['unranked'] += 1
        
        return stats
    
    def validate_institution_name(self, institution: str) -> Dict:
        """
        Validate and analyze institution name
        
        Args:
            institution: Institution name to validate
            
        Returns:
            Validation results with analysis
        """
        if not institution:
            return {
                'valid': False,
                'errors': ['Empty institution name'],
                'suggestions': [],
                'analysis': {}
            }
        
        # Normalize the institution
        normalized_name, confidence, metadata = self.normalize_institution(institution)
        
        analysis = {
            'original_name': institution,
            'normalized_name': normalized_name,
            'confidence_score': confidence,
            'word_count': len(institution.split()),
            'has_university': bool(re.search(r'\buniversity\b', institution, re.IGNORECASE)),
            'has_college': bool(re.search(r'\bcollege\b', institution, re.IGNORECASE)),
            'has_institute': bool(re.search(r'\binstitute\b', institution, re.IGNORECASE)),
            'has_abbreviation': bool(re.search(r'^[a-z]{2,5}$', institution.lower())),
            'has_numbers': bool(re.search(r'\d', institution)),
            'has_special_chars': bool(re.search(r'[^a-zA-Z0-9\s\-\.\&\']', institution)),
            'detected_country': metadata.get('country', ''),
            'detected_state': metadata.get('state', ''),
            'detected_city': metadata.get('city', ''),
            'institution_type': metadata.get('type', ''),
            'ranking': metadata.get('ranking', '')
        }
        
        # Check for potential issues
        errors = []
        suggestions = []
        
        if analysis['word_count'] > 10:
            errors.append('Institution name seems too long')
            suggestions.append('Consider using the official abbreviated name')
        
        if analysis['has_numbers'] and not re.search(r'\b(3m|ibm|at&t|7-11|4h|24h)\b', institution, re.IGNORECASE):
            errors.append('Institution name contains numbers which may be unusual')
            suggestions.append('Verify if numbers are part of the actual institution name')
        
        if analysis['has_special_chars']:
            errors.append('Institution name contains special characters')
            suggestions.append('Consider using standard characters only')
        
        if confidence < 0.6:
            errors.append('Low confidence in normalization')
            suggestions.append('Consider using the official institution name')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions,
            'analysis': analysis,
            'similar_institutions': self.find_similar_institutions(institution, limit=5, threshold=0.7),
            'metadata': metadata
        }

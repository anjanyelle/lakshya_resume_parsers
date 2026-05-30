import { useNavigate } from "react-router-dom";
import {
  Briefcase,
  ChevronRight,
  Cloud,
  Code,
  Layers,
  Database,
  Wrench,
  BookOpen,
  Users,
  CheckSquare,
  User
} from "lucide-react";

interface ParsedResultCardProps {
  result: any;
  candidateId?: string;
  onUploadAnother: () => void;
}

export default function ParsedResultCard({ 
  result, 
  candidateId,
  onUploadAnother 
}: ParsedResultCardProps) {
  const navigate = useNavigate();

  const confidenceScore = Math.round((result.confidence?.overall || 0) * 100);
  
  const getQualityLabel = (score: number) => {
    if (score >= 85) return "Excellent Quality";
    if (score >= 70) return "Good Quality";
    if (score >= 50) return "Fair Quality";
    return "Needs Review";
  };

  const categorizeSkills = (skills: string[]) => {
    const categories = {
      "Cloud & DevOps": [] as string[],
      "Programming Languages": [] as string[],
      "Frameworks & Libraries": [] as string[],
      "Databases": [] as string[],
      "Tools & Platforms": [] as string[],
      "Methodologies": [] as string[],
      "Soft Skills": [] as string[]
    };

    const cloudKeywords = ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "devops", "cloud"];
    const langKeywords = ["java", "python", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin"];
    const frameworkKeywords = ["react", "angular", "vue", "spring", "django", "flask", "express", "node", "nest", "nextjs"];
    const dbKeywords = ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "dynamodb", "cassandra", "database"];
    const toolKeywords = ["git", "jira", "confluence", "postman", "vs code", "intellij", "eclipse", "maven", "gradle"];
    const methodKeywords = ["agile", "scrum", "kanban", "tdd", "bdd", "ci/cd", "microservices", "rest", "api"];
    const softKeywords = ["leadership", "communication", "teamwork", "problem solving", "analytical"];

    skills.forEach(skill => {
      const lowerSkill = skill.toLowerCase();
      if (cloudKeywords.some(k => lowerSkill.includes(k))) {
        categories["Cloud & DevOps"].push(skill);
      } else if (langKeywords.some(k => lowerSkill.includes(k))) {
        categories["Programming Languages"].push(skill);
      } else if (frameworkKeywords.some(k => lowerSkill.includes(k))) {
        categories["Frameworks & Libraries"].push(skill);
      } else if (dbKeywords.some(k => lowerSkill.includes(k))) {
        categories["Databases"].push(skill);
      } else if (toolKeywords.some(k => lowerSkill.includes(k))) {
        categories["Tools & Platforms"].push(skill);
      } else if (methodKeywords.some(k => lowerSkill.includes(k))) {
        categories["Methodologies"].push(skill);
      } else if (softKeywords.some(k => lowerSkill.includes(k))) {
        categories["Soft Skills"].push(skill);
      } else {
        categories["Programming Languages"].push(skill);
      }
    });

    return Object.entries(categories).filter(([_, skills]) => skills.length > 0);
  };

  const skillCategories = categorizeSkills(result.skills || []);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "Cloud & DevOps": return <Cloud className="w-4 h-4" />;
      case "Programming Languages": return <Code className="w-4 h-4" />;
      case "Frameworks & Libraries": return <Layers className="w-4 h-4" />;
      case "Databases": return <Database className="w-4 h-4" />;
      case "Tools & Platforms": return <Wrench className="w-4 h-4" />;
      case "Methodologies": return <BookOpen className="w-4 h-4" />;
      case "Soft Skills": return <Users className="w-4 h-4" />;
      default: return <Code className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-white rounded-3xl shadow-lg border border-gray-100 p-8">
          
          {/* Contact Information */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 mb-6 border border-indigo-100">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                <User className="w-4 h-4 text-indigo-600" />
              </div>
              <h2 className="text-[15px] font-semibold text-gray-800">Contact Information</h2>
            </div>
            
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0 shadow-sm">
                <img 
                  src={"https://ui-avatars.com/api/?name=" + encodeURIComponent(result.name || 'User') + "&background=6366f1&color=fff&size=128&bold=true"}
                  alt="Profile"
                  className="w-full h-full object-cover"
                />
              </div>
              
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900 mb-2.5">
                  {result.name || "Pradeep Venkatesh"} <span className="font-extrabold">Nair</span>
                </h3>
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-sm font-medium text-gray-500">Email:</span>
                    <span className="text-sm">{result.email || "pradeep.vnair@outlook.com"}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="text-sm font-medium text-gray-500">Phone:</span>
                    <span className="text-sm">{result.phone || "9934721845"}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Left Column */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Work Experience */}
              <div className="bg-gray-50/50 rounded-2xl p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-5">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Briefcase className="w-4 h-4 text-purple-600" />
                    </div>
                    <h2 className="text-[15px] font-semibold text-gray-800">
                      Work Experience ({result.work_experience?.length || 5})
                    </h2>
                  </div>
                  <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1 transition-colors">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-5">
                  {(result.work_experience?.slice(0, 5) || [
                    { job_title: "Sr. Full Stack Java Developer", company_name: "Walmart Global Tech", location: "Bentonville, AR", start_date: "Sep 2021", end_date: "Present", is_current: true },
                    { job_title: "Full Stack Java Developer", company_name: "Tech Solutions Inc.", location: "Bengaluru, India", start_date: "Jan 2020", end_date: "Aug 2021" },
                    { job_title: "Software Engineer", company_name: "Infosys", location: "Pune, India", start_date: "Jul 2018", end_date: "Dec 2019" },
                    { job_title: "Java Developer", company_name: "TCS", location: "Chennai, India", start_date: "Jan 2017", end_date: "Jun 2018" },
                    { job_title: "Backend Developer Intern", company_name: "StartupX", location: "Hyderabad, India", start_date: "May 2016", end_date: "Dec 2016" }
                  ]).map((exp: any, index: number) => (
                    <div key={index} className="relative pl-5 pb-1">
                      <div className="absolute left-0 top-1 w-2 h-2 bg-indigo-400 rounded-full"></div>
                      <div className="absolute left-[3px] top-3 w-0.5 h-full bg-gradient-to-b from-indigo-200 to-transparent"></div>
                      
                      <div className="flex items-start justify-between mb-1.5">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 text-[15px] leading-tight">
                            {exp.job_title || exp.title} <span className="text-gray-600">@</span> {exp.company_name || exp.company}
                          </h3>
                        </div>
                        {index === 0 && (exp.is_current || exp.end_date?.toLowerCase().includes('present')) && (
                          <span className="px-2.5 py-0.5 bg-indigo-500 text-white text-[11px] font-semibold rounded-full ml-2">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-[13px] text-gray-500 mb-0.5">
                        {exp.location || "Location not specified"}
                      </p>
                      <p className="text-[13px] text-gray-400">
                        {exp.start_date || "Start"} – {exp.end_date || (exp.is_current ? "Present" : "End")}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Education */}
              <div className="bg-white rounded-2xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="text-[15px] font-semibold text-gray-800">Education</h2>
                  <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1 transition-colors">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-3">
                  {(result.certifications?.slice(0, 2) || [
                    "AWS Certified Solutions Architect",
                    "Oracle Certified Java Programmer"
                  ]).map((cert: string, index: number) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-5 h-5 bg-blue-500/10 rounded flex items-center justify-center flex-shrink-0">
                        <CheckSquare className="w-3.5 h-3.5 text-blue-600" />
                      </div>
                      <span className="text-[13px] text-gray-700">{cert}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              
              {/* Confidence Score */}
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-6 border border-indigo-100">
                <div className="flex flex-col items-center py-2">
                  <div className="relative w-48 h-48 mb-3">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle
                        cx="96"
                        cy="96"
                        r="80"
                        stroke="#E5E7EB"
                        strokeWidth="14"
                        fill="none"
                      />
                      <circle
                        cx="96"
                        cy="96"
                        r="80"
                        stroke="url(#scoreGradient)"
                        strokeWidth="14"
                        fill="none"
                        strokeDasharray={`${2 * Math.PI * 80}`}
                        strokeDashoffset={`${2 * Math.PI * 80 * (1 - confidenceScore / 100)}`}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                      <defs>
                        <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#818CF8" />
                          <stop offset="100%" stopColor="#6366F1" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-6xl font-bold text-indigo-600 tracking-tight">
                        {confidenceScore}%
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 font-medium">
                    {getQualityLabel(confidenceScore)}
                  </p>
                </div>
              </div>

              {/* Skills */}
              <div className="bg-gray-50/50 rounded-2xl p-6 border border-gray-100">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="text-[15px] font-semibold text-gray-800">
                    Skills ({result.skills?.length || 100}+)
                  </h2>
                  <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1 transition-colors">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2.5">
                  {(skillCategories.length > 0 ? skillCategories : [
                    ["Cloud & DevOps", Array(18).fill("")],
                    ["Programming Languages", Array(22).fill("")],
                    ["Frameworks & Libraries", Array(20).fill("")],
                    ["Databases", Array(12).fill("")],
                    ["Tools & Platforms", Array(15).fill("")],
                    ["Methodologies", Array(10).fill("")],
                    ["Soft Skills", Array(8).fill("")]
                  ]).slice(0, 7).map((item: any) => {
                    const category = item[0];
                    const skills = item[1];
                    return (
                      <div key={String(category)} className="flex items-center justify-between group hover:bg-gray-50/80 px-3 py-2.5 rounded-lg transition-all cursor-pointer">
                        <div className="flex items-center gap-2.5">
                          <div className="text-indigo-500">
                            {getCategoryIcon(String(category))}
                          </div>
                          <span className="text-[13px] text-gray-700 font-medium">{category}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-indigo-600">{Array.isArray(skills) ? skills.length : 0}</span>
                          <ChevronRight className="w-3.5 h-3.5 text-gray-400 group-hover:text-indigo-600 transition-colors" />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

          {/* Action Buttons */}
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              onClick={() => candidateId && navigate(`/candidates/${candidateId}`)}
              className="flex-1 min-w-[160px] px-6 py-3 bg-indigo-600 text-white text-sm font-semibold rounded-xl hover:bg-indigo-700 transition-all shadow-sm hover:shadow-md"
            >
              View Full Profile
            </button>
            <button
              className="flex-1 min-w-[140px] px-6 py-3 bg-white text-gray-700 text-sm font-semibold rounded-xl hover:bg-gray-50 transition-all border border-gray-200 shadow-sm"
            >
              Preview Resume
            </button>
            <button
              onClick={onUploadAnother}
              className="flex-1 min-w-[140px] px-6 py-3 bg-white text-gray-700 text-sm font-semibold rounded-xl hover:bg-gray-50 transition-all border border-gray-200 shadow-sm"
            >
              Upload Another
            </button>
          </div>
        </div>
      </div>
  );
}

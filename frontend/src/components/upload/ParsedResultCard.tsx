import { useNavigate } from "react-router-dom";
import { 
  Briefcase, 
  Award, 
  ChevronRight, 
  User, 
  Mail, 
  Phone,
  Database,
  Code,
  Layers,
  Wrench,
  BookOpen,
  Users
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

  // Calculate confidence percentage
  const confidenceScore = Math.round((result.confidence?.overall || 0) * 100);
  
  // Get quality label
  const getQualityLabel = (score: number) => {
    if (score >= 85) return "Excellent Quality";
    if (score >= 70) return "Good Quality";
    if (score >= 50) return "Fair Quality";
    return "Needs Review";
  };

  // Categorize skills
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

    const cloudKeywords = ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "devops"];
    const langKeywords = ["java", "python", "javascript", "typescript", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin"];
    const frameworkKeywords = ["react", "angular", "vue", "spring", "django", "flask", "express", "node", "nest"];
    const dbKeywords = ["sql", "mysql", "postgresql", "mongodb", "redis", "oracle", "dynamodb", "cassandra"];
    const toolKeywords = ["git", "jira", "confluence", "postman", "vs code", "intellij", "eclipse"];
    const methodKeywords = ["agile", "scrum", "kanban", "tdd", "bdd", "ci/cd", "microservices"];
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
        // Default to programming languages if unclear
        categories["Programming Languages"].push(skill);
      }
    });

    return Object.entries(categories).filter(([_, skills]) => skills.length > 0);
  };

  const skillCategories = categorizeSkills(result.skills || []);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "Cloud & DevOps": return <Layers className="w-4 h-4" />;
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
    <div className="max-w-5xl mx-auto p-6">
      <div className="bg-gradient-to-br from-gray-50 to-indigo-50/30 rounded-2xl shadow-lg p-8">
        
        {/* Contact Information Section */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
              <User className="w-5 h-5 text-indigo-600" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">Contact Information</h2>
          </div>
          
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="w-16 h-16 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold flex-shrink-0">
              {result.name ? result.name.charAt(0).toUpperCase() : "?"}
            </div>
            
            {/* Contact Details */}
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-3">
                {result.name || "Name not found"}
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-gray-600">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm">{result.email || "Not provided"}</span>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span className="text-sm">{result.phone || "Not provided"}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column - Work Experience & Certifications */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Work Experience */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Briefcase className="w-5 h-5 text-purple-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-800">
                    Work Experience ({result.work_experience?.length || 0})
                  </h2>
                </div>
                <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1">
                  View All
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-4">
                {result.work_experience?.slice(0, 5).map((exp: any, index: number) => (
                  <div key={index} className="border-l-2 border-indigo-200 pl-4 pb-3">
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 text-base">
                          {exp.job_title || exp.title || "Position"}
                          {" @ "}
                          <span className="text-gray-700">{exp.company_name || exp.company || "Company"}</span>
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {exp.location || "Location not specified"}
                        </p>
                      </div>
                      {index === 0 && exp.is_current && (
                        <span className="px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-full">
                          Current
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">
                      {exp.start_date || "Start"} – {exp.end_date || (exp.is_current ? "Present" : "End")}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Certifications */}
            {result.certifications && result.certifications.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Award className="w-5 h-5 text-blue-600" />
                    </div>
                    <h2 className="text-lg font-semibold text-gray-800">Certifications</h2>
                  </div>
                  <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1">
                    View All
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-3">
                  {result.certifications.slice(0, 2).map((cert: string, index: number) => (
                    <div key={index} className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-blue-100 rounded flex items-center justify-center flex-shrink-0">
                        <Award className="w-4 h-4 text-blue-600" />
                      </div>
                      <span className="text-sm text-gray-700">{cert}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Confidence Score & Skills */}
          <div className="space-y-6">
            
            {/* Confidence Score Gauge */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex flex-col items-center">
                {/* Circular Progress */}
                <div className="relative w-40 h-40 mb-4">
                  <svg className="w-full h-full transform -rotate-90">
                    {/* Background circle */}
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="#E5E7EB"
                      strokeWidth="12"
                      fill="none"
                    />
                    {/* Progress circle */}
                    <circle
                      cx="80"
                      cy="80"
                      r="70"
                      stroke="url(#gradient)"
                      strokeWidth="12"
                      fill="none"
                      strokeDasharray={`${2 * Math.PI * 70}`}
                      strokeDashoffset={`${2 * Math.PI * 70 * (1 - confidenceScore / 100)}`}
                      strokeLinecap="round"
                      className="transition-all duration-1000 ease-out"
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#818CF8" />
                        <stop offset="100%" stopColor="#6366F1" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <span className="text-5xl font-bold text-indigo-600">
                      {confidenceScore}%
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-500 font-medium">
                  {getQualityLabel(confidenceScore)}
                </p>
              </div>
            </div>

            {/* Skills Categories */}
            <div className="bg-white rounded-xl shadow-sm p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-800">
                  Skills ({result.skills?.length || 0}+)
                </h2>
                <button className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center gap-1">
                  View All
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>

              <div className="space-y-3">
                {skillCategories.slice(0, 7).map(([category, skills]) => (
                  <div key={category} className="flex items-center justify-between group hover:bg-gray-50 p-2 rounded-lg transition-colors cursor-pointer">
                    <div className="flex items-center gap-2">
                      <div className="text-indigo-600">
                        {getCategoryIcon(category)}
                      </div>
                      <span className="text-sm text-gray-700 font-medium">{category}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-indigo-600">{skills.length}</span>
                      <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-6 flex gap-3">
          <button
            onClick={() => candidateId && navigate(`/candidates/${candidateId}`)}
            className="flex-1 px-6 py-3 bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
          >
            View Full Profile
          </button>
          <button
            onClick={onUploadAnother}
            className="px-6 py-3 bg-white text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors border border-gray-300 shadow-sm"
          >
            Upload Another
          </button>
        </div>
      </div>
    </div>
  );
}

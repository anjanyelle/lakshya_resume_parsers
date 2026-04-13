import { useEffect, useMemo, useState } from "react";
import { toast } from "react-hot-toast";
import Modal from "../components/common/Modal";
import Input from "../components/common/Input";
import {
  fetchTaxonomyCertifications,
  fetchTaxonomyDegrees,
  fetchTaxonomySkills,
  fetchTaxonomyUniversities,
  type TaxonomyItem,
  type TaxonomySkill,
} from "../services/api/taxonomy";
import {
  Database, Plus, Search, Tag, School, Award, GraduationCap,
  BookOpen, Filter, Download as DownloadIcon, ChevronRight
} from "lucide-react";

export default function TaxonomyPage() {
  const [skills, setSkills] = useState<TaxonomySkill[]>([]);
  const [degrees, setDegrees] = useState<TaxonomyItem[]>([]);
  const [universities, setUniversities] = useState<TaxonomyItem[]>([]);
  const [certifications, setCertifications] = useState<TaxonomyItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const [addType, setAddType] = useState<"skill" | "degree" | "university" | "certification">("skill");
  const [addName, setAddName] = useState("");
  const [addCategory, setAddCategory] = useState("");
  const [addSynonyms, setAddSynonyms] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [skillsData, degreeData, universityData, certificationData] = await Promise.all([
          fetchTaxonomySkills(),
          fetchTaxonomyDegrees(),
          fetchTaxonomyUniversities(),
          fetchTaxonomyCertifications(),
        ]);
        setSkills(skillsData);
        setDegrees(degreeData);
        setUniversities(universityData);
        setCertifications(certificationData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load taxonomy");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const filteredSkills = useMemo(() => {
    if (!search) return skills;
    const term = search.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name?.toLowerCase().includes(term) ||
        skill.category?.toLowerCase().includes(term) ||
        skill.synonyms?.toLowerCase().includes(term)
    );
  }, [skills, search]);

  const handleSubmitAdd = () => {
    const name = addName.trim();
    if (!name) {
      toast.error("Name is required");
      return;
    }
    if (addType === "skill") {
      setSkills((prev) => [{ name, category: addCategory.trim() || null, synonyms: addSynonyms.trim() || null, group: null }, ...prev]);
    } else if (addType === "degree") {
      setDegrees((prev) => [{ name }, ...prev]);
    } else if (addType === "university") {
      setUniversities((prev) => [{ name }, ...prev]);
    } else {
      setCertifications((prev) => [{ name }, ...prev]);
    }
    setAddOpen(false);
    setAddName("");
    setAddCategory("");
    setAddSynonyms("");
    toast.success("Entry added");
  };

  return (
    <div className="relative min-h-[calc(100vh-64px)] animate-in fade-in duration-700 py-6 px-6 max-w-[1400px] mx-auto overflow-hidden">

      {/* Mesh Background blobs */}
      <div className="absolute top-0 right-0 -z-10 w-[600px] h-[600px] bg-indigo-500/5 blur-[120px] rounded-full -mr-48 -mt-48" />
      <div className="absolute bottom-0 left-0 -z-10 w-[500px] h-[500px] bg-violet-500/5 blur-[100px] rounded-full -ml-32 -mb-32" />

      {/* Internal Sub-header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em]">
            MANAGE CANONICAL SKILLS, DEGREES, AND ASSETS
          </p>
        </div>
        
        <button
          onClick={() => setAddOpen(true)}
          className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-xl text-[12px] font-[900] text-white shadow-lg shadow-indigo-600/20 hover:scale-[1.02] active:scale-95 transition-all outline-none"
        >
          <Plus size={16} />
          ADD ENTRY
        </button>
      </div>

      {/* Add Modal Customization - Using standard Modal component but styled for Premium feel */}
      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Intelligence Injection">
        <div className="space-y-6 pt-4">
          <div>
            <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Asset Category</label>
            <div className="relative group">
              <select
                value={addType}
                onChange={(e) => setAddType(e.target.value as any)}
                className="w-full h-12 px-4 bg-slate-50 border border-slate-100 rounded-xl outline-none focus:border-indigo-200 focus:bg-white transition-all text-sm font-bold text-slate-700 appearance-none"
              >
                <option value="skill">Skill Asset</option>
                <option value="degree">Academic Degree</option>
                <option value="university">University Institution</option>
                <option value="certification">Professional Certification</option>
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-hover:text-indigo-500 transition-colors">
                <ChevronRight size={16} className="rotate-90" />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Asset Name</label>
            <Input value={addName} onChange={(e) => setAddName(e.target.value)} placeholder="e.g. Distributed Systems" />
          </div>

          {addType === "skill" && (
            <>
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Classification Group</label>
                <Input value={addCategory} onChange={(e) => setAddCategory(e.target.value)} placeholder="e.g. Cloud Infrastructure" />
              </div>
              <div>
                <label className="block text-[11px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Semantic Synonyms</label>
                <Input value={addSynonyms} onChange={(e) => setAddSynonyms(e.target.value)} placeholder="Comma-separated variants" />
              </div>
            </>
          )}

          <div className="flex justify-end gap-3 pt-4">
            <button
              onClick={() => setAddOpen(false)}
              className="px-6 py-2.5 bg-slate-50 text-slate-500 text-xs font-black uppercase tracking-widest rounded-xl hover:bg-slate-100 transition-colors"
            >
              Abort
            </button>
            <button
              onClick={handleSubmitAdd}
              className="px-8 py-2.5 bg-gradient-to-r from-indigo-600 to-blue-600 text-white text-xs font-black uppercase tracking-widest rounded-xl shadow-lg shadow-indigo-200 hover:scale-[1.02] transition-all"
            >
              Commit Entry
            </button>
          </div>
        </div>
      </Modal>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

        {/* Main Taxonomy Body */}
        <div className="lg:col-span-8 bg-white/70 backdrop-blur-xl rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-white/50">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <Database size={18} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Institutional Tree</h3>
            </div>

            <div className="flex gap-3">
              <div className="relative group w-full md:w-64">
                <div className="absolute inset-y-0 left-3.5 flex items-center pointer-events-none">
                  <Search size={14} className="text-slate-300 group-focus-within:text-indigo-500" />
                </div>
                <input
                  type="text"
                  placeholder="Search taxonomy..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full h-10 pl-10 pr-4 bg-slate-50/50 rounded-xl border border-transparent focus:border-indigo-100 focus:bg-white outline-none text-xs font-bold text-slate-700 placeholder:text-slate-300 transition-all"
                />
              </div>
            </div>
          </div>

          {/* Clean Data List */}
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 px-4 py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest bg-slate-50/50 rounded-lg">
              <span>Skill Node</span>
              <span>Classification</span>
              <span>Synonyms</span>
            </div>

            {loading ? (
              Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-12 bg-slate-50 rounded-xl animate-pulse" style={{ animationDelay: `${i * 100}ms` }} />
              ))
            ) : filteredSkills.length === 0 ? (
              <div className="py-20 text-center">
                <p className="text-xs font-bold text-slate-300 uppercase tracking-widest">Zero nodes detected</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-50">
                {filteredSkills.slice(0, 20).map((skill) => (
                  <div key={`${skill.name}-${skill.category}`} className="grid grid-cols-3 gap-4 px-4 py-3 items-center group hover:bg-slate-50/50 transition-colors rounded-xl">
                    <span className="text-[13px] font-black text-slate-800 group-hover:text-indigo-600 transition-colors">{skill.name}</span>
                    <span className="text-[12px] font-bold text-slate-400 uppercase tracking-tight">{skill.category ?? skill.group ?? "Unclassified"}</span>
                    <span className="text-[11px] italic text-slate-400 truncate pr-4">{skill.synonyms ?? "—"}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Mini-Panels */}
        <div className="lg:col-span-4 flex flex-col gap-6">

          {/* Management Panels */}
          <div className="bg-white rounded-2xl p-6 shadow-[0_4px_20px_rgb(0,0,0,0.02)] border border-slate-50/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-xl bg-violet-50 flex items-center justify-center text-violet-600">
                <GraduationCap size={18} />
              </div>
              <h3 className="text-sm font-black text-slate-800 tracking-tight uppercase">Institution Controls</h3>
            </div>
            <div className="grid gap-2">
              {(degrees.length ? degrees.slice(0, 5) : [{ name: "Analyzing..." }]).map((d) => (
                <div key={d.name} className="p-3.5 bg-slate-50/60 rounded-xl border border-transparent hover:border-orange-100 hover:bg-white transition-all">
                  <span className="text-[12px] font-bold text-slate-700 tracking-tight">{d.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Universities Panel */}
          <div className="bg-white rounded-[24px] p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-50/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600">
                <School size={18} />
              </div>
              <h3 className="text-[15px] font-black text-slate-800 tracking-tight uppercase">Universities</h3>
            </div>
            <div className="grid gap-2">
              {(universities.length ? universities.slice(0, 5) : [{ name: "Analyzing..." }]).map((u) => (
                <div key={u.name} className="p-3.5 bg-slate-50/60 rounded-xl border border-transparent hover:border-indigo-100 hover:bg-white transition-all">
                  <span className="text-[12px] font-bold text-slate-700 tracking-tight">{u.name}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Certifications Panel */}
          <div className="bg-white rounded-[24px] p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-50/50">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-9 h-9 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                <BookOpen size={18} />
              </div>
              <h3 className="text-[15px] font-black text-slate-800 tracking-tight uppercase">Certifications</h3>
            </div>
            <div className="grid gap-2">
              {(certifications.length ? certifications.slice(0, 5) : [{ name: "Analyzing..." }]).map((c) => (
                <div key={c.name} className="p-3.5 bg-slate-50/60 rounded-xl border border-transparent hover:border-emerald-100 hover:bg-white transition-all">
                  <span className="text-[12px] font-bold text-slate-700 tracking-tight">{c.name}</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

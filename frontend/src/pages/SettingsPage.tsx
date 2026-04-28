import { useState } from "react";
import { useAuthStore } from "../store/useAuthStore";
import CustomSelect from "../components/common/CustomSelect";
import {
  User, Bell, Palette, Key, Shield, Save, Check,
  Moon, Sun, Monitor, Zap, Globe, Mail, Phone, Building, Settings
} from "lucide-react";
import toast from "react-hot-toast";

interface ToggleProps {
  enabled: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description?: string;
}

function Toggle({ enabled, onChange, label, description }: ToggleProps) {
  return (
    <div className="flex items-center justify-between py-3">
      <div className="flex-1 min-w-0 mr-4">
        <p className="text-sm font-semibold text-slate-700">{label}</p>
        {description && <p className="text-xs text-slate-400 mt-0.5">{description}</p>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 flex-shrink-0 rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none ${enabled ? "bg-purple-600" : "bg-slate-200"}`}
      >
        <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${enabled ? "translate-x-5" : "translate-x-0"}`} />
      </button>
    </div>
  );
}

export default function SettingsPage() {
  const { user } = useAuthStore();

  // Profile state
  const [profileForm, setProfileForm] = useState({
    name: user?.name || "",
    email: user?.email || "",
    phone: "",
    company: "Lakshya AI",
    role: user?.role || "Admin",
  });

  // Notification toggles
  const [notifications, setNotifications] = useState({
    emailAlerts: true,
    parseComplete: true,
    matchingComplete: true,
    weeklyReport: false,
    systemUpdates: true,
  });

  // API config
  const [apiConfig, setApiConfig] = useState({
    apiKey: "sk-••••••••••••••••••••••••••••",
    endpoint: import.meta.env.VITE_API_URL || "http://localhost:3001",
    timeout: "30",
    maxRetries: "3",
  });
  const [showApiKey, setShowApiKey] = useState(false);

  // Theme
  const [selectedTheme, setSelectedTheme] = useState<"light" | "dark" | "system">("light");

  const [saved, setSaved] = useState(false);

  const handleSaveProfile = () => {
    // UI-only: show feedback
    setSaved(true);
    toast.success("Profile settings saved!");
    setTimeout(() => setSaved(false), 2000);
  };

  const handleSaveAPI = () => {
    toast.success("API configuration saved!");
  };

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "appearance", label: "Appearance", icon: Palette },
    { id: "api", label: "API Config", icon: Key },
    { id: "security", label: "Security", icon: Shield },
  ];

  const [activeTab, setActiveTab] = useState("profile");

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="p-6 sm:p-8 max-w-5xl mx-auto space-y-6">

        {/* Page Header */}
        <div className="flex items-center gap-4 mb-2">
          <div className="p-2.5 rounded-xl shadow-sm text-white flex-shrink-0" style={{ background: 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)' }}>
            <Settings className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-800">Settings</h1>
            <p className="text-slate-500 text-sm font-medium">Manage your profile, preferences, and system configuration</p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-6">
          {/* Sidebar Tabs */}
          <div className="sm:w-52 flex-shrink-0">
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-2">
              {tabs.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all text-left ${activeTab === id
                    ? "bg-brand-600 text-white shadow-sm"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-800"
                    }`}
                  style={activeTab === id ? { background: '#7C3AED' } : {}}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Content Panel */}
          <div className="flex-1 min-w-0">

            {/* PROFILE TAB */}
            {activeTab === "profile" && (
              <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm transition-all">
                <div className="px-6 py-4 border-b border-slate-50">
                  <h2 className="text-sm font-bold text-slate-800">Profile Information</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Update your personal details</p>
                </div>
                <div className="p-6 space-y-5">
                  {/* Avatar */}
                  <div className="flex items-center gap-5">
                    <div className="h-16 w-16 rounded-2xl flex items-center justify-center shadow-md text-white" style={{ background: 'linear-gradient(135deg, #7C3AED, #9333EA)' }}>
                      <span className="text-2xl font-black">
                        {(profileForm.name || "U").charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-800">{profileForm.name || "User"}</p>
                      <p className="text-xs text-slate-400">{profileForm.role}</p>
                      <button className="mt-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition-colors" style={{ color: '#7C3AED' }}>
                        Change Avatar
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {[
                      { label: "Full Name", key: "name", icon: User, type: "text", placeholder: "Your full name" },
                      { label: "Email Address", key: "email", icon: Mail, type: "email", placeholder: "your@email.com" },
                      { label: "Phone Number", key: "phone", icon: Phone, type: "tel", placeholder: "+1 (555) 000-0000" },
                      { label: "Company", key: "company", icon: Building, type: "text", placeholder: "Company name" },
                    ].map(({ label, key, icon: Icon, type, placeholder }) => (
                      <div key={key}>
                        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">{label}</label>
                        <div className="relative">
                          <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                          <input
                            type={type}
                            value={profileForm[key as keyof typeof profileForm]}
                            onChange={(e) => setProfileForm((p) => ({ ...p, [key]: e.target.value }))}
                            className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                            placeholder={placeholder}
                          />
                        </div>
                      </div>
                    ))}
                  </div>

                  <CustomSelect
                    label="Role"
                    options={[
                      { value: "Admin", label: "Admin" },
                      { value: "Recruiter", label: "Recruiter" },
                      { value: "Analyst", label: "Analyst" },
                      { value: "Viewer", label: "Viewer" }
                    ]}
                    value={profileForm.role}
                    onChange={(val) => setProfileForm(p => ({ ...p, role: val }))}
                  />

                  <button
                    onClick={handleSaveProfile}
                    className={`flex items-center gap-2 px-5 py-2.5 text-sm font-bold rounded-xl transition-all shadow-sm ${saved ? "bg-emerald-600 text-white" : "text-white hover:shadow-md"
                      }`}
                    style={!saved ? { background: '#7C3AED' } : {}}
                  >
                    {saved ? <><Check className="w-4 h-4" /> Saved!</> : <><Save className="w-4 h-4" /> Save Profile</>}
                  </button>
                </div>
              </div>
            )}

            {/* NOTIFICATIONS TAB */}
            {activeTab === "notifications" && (
              <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all">
                <div className="px-6 py-4 border-b border-slate-50">
                  <h2 className="text-sm font-bold text-slate-800">Notification Preferences</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Choose what you want to be notified about</p>
                </div>
                <div className="p-6">
                  <div className="divide-y divide-slate-50">
                    <Toggle enabled={notifications.emailAlerts} onChange={(v) => setNotifications((p) => ({ ...p, emailAlerts: v }))}
                      label="Email Alerts" description="Receive important alerts via email" />
                    <Toggle enabled={notifications.parseComplete} onChange={(v) => setNotifications((p) => ({ ...p, parseComplete: v }))}
                      label="Parse Completed" description="Notify when resume parsing finishes" />
                    <Toggle enabled={notifications.matchingComplete} onChange={(v) => setNotifications((p) => ({ ...p, matchingComplete: v }))}
                      label="Matching Completed" description="Notify when matching algorithm finishes" />
                    <Toggle enabled={notifications.weeklyReport} onChange={(v) => setNotifications((p) => ({ ...p, weeklyReport: v }))}
                      label="Weekly Report" description="Get a weekly summary of platform activity" />
                    <Toggle enabled={notifications.systemUpdates} onChange={(v) => setNotifications((p) => ({ ...p, systemUpdates: v }))}
                      label="System Updates" description="Notifications about system changes and updates" />
                  </div>
                  <button onClick={() => toast.success("Notification preferences saved!")}
                    className="mt-5 flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-xl transition-colors shadow-sm"
                    style={{ background: '#7C3AED' }}>
                    <Save className="w-4 h-4" /> Save Preferences
                  </button>
                </div>
              </div>
            )}

            {/* APPEARANCE TAB */}
            {activeTab === "appearance" && (
              <div className="space-y-5">
                <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all">
                  <div className="px-6 py-4 border-b border-slate-50">
                    <h2 className="text-sm font-bold text-slate-800">Theme</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Choose your preferred color scheme</p>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-3 gap-4">
                      {[
                        { id: "light", label: "Light", icon: Sun, preview: "bg-white border-slate-200" },
                        { id: "dark", label: "Dark", icon: Moon, preview: "bg-slate-800 border-slate-700" },
                        { id: "system", label: "System", icon: Monitor, preview: "bg-gradient-to-br from-white to-slate-800 border-slate-300" },
                      ].map(({ id, label, icon: Icon, preview }) => (
                        <button
                          key={id}
                          onClick={() => setSelectedTheme(id as any)}
                          className={`relative p-4 rounded-2xl border-2 transition-all text-center ${selectedTheme === id
                            ? "border-purple-600 shadow-md bg-purple-50/30"
                            : "border-slate-200 hover:border-purple-400 hover:bg-slate-50"
                            }`}
                        >
                          <div className={`h-16 rounded-xl border mb-3 ${preview}`} />
                          <Icon className="w-4 h-4 mx-auto mb-1 text-slate-600" />
                          <span className="text-xs font-semibold text-slate-700">{label}</span>
                          {selectedTheme === id && (
                            <div className="absolute top-2 right-2 h-5 w-5 rounded-full flex items-center justify-center text-white" style={{ background: '#7C3AED' }}>
                              <Check className="w-3 h-3" />
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Color Preview */}
                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-50">
                    <h2 className="text-sm font-bold text-slate-800">Brand Colors</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Current purple gradient theme (default)</p>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-5 gap-2">
                      {[
                        { name: "50", color: "#faf5ff" }, { name: "100", color: "#f3e8ff" },
                        { name: "300", color: "#d8b4fe" }, { name: "500", color: "#a855f7" },
                        { name: "600", color: "#9333ea" }, { name: "700", color: "#7e22ce" },
                        { name: "800", color: "#6b21a8" }, { name: "900", color: "#581c87" },
                        { name: "950", color: "#3b0764" }, { name: "Grad", color: "linear-gradient(135deg, #581c87, #9333ea)" },
                      ].map(({ name, color }) => (
                        <div key={name} className="text-center">
                          <div className="h-10 rounded-xl mb-1.5 border border-slate-100" style={{
                            background: name === "Grad" ? "linear-gradient(135deg, #581c87, #9333ea)" : color
                          }} />
                          <span className="text-xs text-slate-400">{name}</span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 p-3 rounded-xl border flex items-center gap-2" style={{ background: '#f3e8ff', borderColor: '#d8b4fe' }}>
                      <Zap className="w-4 h-4" style={{ color: '#7C3AED' }} />
                      <span className="text-xs font-semibold" style={{ color: '#7C3AED' }}>Purple Gradient is the default theme and cannot be changed.</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* API CONFIG TAB */}
            {activeTab === "api" && (
              <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all">
                <div className="px-6 py-4 border-b border-slate-50">
                  <h2 className="text-sm font-bold text-slate-800">API Configuration</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Manage API keys and endpoint settings</p>
                </div>
                <div className="p-6 space-y-5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">API Key</label>
                    <div className="flex gap-2">
                      <div className="relative flex-1">
                        <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                          type={showApiKey ? "text" : "password"}
                          value={apiConfig.apiKey}
                          onChange={(e) => setApiConfig((p) => ({ ...p, apiKey: e.target.value }))}
                          className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm font-mono focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                        />
                      </div>
                      <button onClick={() => setShowApiKey(!showApiKey)}
                        className="px-4 py-2.5 border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold rounded-xl transition-colors">
                        {showApiKey ? "Hide" : "Show"}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">API Endpoint</label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <input
                        type="text"
                        value={apiConfig.endpoint}
                        onChange={(e) => setApiConfig((p) => ({ ...p, endpoint: e.target.value }))}
                        className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Timeout (seconds)</label>
                      <input type="number" value={apiConfig.timeout} min="5" max="120"
                        onChange={(e) => setApiConfig((p) => ({ ...p, timeout: e.target.value }))}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all" />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Max Retries</label>
                      <input type="number" value={apiConfig.maxRetries} min="0" max="10"
                        onChange={(e) => setApiConfig((p) => ({ ...p, maxRetries: e.target.value }))}
                        className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all" />
                    </div>
                  </div>

                  <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
                    <p className="text-xs font-semibold text-amber-700">⚠️ Changes to API configuration will take effect after saving. Ensure your endpoint is reachable.</p>
                  </div>

                  <button onClick={handleSaveAPI}
                    className="flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-xl transition-colors shadow-sm"
                    style={{ background: '#7C3AED' }}>
                    <Save className="w-4 h-4" /> Save API Config
                  </button>
                </div>
              </div>
            )}

            {/* SECURITY TAB */}
            {activeTab === "security" && (
              <div className="space-y-5">
                <div className="bg-white dark:bg-slate-800/40 dark:backdrop-blur-xl rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm overflow-hidden transition-all">
                  <div className="px-6 py-4 border-b border-slate-50">
                    <h2 className="text-sm font-bold text-slate-800">Change Password</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Update your account password</p>
                  </div>
                  <div className="p-6 space-y-4">
                    {["Current Password", "New Password", "Confirm New Password"].map((label) => (
                      <div key={label}>
                        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">{label}</label>
                        <input type="password" placeholder="••••••••••••"
                          className="w-full px-4 py-2.5 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all" />
                      </div>
                    ))}
                    <button onClick={() => toast.success("Password updated!")}
                      className="flex items-center gap-2 px-5 py-2.5 text-white text-sm font-bold rounded-xl transition-colors shadow-sm"
                      style={{ background: '#7C3AED' }}>
                      <Shield className="w-4 h-4" /> Update Password
                    </button>
                  </div>
                </div>

                <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-slate-50">
                    <h2 className="text-sm font-bold text-slate-800">Security Settings</h2>
                  </div>
                  <div className="p-6 divide-y divide-slate-50">
                    <Toggle enabled={true} onChange={() => toast("Two-factor auth coming soon")} label="Two-Factor Authentication" description="Add an extra layer of security to your account" />
                    <Toggle enabled={false} onChange={() => toast("Session log coming soon")} label="Session Logging" description="Log all login sessions for audit purposes" />
                    <Toggle enabled={true} onChange={() => { }} label="Login Email Alerts" description="Receive email on new login from unknown device" />
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}

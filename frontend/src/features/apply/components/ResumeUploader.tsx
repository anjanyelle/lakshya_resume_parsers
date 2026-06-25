import { useRef, useState } from "react";
import { FileUp, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { FooterButtons } from "./FooterButtons";
import { useApplicationContext } from "../context/ApplicationContext";
import { previewSections, parseSections, type ParseSectionsResponse } from "../../../services/api/apply";
import { toast } from "react-hot-toast";

const ACCEPTED_TYPES = [".pdf", ".doc", ".docx", ".txt"];
const MAX_SIZE_BYTES = 5 * 1024 * 1024;

export function ResumeUploader() {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const { application, saveSection, nextStep, prevStep } =
    useApplicationContext();
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);

  const handleResumeUpload = async (file: File) => {
    setError("");
    setIsUploading(true);
    setProgress(0);

    try {
      saveSection("resume", {
        fileName: file.name,
        fileSizeKb: Math.round(file.size / 1024),
        uploadStatus: "uploading",
      });

      setProgress(20);
      const previewResponse = await previewSections(file, false);
      console.log("Preview response:", previewResponse);
      
      setProgress(50);
      saveSection("resume", {
        fileName: file.name,
        fileSizeKb: Math.round(file.size / 1024),
        uploadStatus: "parsing",
      });

      const parseResponse = await parseSections(previewResponse, "deberta");
      console.log("Parse response:", parseResponse);
      
      setProgress(100);
      saveSection("resume", {
        fileName: file.name,
        fileSizeKb: Math.round(file.size / 1024),
        uploadStatus: "parsed",
      });

      populateFormWithParsedData(parseResponse);
      toast.success("Resume parsed successfully!");
    } catch (err: any) {
      console.error("Resume upload error:", err);
      setError(err.message || "Failed to upload and parse resume. Please try again.");
      toast.error(err.message || "Failed to upload resume");
      saveSection("resume", {
        fileName: "",
        fileSizeKb: 0,
        uploadStatus: "idle",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const populateFormWithParsedData = (data: ParseSectionsResponse) => {
    if (data.contact) {
      const nameParts = (data.contact.name || "").split(" ");
      const firstName = nameParts[0] || "";
      const lastName = nameParts.slice(1).join(" ") || "";

      saveSection("personalInfo", {
        ...application.personalInfo,
        firstName,
        lastName,
        email: data.contact.email || application.personalInfo.email,
        phone: data.contact.phone || application.personalInfo.phone,
        linkedIn: data.contact.linkedin || application.personalInfo.linkedIn,
        portfolio: data.contact.portfolio || data.contact.portfolio_url || data.contact.website || application.personalInfo.portfolio,
      });
    }

    if (data.work_experience && data.work_experience.length > 0) {
      const experiences = data.work_experience.map((exp) => {
        const startDate = exp.start_date ? new Date(exp.start_date) : null;
        const endDate = exp.end_date ? new Date(exp.end_date) : null;

        return {
          id: crypto.randomUUID(),
          jobTitle: exp.job_title || "",
          company: exp.company_name || "",
          employmentType: "",
          location: exp.location || "",
          country: "",
          state: "",
          city: "",
          startMonth: startDate ? String(startDate.getMonth() + 1).padStart(2, "0") : "",
          startYear: startDate ? String(startDate.getFullYear()) : "",
          endMonth: endDate ? String(endDate.getMonth() + 1).padStart(2, "0") : "",
          endYear: endDate ? String(endDate.getFullYear()) : "",
          duration: "",
          currentlyWorking: exp.is_current || false,
          roleDescription: exp.description || "",
          technologiesUsed: "",
          skillsUsed: "",
        };
      });
      saveSection("experiences", experiences);
    }

    if (data.education && data.education.length > 0) {
      const education = data.education.map((edu) => ({
        id: crypto.randomUUID(),
        degree: edu.degree || "",
        institution: edu.institution || "",
        fieldOfStudy: edu.field_of_study || "",
        startYear: edu.start_date || "",
        endYear: edu.end_date || "",
        cgpa: edu.gpa ? String(edu.gpa) : "",
        percentage: "",
        description: edu.description || "",
      }));
      saveSection("education", education);
    }

    if (data.skills && data.skills.length > 0) {
      saveSection("skills", data.skills);
    }

    if (data.certifications && data.certifications.length > 0) {
      const certifications = data.certifications.map((cert) => ({
        id: crypto.randomUUID(),
        certificationName: cert.name || "",
        organization: cert.issuing_organization || "",
        issueDate: cert.issue_date || "",
        expiryDate: cert.expiry_date || "",
        credentialId: cert.credential_id || "",
        credentialUrl: "",
      }));
      saveSection("certifications", certifications);
    }

    if (data.projects && data.projects.length > 0) {
      const projects = data.projects.map((proj) => ({
        id: crypto.randomUUID(),
        projectName: proj.name || "",
        client: proj.client || "",
        role: proj.role || "",
        duration: proj.duration || "",
        technologies: proj.technologies || "",
        description: proj.description || "",
        projectUrl: proj.url || "",
      }));
      saveSection("projects", projects);
    }
  };

  const onFileSelect = (file?: File) => {
    if (!file) {
      return;
    }

    const extension = `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!ACCEPTED_TYPES.includes(extension)) {
      setError("Only PDF, DOC, DOCX, TXT files are supported.");
      return;
    }

    if (file.size > MAX_SIZE_BYTES) {
      setError("File exceeds 5MB size limit.");
      return;
    }

    handleResumeUpload(file);
  };

  return (
    <div className="mx-auto max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-center text-4xl font-semibold text-slate-800">Autofill with Resume</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <p className="text-sm font-semibold text-slate-500">* Indicates a required field</p>
          <p className="text-sm text-slate-600">
            Please upload your resume/CV (PDF and Word Document preferred). Once uploaded, the
            system will parse your resume and make additional updates before submitting your
            application.
          </p>
          <p className="text-xs text-slate-500">Upload DOC, DOCX, HTML, PDF, or TXT file types (5MB max)</p>

          <div
            className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              onFileSelect(event.dataTransfer.files[0]);
            }}
          >
            <FileUp className="mx-auto mb-3 h-10 w-10 text-brand-500" />
            <p className="text-slate-700">Drop file here or select one</p>
            <Button
              className="mt-4"
              variant="secondary"
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
            >
              Select File
            </Button>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept={ACCEPTED_TYPES.join(",")}
              onChange={(event) => onFileSelect(event.target.files?.[0])}
            />
          </div>

          {error && <p className="text-sm text-red-600">{error}</p>}

          {application.resume.uploadStatus === "uploading" && (
            <div className="space-y-2">
              <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-brand-600 transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-slate-500">Uploading... {progress}%</p>
            </div>
          )}

          {(application.resume.uploadStatus === "uploaded" ||
            application.resume.uploadStatus === "parsing" ||
            application.resume.uploadStatus === "parsed") && (
            <div className="rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700">
              Resume Uploaded Successfully: {application.resume.fileName} ({application.resume.fileSizeKb} KB)
            </div>
          )}

          {application.resume.uploadStatus === "parsing" && (
            <div className="flex items-center gap-2 rounded-xl bg-brand-50 p-4 text-sm text-brand-700">
              <Loader2 className="h-4 w-4 animate-spin" /> Parsing Resume...
            </div>
          )}
        </CardContent>
      </Card>

      <FooterButtons
        onBack={prevStep}
        continueType="button"
        onContinue={nextStep}
        disabled={application.resume.uploadStatus !== "parsed"}
      />
    </div>
  );
}

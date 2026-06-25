import { useState } from "react";
import { Loader2, PencilLine } from "lucide-react";
import toast from "react-hot-toast";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Badge } from "../../../components/ui/badge";
import { WIZARD_STEPS, useApplicationContext } from "../context/ApplicationContext";

const stepTargetMap = {
  account: "account",
  resume: "resume",
  personal: "information",
  experience: "experience",
  questions: "questions",
  disclosures: "disclosures",
} as const;

export function ReviewPage() {
  const { application, prevStep, setCurrentStep, resetApplication, clearDraft } = useApplicationContext();
  const [submitting, setSubmitting] = useState(false);

  const summaryCards = [
    {
      key: "account",
      title: "Account",
      editStep: stepTargetMap.account,
      content: <p className="text-sm text-slate-600">{application.account.email}</p>,
    },
    {
      key: "resume",
      title: "Resume",
      editStep: stepTargetMap.resume,
      content: (
        <p className="text-sm text-slate-600">
          {application.resume.fileName} ({application.resume.fileSizeKb} KB)
        </p>
      ),
    },
    {
      key: "personal",
      title: "Personal Information",
      editStep: stepTargetMap.personal,
      content: (
        <div className="space-y-1 text-sm text-slate-600">
          <p>
            {application.personalInfo.firstName} {application.personalInfo.middleName} {application.personalInfo.lastName}
          </p>
          <p>{application.personalInfo.email}</p>
          <p>
            {application.personalInfo.countryCode} {application.personalInfo.mobile}
          </p>
          <p>
            {application.personalInfo.city}, {application.personalInfo.state}, {application.personalInfo.country}
          </p>
        </div>
      ),
    },
    {
      key: "experience",
      title: "Experience",
      editStep: stepTargetMap.experience,
      content: (
        <div className="space-y-2">
          {application.experiences.map((experience) => (
            <p key={experience.id} className="text-sm text-slate-600">
              {experience.jobTitle} - {experience.company}
            </p>
          ))}
        </div>
      ),
    },
    {
      key: "education",
      title: "Education",
      editStep: stepTargetMap.experience,
      content: (
        <div className="space-y-2">
          {application.education.map((education) => (
            <p key={education.id} className="text-sm text-slate-600">
              {education.degree} - {education.institution}
            </p>
          ))}
        </div>
      ),
    },
    {
      key: "certifications",
      title: "Certifications",
      editStep: stepTargetMap.experience,
      content: (
        <div className="space-y-2">
          {application.certifications.map((certification) => (
            <p key={certification.id} className="text-sm text-slate-600">
              {certification.certificationName} - {certification.organization}
            </p>
          ))}
        </div>
      ),
    },
    {
      key: "projects",
      title: "Projects",
      editStep: stepTargetMap.experience,
      content: (
        <div className="space-y-2">
          {application.projects.map((project) => (
            <p key={project.id} className="text-sm text-slate-600">
              {project.projectName} - {project.role}
            </p>
          ))}
        </div>
      ),
    },
    {
      key: "languages",
      title: "Languages",
      editStep: stepTargetMap.experience,
      content: (
        <div className="space-y-2">
          {application.languages.map((language) => (
            <p key={language.id} className="text-sm text-slate-600">
              {language.language} - {language.proficiency}
            </p>
          ))}
        </div>
      ),
    },
    {
      key: "skills",
      title: "Skills",
      editStep: stepTargetMap.experience,
      content: (
        <div className="flex flex-wrap gap-2">
          {application.skills.map((skill) => (
            <Badge key={skill}>{skill}</Badge>
          ))}
        </div>
      ),
    },
    {
      key: "questions",
      title: "Application Questions",
      editStep: stepTargetMap.questions,
      content: <p className="text-sm text-slate-600">Notice period: {application.questions.noticePeriod || "N/A"}</p>,
    },
    {
      key: "disclosures",
      title: "Disclosures",
      editStep: stepTargetMap.disclosures,
      content: <p className="text-sm text-slate-600">Gender: {application.disclosures.gender}</p>,
    },
  ] as const;

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      await new Promise((resolve) => setTimeout(resolve, 700));
      clearDraft();
      toast.success("Application submitted locally. Ready for parser integration.");
      resetApplication();
    } catch (error) {
      console.error(error);
      toast.error("Unable to complete local submit simulation.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-subtle">
        <h2 className="text-center text-4xl font-semibold text-slate-800">Review</h2>
        <p className="mt-1 text-sm text-slate-600">
          Verify your details before submitting the final application payload.
        </p>
      </div>

      {summaryCards.map((card) => (
        <Card key={card.key}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0">
            <CardTitle>{card.title}</CardTitle>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setCurrentStep(card.editStep)}
            >
              <PencilLine className="mr-1 h-4 w-4" /> Edit
            </Button>
          </CardHeader>
          <CardContent>{card.content}</CardContent>
        </Card>
      ))}

      <div className="sticky bottom-0 z-20 border-t border-slate-200 bg-white/95 px-2 py-4 backdrop-blur">
        <div className="mx-auto flex max-w-4xl justify-end gap-3">
          <Button variant="secondary" onClick={prevStep}>Back</Button>
          <Button onClick={handleSubmit} disabled={submitting}>
            {submitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Submitting...
              </>
            ) : (
              "Submit Application"
            )}
          </Button>
        </div>
      </div>

      <p className="sr-only">{WIZARD_STEPS.length}</p>
    </div>
  );
}

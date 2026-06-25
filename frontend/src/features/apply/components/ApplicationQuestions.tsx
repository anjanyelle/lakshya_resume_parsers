import { useForm } from "react-hook-form";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Textarea } from "../../../components/ui/textarea";
import { FooterButtons } from "./FooterButtons";
import { useApplicationContext } from "../context/ApplicationContext";
import type { ApplicationQuestionsInfo } from "../types/application";

export function ApplicationQuestions() {
  const { application, saveSection, nextStep, prevStep } = useApplicationContext();
  const { register, handleSubmit } = useForm<ApplicationQuestionsInfo>({
    defaultValues: application.questions,
  });

  const onSubmit = (values: ApplicationQuestionsInfo) => {
    saveSection("questions", values);
    nextStep();
  };

  const yesNoOptions = [
    { value: "", label: "Select" },
    { value: "yes", label: "Yes" },
    { value: "no", label: "No" },
  ];

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="mx-auto max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-center text-4xl font-semibold text-slate-800">Application Questions</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 sm:grid-cols-2">
          <p className="sm:col-span-2 text-sm font-semibold text-slate-500">* Indicates a required field</p>
          <div><Label>How did you hear about us?</Label><Input {...register("hearAboutUs")} /></div>
          <div><Label>Expected Salary</Label><Input {...register("expectedSalary")} /></div>
          <div><Label>Current Salary</Label><Input {...register("currentSalary")} /></div>
          <div><Label>Notice Period</Label><Input {...register("noticePeriod")} /></div>

          <div>
            <Label>Willing to Relocate</Label>
            <select className="h-11 w-full rounded-xl border border-slate-300 px-3" {...register("willingToRelocate")}>
              {yesNoOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          <div>
            <Label>Willing to Travel</Label>
            <select className="h-11 w-full rounded-xl border border-slate-300 px-3" {...register("willingToTravel")}>
              {yesNoOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>

          <div>
            <Label>Do you require Sponsorship?</Label>
            <select className="h-11 w-full rounded-xl border border-slate-300 px-3" {...register("requiresSponsorship")}>
              {yesNoOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </div>
          <div><Label>Years of Experience</Label><Input {...register("yearsOfExperience")} /></div>
          <div><Label>Current Employer</Label><Input {...register("currentEmployer")} /></div>
          <div className="sm:col-span-2">
            <Label>Reason for Job Change</Label>
            <Textarea {...register("reasonForJobChange")} />
          </div>
        </CardContent>
      </Card>

      <FooterButtons onBack={prevStep} />
    </form>
  );
}

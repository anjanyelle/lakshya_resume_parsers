import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Checkbox } from "../../../components/ui/checkbox";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Button } from "../../../components/ui/button";
import { useApplicationContext } from "../context/ApplicationContext";

const schema = z
  .object({
    email: z.email("Error: Please enter a valid email"),
    password: z
      .string()
      .min(1, "Error: Please enter your password")
      .min(8, "Minimum 8 characters")
      .regex(/[A-Z]/, "At least one uppercase letter")
      .regex(/[a-z]/, "At least one lowercase letter")
      .regex(/\d/, "At least one number")
      .regex(/[^A-Za-z0-9]/, "At least one special character"),
    confirmPassword: z.string().min(1, "Error: Please verify your password"),
    agreedToTerms: z.boolean().refine((value) => value, "Please accept Terms & Conditions and Privacy Policy"),
  })
  .refine((value) => value.password === value.confirmPassword, {
    path: ["confirmPassword"],
    message: "Error: Passwords do not match",
  });

type FormValues = z.infer<typeof schema>;

export function CreateAccountForm() {
  const { application, saveSection, nextStep } = useApplicationContext();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: application.account,
  });

  const onSubmit = (values: FormValues) => {
    saveSection("account", values);
    nextStep();
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="mx-auto max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle className="text-center text-4xl font-semibold text-slate-800">Create Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="mx-auto max-w-md">
            <p className="mb-1 text-sm font-semibold text-slate-700">Password Requirements:</p>
            <ul className="mb-6 list-disc space-y-1 pl-5 text-sm text-slate-600">
              <li>An uppercase character</li>
              <li>A lowercase character</li>
              <li>A special character</li>
              <li>A numeric character</li>
              <li>A minimum of 8 characters</li>
              <li>An alphabetic character</li>
            </ul>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address <span className="text-red-600">*</span></Label>
                <Input id="email" type="email" {...register("email")} />
                {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password <span className="text-red-600">*</span></Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    className={errors.password ? "border-red-500 pr-10 focus-visible:ring-red-300" : "pr-10"}
                    {...register("password")}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.password && <p className="text-xs text-red-600">{errors.password.message}</p>}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Verify New Password <span className="text-red-600">*</span></Label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    className={errors.confirmPassword ? "border-red-500 pr-10 focus-visible:ring-red-300" : "pr-10"}
                    {...register("confirmPassword")}
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                    aria-label="Toggle verify password visibility"
                  >
                    {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-xs text-red-600">{errors.confirmPassword.message}</p>
                )}
              </div>

              <p className="text-sm leading-relaxed text-slate-700">
                By creating an account, you agree to the collection and processing of your personal information for recruitment purposes in accordance with the
                <a href="#" className="mx-1 text-brand-600 underline">Lakshya Technologies Applicant Privacy Notice</a>
                and
                <a href="#" className="mx-1 text-brand-600 underline">Privacy Policy</a>.
              </p>

              <label className="flex items-start gap-3 pt-0.5">
                <Checkbox {...register("agreedToTerms")} />
                <span className="text-sm leading-tight text-slate-700">I have read and agree to the Terms &amp; Conditions and Privacy Policy.</span>
              </label>
              {errors.agreedToTerms && (
                <p className="text-xs text-red-600">{errors.agreedToTerms.message}</p>
              )}

              <div className="mt-3 flex justify-end border-t border-slate-200 pt-3">
                <Button type="submit" className="min-w-48" size="lg">
                  Create Account
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </form>
  );
}

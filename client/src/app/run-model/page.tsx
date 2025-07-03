"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Container,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from "@mui/material";

import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import ModelSetup from "./components/ModelSetup";

export default function RunModel() {
  const [apiCall, setApiCall] = useState("Loading...");

  useEffect(() => {
    fetch("http://localhost:8080/api/home")
      .then((res) => res.json())
      .then((data) => {
        console.log(data);
        setApiCall(data.message);
      });
  }, []);

  const steps = ["Setup", "Context Validation", "Model Running", "Output"];

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  // const { data: session, status } = useSession(); // include status

  const isValidYear = (year: string) => {
    const num = Number(year);
    return /^\d{4}$/.test(year) && num >= 1950 && num <= 2050;
  };

  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return true;
      // case 1:
      //   return (
      //     formData.firstName &&
      //     formData.surname &&
      //     formData.studentEmail &&
      //     formData.course &&
      //     (formData.course !== "other" ||
      //       (formData.customCourse && formData.customCourse.length >= 3)) &&
      //     formData.uclId &&
      //     ((formData.graduationYear && formData.graduationYear !== "custom") ||
      //       (formData.customGraduationYear &&
      //         isValidYear(formData.customGraduationYear))) &&
      //     formData.personalEmail &&
      //     /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(
      //       formData.personalEmail
      //     ) &&
      //     formData.studentType &&
      //     formData.preferredJobLocation
      //   );
      // case 2:
      //   return (
      //     formData.ethnicity &&
      //     formData.gender &&
      //     formData.dateOfBirth &&
      //     formData.address
      //   );
      // case 3:
      //   return (
      //     formData.receiveUpdates &&
      //     formData.shareEmail &&
      //     formData.isPrivate &&
      //     formData.resumeReminderInterval
      //   );
      default:
        return true;
    }
  };

  // Form data state
  // const [formData, setFormData] = useState({
  //   // Personal Information
  //   firstName: "",
  //   surname: "",
  //   studentEmail: session?.user.email || "ucabbjt@ucl.ac.uk",
  //   uclId: session?.user.upi || "bjtho63",
  //   studentType: "",
  //   personalEmail: "",
  //   graduationYear: "",
  //   customGraduationYear: "",
  //   course: "",
  //   customCourse: "",
  //   preferredJobLocation: "",

  //   // Personal details
  //   address: "",
  //   dateOfBirth: "",
  //   gender: "",
  //   ethnicity: "",

  //   // Preferences
  //   receiveUpdates: true,
  //   shareEmail: true,
  //   isPrivate: true,
  //   resumeReminderInterval: "Two months",
  // });
  // useEffect(() => {
  //   if (status === "authenticated" && session?.user) {
  //     const fullName = session.user.name || "";
  //     const [firstName, ...rest] = fullName.split(" ");
  //     const surname = rest.join(" ");

  //     setFormData((prev) => ({
  //       ...prev,
  //       firstName,
  //       surname,
  //       studentEmail: session.user.email || prev.studentEmail,
  //       uclId: session.user.upi || prev.uclId,
  //     }));
  //   } else if (status === "unauthenticated") {
  //     // Redirect if not authenticated
  //     router.push("/login");
  //   }
  // }, [session, status, router]);

  // const handleNext = async () => {
  //   console.log(`[Registration Page] Moving to step ${activeStep + 1}`);
  //   if (activeStep === 0) {
  //     setActiveStep((prevStep) => prevStep + 1);
  //   }
  //   try {
  //     let response;
  //     if (activeStep === 1) {
  //     } else if (activeStep === 2) {
  //     }

  //     if (response?.success) {
  //       setActiveStep((prevStep) => prevStep + 1);
  //     } else {
  //       console.error('Error updating:', response?.error || 'Unknown error');
  //     }
  //   } catch (err) {
  //     console.error('Unexpected error during step transition:', err);
  //   }
  // };

  const handleBack = () => {
    console.log(`[Registration Page] Moving back to step ${activeStep - 1}`);
    setActiveStep((prevStep) => prevStep - 1);
  };

  // const handleSubmit = async () => {
  //   try {
  //     console.log('[Registration Page] Starting form submission');
  //     setSaving(true);
  //     setError(null);
  //     const preferencesResponse = await insertStudentPreferences(formData);

  //     if (preferencesResponse?.success) {
  //       setSaving(false);
  //       router.push('/my-profile');
  //     } else {
  //       console.error('Error updating:', preferencesResponse?.error || 'Unknown error');
  //     }
  //   } catch (err) {
  //     console.error('[Registration Page] Error during registration:', err);
  //     if (err instanceof Error) {
  //       console.error('[Registration Page] Error details:', {
  //         message: err.message,
  //         stack: err.stack,
  //         name: err.name
  //       });
  //     }
  //     setError('Failed to complete registration. Please try again.');
  //   } finally {
  //     setSaving(false);
  //   }
  // };

  const renderContent = (step: number) => {
    switch (step) {
      case 0: // Welcome Step
        return (
          <Box sx={{ textAlign: "center" }}>
            <ModelSetup />
          </Box>
        );
      // case 1:
      //   return <PersonalInfoForm formData={formData} setFormData={setFormData} />;
      // case 2:
      //   return <PersonalDetailsForm formData={formData} setFormData={setFormData} />;
      // case 3:
      //   return <PreferencesForm formData={formData} setFormData={setFormData} />;
      // default:
      //   return null;
    }
  };

  if (loading) {
    console.log("[Registration Page] Rendering loading state");
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading your information...
        </Typography>
      </Container>
    );
  }

  console.log("[Registration Page] Rendering main content");
  return (
    <Box sx={{ px: 5 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderContent(activeStep)}

        <Box sx={{ display: "flex", justifyContent: "space-between", mt: 4 }}>
          <Button disabled={activeStep === 0} onClick={handleBack}>
            Back
          </Button>

          <Box>
            {activeStep === steps.length - 1 ? (
              <Button variant="contained" onClick={() => {}} disabled={saving}>
                {saving ? (
                  <CircularProgress size={24} />
                ) : (
                  "Complete Registration"
                )}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={() => {}}
                disabled={!isStepValid()}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

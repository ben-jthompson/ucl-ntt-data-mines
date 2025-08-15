"use client";

import { useState } from "react";
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
import dynamic from "next/dynamic";

import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

import Setup from "./components/Setup";
import ContextValidation from "./components/ContextValidation";
import ModelRunning from "./components/ModelRunning";
import Output from "./components/Output";

import { UploadedFile } from "@/types/UploadedFile";

const ResultMap = dynamic(() => import("../../components/ResultMap"), {
  ssr: false,
});

export default function RunModel() {
  const steps = ["Setup", "Context Validation", "Model Running", "Output"];

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [modelRunning, setModelRunning] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // state for user input
  const [coords, setCoords] = useState<[number, number] | null>(null);
  const [radius, setRadius] = useState(10000);
  const [location, setLocation] = useState<string | undefined>("UK");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[] | null>(
    null
  );
  const [model, setModel] = useState<{}>({ place: "holder" });

  // state for model progress
  const [status, setStatus] = useState(false);

  const router = useRouter();

  {
    /* logic to allow/disable progress */
  }
  const isStepValid = () => {
    switch (activeStep) {
      case 0:
        return coords != null && loading == false;
      case 1:
        // TODO: wait for loading before allowing
        return loading == false;
      case 2:
        return modelRunning == false;
      // case 3:
      default:
        return true;
    }
  };

  // increment progress bar
  const handleNext = async () => {
    console.log(`Moving to step ${activeStep + 1}`);
    setActiveStep((prevStep) => prevStep + 1);
  };
  // decrement progress bar
  const handleBack = () => {
    console.log(`Moving back to step ${activeStep - 1}`);
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleComplete = () => {
    console.log(`Routing to home`);
    router.push("/");
  };

  const renderContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Setup
            loading={loading}
            setLoading={setLoading}
            coords={coords}
            setCoords={setCoords}
            radius={radius}
            setRadius={setRadius}
            uploadedFiles={uploadedFiles}
            setUploadedFiles={setUploadedFiles}
          />
        );
      case 1:
        return (
          coords && (
            <ContextValidation
              loading={loading}
              setLoading={setLoading}
              coords={coords}
              radius={radius}
              model={model}
              setLocation={setLocation}
              setModel={setModel}
              uploadedFiles={uploadedFiles}
            />
          )
        );
      case 2:
        setModelRunning(true);
        return coords ? (
          <ModelRunning
            location={location}
            query={"Gravitational Energy"}
            coords={coords}
            buffer={radius}
            onFinishedRunning={setModelRunning}
          />
        ) : (
          <Container maxWidth="md" sx={{ py: 4 }}>
            <CircularProgress />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Something went wrong. Please reload the page and retry.
            </Typography>
          </Container>
        );
      case 3:
        return coords && <Output coords={coords} radius={radius} />;
      // default:
      //   return null;
    }
  };

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
          <Button
            disabled={activeStep === 0 || activeStep === 3}
            onClick={handleBack}
          >
            Back
          </Button>

          <Box>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                onClick={handleComplete}
                disabled={saving}
              >
                {saving ? <CircularProgress size={24} /> : "Complete"}
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleNext}
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

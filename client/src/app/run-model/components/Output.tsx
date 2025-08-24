"use client";

import { Grid, Box, Typography, Paper, Button } from "@mui/material";
import dynamic from "next/dynamic";
import { ReportFile } from "@/types/ReportFile";
import axios from "axios";
const ResultMap = dynamic(() => import("../../../components/ResultMap"), {
  ssr: false,
});

const downloadReport = async (clientId: string, fileName: string) => {
  try {
    const response = await axios.get(
      `http://localhost:8080/api/reports/${clientId}/files/${fileName}`,
      {
        responseType: "blob",
      }
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("Download failed", error);
  }
};

const downloadReportAccompaniment = async (
  clientId: string,
  fileName: string
) => {
  try {
    const response = await axios.get(
      `http://localhost:8080/api/reports/${clientId}/files/${fileName}/zip`,
      { responseType: "blob" }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Default to backend-provided filename, fallback to client side
    const suggestedName = `${fileName.replace(/\.pdf$/, "")}_accompanying.zip`;
    link.setAttribute("download", suggestedName);

    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error("Download failed", error);
  }
};

export default function Output({
  radius,
  result,
}: {
  radius: number;
  result: ReportFile;
}) {
  const clientId = localStorage.getItem("clientId");
  return (
    <Grid container sx={{ height: "100vh" }}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Box sx={{ width: "100%", height: "100%" }}>
          <ResultMap coords={null} radius={radius} result={result} />
        </Box>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Box sx={{ p: 3, width: "100%", textAlign: "left" }}>
          <Typography variant="h5" gutterBottom>
            Your Report
          </Typography>

          <Typography variant="body1" color="text.secondary" gutterBottom>
            Click on the marker to view the report.
          </Typography>

          <Box sx={{ mt: 3, display: "flex", flexDirection: "column", gap: 2 }}>
            <Button
              size="small"
              variant="contained"
              onClick={() =>
                clientId && downloadReport(clientId, result.file_name)
              }
            >
              Download Report
            </Button>

            <Button
              size="small"
              variant="contained"
              onClick={() =>
                clientId &&
                downloadReportAccompaniment(clientId, result.file_name)
              }
            >
              Download Accompanying Files
            </Button>
          </Box>
        </Box>
      </Grid>
    </Grid>
  );
}

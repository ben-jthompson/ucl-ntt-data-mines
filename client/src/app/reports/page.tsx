"use client";

import { Grid, Box, Typography } from "@mui/material";

import { useState, useEffect } from "react";
import axios from "axios";
import dynamic from "next/dynamic";
import { ReportFile } from "@/types/ReportFile";
import ReportsMenu from "@/components/ReportsMenu";
const ResultMap = dynamic(() => import("../../components/ResultMap"), {
  ssr: false,
});
const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export default function Reports() {
  const [reports, setReports] = useState<ReportFile[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [client, setClient] = useState<string | null>(null);
  useEffect(() => {
    const clientId = localStorage.getItem("clientId");
    axios
      .get(`${backendUrl}/api/reports/${clientId}`)
      .then((response) => {
        console.log("Response:", response.data);
        if (response.data.success && response.data.files.length > 0) {
          setReports(response.data.files);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => {
        setLoading(false);
        setClient(clientId);
      });
  }, []);
  return (
    <Grid
      container
      justifyContent="center"
      alignItems="center"
      style={{ minHeight: "100vh" }}
    >
      {" "}
      {loading ? (
        <Typography>Searching for reports...</Typography>
      ) : reports ? (
        <>
          <Grid size={{ xs: 12, md: 6 }}>
            <Box
              sx={{
                p: 3,
                textAlign: "center",
              }}
            >
              <ResultMap coords={null} radius={0} reports={reports} />
            </Box>
          </Grid>
          <Grid size={{ xs: 12, md: 6 }}>
            {client && (
              <ReportsMenu
                reports={reports}
                clientId={client}
                setReports={setReports}
              />
            )}
          </Grid>
        </>
      ) : (
        <Typography>
          No reports currently completed. Navigate to Run Model page to get
          started!
        </Typography>
      )}
    </Grid>
  );
}

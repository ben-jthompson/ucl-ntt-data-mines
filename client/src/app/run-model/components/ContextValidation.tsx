"use client";

import {
  Grid,
  Box,
  Typography,
  Accordion,
  AccordionDetails,
  AccordionSummary,
} from "@mui/material";

import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import axios from "axios";
import { useState, useEffect } from "react";
import { UploadedFile } from "@/types/UploadedFile";
import dynamic from "next/dynamic";

const ResultMap = dynamic(() => import("../../../components/ResultMap"), {
  ssr: false,
});

export default function ContextValidation({
  loading,
  setLoading,
  coords,
  radius,
  setLocation,
  uploadedFiles,
}: {
  loading: boolean;
  setLoading: (loading: boolean) => void;
  coords: [number, number];
  radius: number;
  setLocation: (location: string | undefined) => void;
  uploadedFiles: UploadedFile[] | null;
}) {
  // Store for OpenStreetMap API Response
  type AreaDescription = {
    locality?: string;
    county?: string;
    country?: string;
    fullAddress?: string;
  };
  const [areaDescription, setAreaDescription] = useState<AreaDescription>({
    locality: "",
    county: "",
    country: "",
    fullAddress: "",
  });

  const apiUrl = `https://nominatim.openstreetmap.org/reverse?lat=${coords[0]}&lon=${coords[1]}&format=json`;
  useEffect(() => {
    setLoading(true);
    axios.get(apiUrl).then((res) => {
      const data = res.data;
      setAreaDescription({
        locality:
          data.address.locality ||
          data.address.neighbourhood ||
          data.address.suburb ||
          data.address.hamlet ||
          data.address.village ||
          data.address.town ||
          data.address.city ||
          data.address.county ||
          "",
        county: data.address.county || "",
        fullAddress: data.display_name || "",
      });
      setLocation(
        data.address.locality ||
          data.address.neighbourhood ||
          data.address.suburb ||
          data.address.hamlet ||
          data.address.village ||
          data.address.town ||
          data.address.city ||
          data.address.county ||
          "UK"
      );
      setLoading(false);
    });
  }, [setLocation, apiUrl, setLoading]);
  console.log(uploadedFiles, "up");
  return (
    <Grid container spacing={6}>
      <Grid size={{ xs: 12, md: 6 }}>
        <Box
          sx={{
            bgcolor: "background.paper",
            p: 3,
            borderRadius: 1,
            border: "1px solid",
            borderColor: "divider",
            textAlign: "center",
          }}
        >
          <Typography variant="h6" gutterBottom>
            Documents and Preferences
          </Typography>

          {/* Uploaded Files List */}
          {uploadedFiles && uploadedFiles.length ? (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Uploaded Files
              </Typography>
              <Box
                mt={3}
                sx={{
                  maxHeight: 200,
                  overflowY: "auto",
                  border: "1px solid #ccc",
                  borderRadius: 2,
                  p: 1,
                }}
              >
                {uploadedFiles.map((file) => (
                  <Accordion
                    key={file.file_name}
                    sx={{ mb: 1, borderRadius: 2, boxShadow: 1 }}
                  >
                    <AccordionSummary
                      expandIcon={<ArrowDropDownIcon />}
                      aria-controls={`${file.file_name}-content`}
                      id={`${file.file_name}-header`}
                    >
                      <Typography variant="subtitle1" fontWeight="bold">
                        {file.display_name}
                      </Typography>
                    </AccordionSummary>

                    <AccordionDetails>
                      <Box
                        sx={{
                          backgroundColor: "background.default",

                          p: 2,
                          borderRadius: 1,
                        }}
                      >
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Description:</strong>{" "}
                          {file.description || "No description provided"}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Tags:</strong>{" "}
                          {file.tags?.length ? file.tags.join(", ") : "No tags"}
                        </Typography>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            </Box>
          ) : (
            <Typography>No files uploaded.</Typography>
          )}
        </Box>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <Box
          sx={{
            bgcolor: "background.paper",
            p: 3,
            textAlign: "center",
          }}
        >
          <ResultMap coords={coords} radius={radius} />
          {!loading && (
            <Box>
              {areaDescription.locality ? (
                <Typography>
                  Searching in this area: {areaDescription.locality}
                </Typography>
              ) : (
                <Typography>
                  Searching in this area: {areaDescription.county}
                </Typography>
              )}
              <Typography>
                Full address: {areaDescription.fullAddress}
              </Typography>
            </Box>
          )}
        </Box>
      </Grid>
    </Grid>
  );
}

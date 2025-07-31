"use client";

import {
  Grid,
  Box,
  Typography,
  Link,
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
  coords,
  radius,
  model,
  setModel,
  setLocation,
  uploadedFiles,
}: {
  coords: [number, number];
  radius: number;
  model: {};
  setModel: (model: {}) => void;
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
  // Resources found from the internet
  type foundResource = {
    file: string;
    source: string;
    description?: string;
  };
  const [foundResources, setFoundResources] = useState<foundResource[]>([
    {
      file: "Abandoned Mines Dataset",
      source:
        "https://www.data.gov.uk/dataset/15777eb2-a97e-4dc8-b435-0e4292d6575c/abandoned-mines-catalogue",
      description: "Description of plans for abandoned mines in the UK",
    },
  ]);

  const apiUrl = `https://nominatim.openstreetmap.org/reverse?lat=${coords[0]}&lon=${coords[1]}&format=json`;
  useEffect(() => {
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
    });
  }, []);

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
          {uploadedFiles && (
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
                {uploadedFiles.map((file, ind) => (
                  <Accordion key={file.file_name}>
                    <AccordionSummary
                      expandIcon={<ArrowDropDownIcon />}
                      aria-controls="panel1-content"
                      id={file.file_name}
                    >
                      <Typography component="span">{file.file_name}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography>{file.description}</Typography>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            </Box>
          )}
          {/* Uploaded Files List */}
          {foundResources && (
            <Box mt={3}>
              <Typography variant="subtitle1" gutterBottom>
                Key Resources found
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
                {foundResources.map((resource, ind) => (
                  <Accordion key={resource.file}>
                    <AccordionSummary
                      expandIcon={<ArrowDropDownIcon />}
                      aria-controls="panel1-content"
                      id={resource.file}
                    >
                      <Typography component="span">{resource.file}</Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Typography>
                        {resource.description || "No description available."}
                      </Typography>
                      <Link
                        href={resource.source}
                        target="_blank"
                        rel="noopener noreferrer"
                        underline="hover"
                        color="#00CEC8"
                      >
                        View Source
                      </Link>
                    </AccordionDetails>
                  </Accordion>
                ))}
              </Box>
            </Box>
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
          <ResultMap coords={coords} radius={radius} result={false} />
          {areaDescription.locality ? (
            <Typography>
              Searching in this area: {areaDescription.locality}
            </Typography>
          ) : (
            <Typography>
              Searching in this area: {areaDescription.county}
            </Typography>
          )}
          <Typography>{areaDescription.fullAddress}</Typography>
        </Box>
      </Grid>
    </Grid>
  );
}

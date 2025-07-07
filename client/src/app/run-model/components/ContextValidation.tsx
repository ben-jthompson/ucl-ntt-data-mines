"use client";

import {
  Grid,
  Box,
  Typography,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
  List,
  ListItem,
  ListItemText,
  Button,
  SelectChangeEvent,
  Accordion,
  AccordionDetails,
  AccordionSummary,
} from "@mui/material";

import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

import { useState, useEffect } from "react";
import UploadWidget from "./UploadWidget";
import dynamic from "next/dynamic";

const ResultMap = dynamic(() => import("./ResultMap"), {
  ssr: false,
});

export default function ContextValidation({
  coords,
  radius,
  model,
  setModel,
  uploadedFiles,
}: {
  coords: [number, number];
  radius: number;
  model: {};
  setModel: (model: {}) => void;
  uploadedFiles: string[] | null;
}) {
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
    fetch(apiUrl)
      .then((res) => {
        return res.json();
      })
      .then((data) => {
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
              {uploadedFiles.map((file_name, desc) => (
                <Accordion key={file_name}>
                  <AccordionSummary
                    expandIcon={<ArrowDropDownIcon />}
                    aria-controls="panel1-content"
                    id={file_name}
                  >
                    <Typography component="span">{file_name}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography>{desc}</Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
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
          <FormControl fullWidth>
            <InputLabel id="demo-simple-select-label">Radius</InputLabel>
            <Select
              labelId="select-label"
              id="radius-select"
              value={radius}
              label="Location Area"
              // onChange={handleRadiusChange}
            >
              <MenuItem value={5000}>5km</MenuItem>
              <MenuItem value={10000}>10km</MenuItem>
              <MenuItem value={20000}>20km</MenuItem>
            </Select>
          </FormControl>

          <ResultMap coords={coords} radius={radius} />
          <Typography>Searching for results in:</Typography>
          <Typography>{areaDescription.county}</Typography>
          {areaDescription.locality ? (
            <Typography>{areaDescription.locality}</Typography>
          ) : (
            <Typography>{areaDescription.county}</Typography>
          )}
          <Typography>{areaDescription.fullAddress}</Typography>
        </Box>
      </Grid>
    </Grid>
  );
}

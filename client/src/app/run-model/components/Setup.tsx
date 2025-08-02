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
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Button,
  SelectChangeEvent,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { useState, useEffect } from "react";
import UploadWidget from "./UploadWidget";
import dynamic from "next/dynamic";
import axios from "axios";

import { UploadedFile } from "@/types/UploadedFile";

const GeoMap = dynamic(() => import("../../../components/GeoMap"), {
  ssr: false,
});

export default function Setup({
  coords,
  setCoords,
  radius,
  setRadius,
  uploadedFiles,
  setUploadedFiles,
}: {
  coords: [number, number] | null;
  setCoords: (coords: [number, number]) => void;
  radius: number;
  setRadius: (radius: number) => void;
  uploadedFiles: UploadedFile[] | null;
  setUploadedFiles: (uploadedFiles: UploadedFile[]) => void;
}) {
  const [capacity, setCapacity] = useState<string>("");
  const [widget, setWidget] = useState(false);

  const handleWidgetOpen = () => {
    setWidget(true);
  };

  const handleWidgetClose = () => {
    setWidget(false);
  };

  const handleRadiusChange = (event: SelectChangeEvent<number>) => {
    setRadius(event.target.value);
  };

  useEffect(() => {
    const client = localStorage.getItem("clientId");
    axios
      .get(`http://localhost:8080/api/clients/${client}/files`)
      .then((res) => setUploadedFiles(res.data));
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

          {/* Capacity Selector */}
          <FormControl fullWidth margin="normal">
            <InputLabel id="capacity-label">Expected Capacity (MW)</InputLabel>
            <Select
              labelId="capacity-label"
              value={capacity}
              label="Expected Capacity (MW)"
              onChange={(e) => setCapacity(e.target.value)}
            >
              <MenuItem value="small">5</MenuItem>
              <MenuItem value="medium">10</MenuItem>
              <MenuItem value="large">20</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel id="capacity-label">Expected Capacity (MW)</InputLabel>
            <Select
              labelId="capacity-label"
              value={capacity}
              label="Expected Capacity (MW)"
              onChange={(e) => setCapacity(e.target.value)}
            >
              <MenuItem value="small">5</MenuItem>
              <MenuItem value="medium">10</MenuItem>
              <MenuItem value="large">20</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel id="capacity-label">Expected Capacity (MW)</InputLabel>
            <Select
              labelId="capacity-label"
              value={capacity}
              label="Expected Capacity (MW)"
              onChange={(e) => setCapacity(e.target.value)}
            >
              <MenuItem value="small">5</MenuItem>
              <MenuItem value="medium">10</MenuItem>
              <MenuItem value="large">20</MenuItem>
            </Select>
          </FormControl>

          {/* Uploaded Files List */}
          <Box mt={3}>
            <Typography variant="subtitle1" gutterBottom>
              Uploaded Files
            </Typography>
            {uploadedFiles ? (
              <Box sx={{ maxHeight: 200, overflow: "auto" }}>
                <List dense>
                  {uploadedFiles.map((file, index) => (
                    <Accordion key={index}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>
                          {file.display_name || file.file_name}
                        </Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          <strong>Description:</strong>{" "}
                          {file.description || "No description provided"}
                        </Typography>
                        <Typography variant="body2">
                          <strong>Tags:</strong>{" "}
                          {file.tags?.length ? file.tags.join(", ") : "No tags"}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </List>
              </Box>
            ) : (
              <Typography>No files uploaded.</Typography>
            )}
          </Box>

          {/* Upload Button */}
          <Box mt={2}>
            <Button variant="outlined" onClick={handleWidgetOpen}>
              Upload Files
            </Button>
          </Box>
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
              onChange={handleRadiusChange}
            >
              <MenuItem value={5000}>5km</MenuItem>
              <MenuItem value={10000}>10km</MenuItem>
              <MenuItem value={20000}>20km</MenuItem>
            </Select>
          </FormControl>

          <GeoMap
            coords={coords}
            onLocationSelected={setCoords}
            radius={radius}
          />
        </Box>
      </Grid>

      <UploadWidget
        open={widget}
        handleClose={() => setWidget(false)}
        setUploadedFiles={setUploadedFiles}
        uploadedFiles={uploadedFiles}
      />
    </Grid>
  );
}

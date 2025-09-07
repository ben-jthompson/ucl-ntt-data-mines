"use client";

import {
  Grid,
  Box,
  Typography,
  TextField,
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
import { isInsideBound } from "@/utilities/IsInsideBound";
import { FeatureCollection } from "geojson";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
const GeoMap = dynamic(() => import("../../../components/GeoMap"), {
  ssr: false,
});

type Address = {
  postalcode?: string;
  city?: string;
  county?: string;
  street?: string;
  number?: number;
};

export default function Setup({
  loading,
  setLoading,
  coords,
  setCoords,
  radius,
  setRadius,
  uploadedFiles,
  setUploadedFiles,
}: {
  loading: boolean;
  setLoading: (loading: boolean) => void;
  coords: [number, number] | null;
  setCoords: (coords: [number, number]) => void;
  radius: number;
  setRadius: (radius: number) => void;
  uploadedFiles: UploadedFile[] | null;
  setUploadedFiles: (uploadedFiles: UploadedFile[]) => void;
}) {
  const [widget, setWidget] = useState(false);
  const [address, setAddress] = useState<Address>({});
  const [UKBound, setUKBound] = useState<FeatureCollection | null>(null);
  const [mineExtent, setMineExtent] = useState<FeatureCollection | null>(null);

  const handleWidgetOpen = () => {
    setWidget(true);
  };

  const handleAddressLookup = () => {
    let query = "";

    if (address) {
      for (const [key, value] of Object.entries(address)) {
        if (value !== undefined && value !== null && value !== "") {
          query += `${encodeURIComponent(key)}=${encodeURIComponent(value)}&`;
        }
      }
      // remove trailing &
      if (query.endsWith("&")) {
        query = query.slice(0, -1);
      }
    }

    if (query.length > 0) {
      axios
        .get(`https://nominatim.openstreetmap.org/search?${query}&format=json`)
        .then((res) => {
          if (res.data) {
            console.log("Response:", res.data[0]);
            const boundingbox = res.data[0].boundingbox.map(Number);
            const geocodedCoords: [number, number] = [
              (boundingbox[0] + boundingbox[1]) / 2,
              (boundingbox[2] + boundingbox[3]) / 2,
            ];
            console.log("API Coords: ", geocodedCoords);
            if (
              isInsideBound({ coords: geocodedCoords, bound: mineExtent }) &&
              isInsideBound({ coords: geocodedCoords, bound: UKBound })
            ) {
              setCoords(geocodedCoords);
            } else {
              alert(
                "Response invalid or not in bounds of UK mines (coastal mines unsuitable)."
              );
            }
          } else {
            let backupQuery = "";
            for (const [, value] of Object.entries(address)) {
              if (value !== undefined && value !== null && value !== "") {
                backupQuery += `${encodeURIComponent(value)}, `;
              }
              if (backupQuery.endsWith(",+")) {
                backupQuery = backupQuery.slice(0, -2);
              }
              handleAddressBackup(backupQuery);
            }
          }
        });
    }
  };

  const handleAddressBackup = (query: string) => {
    axios
      .get(`https://nominatim.openstreetmap.org/search?q=${query}&format=json`)
      .then((res) => {
        if (res.data) {
          console.log("Response:", res.data[0]);
          const boundingbox = res.data[0].boundingbox.map(Number);
          const geocodedCoords: [number, number] = [
            (boundingbox[0] + boundingbox[1]) / 2,
            (boundingbox[2] + boundingbox[3]) / 2,
          ];
          console.log("API Coords: ", geocodedCoords);
          if (isInsideBound({ coords: geocodedCoords, bound: mineExtent })) {
            setCoords(geocodedCoords);
          } else {
            alert("Response invalid or not in bounds of UK mines.");
          }
        } else {
          alert("Invalid response retrieved. Please try another address.");
        }
      });
  };

  const handleRadiusChange = (event: SelectChangeEvent<number>) => {
    setRadius(event.target.value);
  };

  useEffect(() => {
    const client = localStorage.getItem("clientId");
    axios.get(`${backendUrl}/api/clients/${client}/files`).then((response) => {
      console.log("Response:", response.data);
      if (response.data.files && response.data.files.length) {
        setUploadedFiles(response.data.files);
      }
    });
    setLoading(false);
  }, [setUploadedFiles, setLoading]);

  useEffect(() => {
    axios
      .get(`${backendUrl}/api/geojson/coalfield-extent-4326.geojson`)
      .then((res) => {
        const geojson = res.data as FeatureCollection;
        setMineExtent(geojson);
      });
  }, []);

  useEffect(() => {
    axios.get("geojson/uk.geo.json").then((res) => setUKBound(res.data));
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

          {/* Address Selector */}
          <Box mt={3}>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Address Lookup</strong>
            </Typography>
            <TextField
              label="Number, Street (eg. 1 Oxford Street)"
              variant="outlined"
              fullWidth
              value={address.street || ""}
              onChange={(e) =>
                setAddress({ ...address, street: e.target.value })
              }
              sx={{ my: 1 }}
            />
            <TextField
              label="City (eg. Sheffield)"
              variant="outlined"
              fullWidth
              value={address.city || ""}
              onChange={(e) => setAddress({ ...address, city: e.target.value })}
              sx={{ my: 1 }}
            />
            <TextField
              label="County (eg. Lancashire)"
              variant="outlined"
              fullWidth
              value={address.county || ""}
              onChange={(e) =>
                setAddress({ ...address, county: e.target.value })
              }
              sx={{ my: 1 }}
            />
            <TextField
              label="Postcode (eg. M1 1AA)"
              variant="outlined"
              fullWidth
              value={address.postalcode || ""}
              onChange={(e) =>
                setAddress({ ...address, postalcode: e.target.value })
              }
              sx={{ my: 1 }}
            />
            <Button
              variant="contained"
              onClick={handleAddressLookup}
              sx={{ mt: 2 }}
            >
              Submit
            </Button>
          </Box>

          {/* Uploaded Files List */}
          <Box mt={3}>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Uploaded Files</strong>
            </Typography>
            {uploadedFiles ? (
              <Box
                sx={{
                  maxHeight: 200,
                  overflow: "auto",
                }}
              >
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
            ) : loading ? (
              <>
                <Typography>Searching for files...</Typography>
              </>
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

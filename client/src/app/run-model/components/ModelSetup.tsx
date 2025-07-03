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
} from "@mui/material";
import { useState } from "react";
import UploadWidget from "./UploadWidget";
import dynamic from "next/dynamic";

const GeoMap = dynamic(() => import("../../../components/GeoMap"), {
  ssr: false,
});

export default function ModelSetup() {
  const [capacity, setCapacity] = useState<string>("");
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([
    "geology_report.pdf",
    "cooling_study.docx",
  ]);
  const [widget, setWidget] = useState(false);
  const [coords, setCoords] = useState<[number, number] | null>(null);
  const [radius, setRadius] = useState(10000);

  const handleWidgetOpen = () => {
    setWidget(true);
  };

  const handleWidgetClose = () => {
    setWidget(false);
  };

  const handleRadiusChange = (event: SelectChangeEvent<number>) => {
    setRadius(event.target.value);
  };

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
          }}
        >
          <Typography variant="h6" gutterBottom>
            About me
          </Typography>

          {/* Capacity Selector */}
          <FormControl fullWidth margin="normal">
            <InputLabel id="capacity-label">Capacity</InputLabel>
            <Select
              labelId="capacity-label"
              value={capacity}
              label="Capacity"
              onChange={(e) => setCapacity(e.target.value)}
            >
              <MenuItem value="small">Small-scale</MenuItem>
              <MenuItem value="medium">Medium-scale</MenuItem>
              <MenuItem value="large">Large-scale</MenuItem>
            </Select>
          </FormControl>

          {/* Uploaded Files List */}
          <Box mt={3}>
            <Typography variant="subtitle1" gutterBottom>
              Uploaded Files
            </Typography>
            <List dense>
              {uploadedFiles.map((file, index) => (
                <ListItem key={index}>
                  <ListItemText primary={file} />
                </ListItem>
              ))}
            </List>
          </Box>

          {/* Upload Button */}
          <Box mt={2}>
            <Button variant="outlined" onClick={handleWidgetOpen}>
              Upload More Files
            </Button>
          </Box>
        </Box>
      </Grid>
      <Grid size={{ xs: 12, md: 6 }}>
        <FormControl>
          <InputLabel id="demo-simple-select-label">Radius</InputLabel>
          <Select
            labelId="demo-simple-select-label"
            id="demo-simple-select"
            value={radius}
            label="Location Area"
            onChange={handleRadiusChange}
          >
            <MenuItem value={5000}>5km</MenuItem>
            <MenuItem value={10000}>10km</MenuItem>
            <MenuItem value={20000}>20km</MenuItem>
          </Select>
        </FormControl>

        <GeoMap onLocationSelected={setCoords} radius={radius} />
        {coords && <Typography>{coords}</Typography>}
        <Typography>{radius}</Typography>
      </Grid>

      {/* open widget on button press */}
      {widget && <UploadWidget open={widget} handleClose={handleWidgetClose} />}
    </Grid>
  );
}

"use client";

import { Box, Grid, Button, Typography } from "@mui/material";
import { MapContainer, TileLayer, Marker, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { useState, useEffect } from "react";
import { ReportFile } from "@/types/ReportFile";
import { formatDate, viewReport, downloadReport } from "@/utilities/Utilities";
import DocumentViewer from "./DocumentViewer";

// Apply default marker
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

function LocationMarker({
  coords,
  radius,
  metadata,
  setViewerLink,
  setDialogOpen,
}: {
  coords: [number, number] | null;
  radius: number;
  metadata?: ReportFile;
  setViewerLink?: (link: string) => void;
  setDialogOpen?: (open: boolean) => void;
}) {
  const clientId = localStorage.getItem("clientId");
  console.log("INFO", metadata, clientId, setDialogOpen, setViewerLink);
  return coords ? (
    <>
      <Marker position={coords}>
        {metadata && clientId && setDialogOpen && setViewerLink ? (
          <Popup>
            <Typography variant="h6">{metadata.display_name}</Typography>
            <Typography>
              Uploaded on: {formatDate(metadata.upload_date)}
            </Typography>
            <Button
              size="small"
              variant="outlined"
              sx={{ mr: 1 }}
              onClick={() =>
                viewReport(
                  clientId,
                  metadata.file_name,
                  setDialogOpen,
                  setViewerLink
                )
              }
            >
              View
            </Button>
            <Button
              size="small"
              variant="contained"
              onClick={() => downloadReport(clientId, metadata.file_name)}
            >
              Download
            </Button>
          </Popup>
        ) : (
          <Popup>
            lat: {Math.round(coords[0] * 10000) / 10000}; lng:{" "}
            {Math.round(coords[1] * 10000) / 10000}{" "}
          </Popup>
        )}
      </Marker>
      <Circle center={coords} radius={radius} />
    </>
  ) : null;
}

export default function ResultMap({
  coords,
  radius,
  reports,
  result,
}: {
  coords: [number, number] | null;
  radius: number;
  reports?: ReportFile[];
  result?: ReportFile;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewerLink, setViewerLink] = useState<string | null>(null);
  const [centre, setCentre] = useState<{ lat: number; lng: number } | null>(
    null
  );

  const zoomScale: { [key: number]: number } = {
    5000: 12,
    10000: 11,
    20000: 10,
  };

  const zoom = result ? (zoomScale[radius] ?? 7) - 1 : zoomScale[radius] ?? 6;

  const hasOneResult = reports ? reports.length === 1 : false;
  useEffect(() => {
    if (result) {
      setCentre({ lat: result["coords"][0], lng: result["coords"][1] });
    } else if (hasOneResult && reports) {
      setCentre({ lat: reports[0]["coords"][0], lng: reports[0]["coords"][1] });
    } else {
      setCentre({ lat: 53.505, lng: -0.09 });
    }
  }, [result, hasOneResult, reports]);
  return coords ? (
    <Box
      sx={{
        height: "400px",
        borderRadius: 2,
        overflow: "hidden",
        mt: 3,
        textAlign: "center",
      }}
    >
      <MapContainer
        center={{ lat: coords[0], lng: coords[1] }}
        zoom={zoom}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <LocationMarker coords={coords} radius={radius} />
      </MapContainer>
    </Box>
  ) : (
    <Grid size={{ xs: 12 }}>
      <Box
        sx={{
          height: "400px",
          borderRadius: 2,
          overflow: "hidden",
          mt: 3,
          textAlign: "center",
        }}
      >
        {centre && (
          <MapContainer
            center={centre}
            zoom={zoom}
            style={{ height: "100%", width: "100%" }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; OpenStreetMap contributors"
            />
            {reports &&
              reports.map((report, idx) => (
                <LocationMarker
                  key={`report-${idx}`}
                  coords={report.coords}
                  radius={1000}
                  metadata={report}
                  setDialogOpen={setDialogOpen}
                  setViewerLink={setViewerLink}
                />
              ))}

            {result && (
              <LocationMarker
                coords={result.coords}
                radius={1000}
                metadata={result}
                setDialogOpen={setDialogOpen}
                setViewerLink={setViewerLink}
              />
            )}
          </MapContainer>
        )}
      </Box>
      {dialogOpen && viewerLink && (
        <DocumentViewer
          pdf={viewerLink}
          dialogOpen={dialogOpen}
          onDialogClosed={setDialogOpen}
        />
      )}
    </Grid>
  );
}

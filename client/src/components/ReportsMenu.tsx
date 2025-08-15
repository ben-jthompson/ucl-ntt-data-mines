"use client";

import {
  Box,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";
import axios from "axios";
import { useState } from "react";
import { ReportFile } from "@/types/ReportFile";
import DocumentViewer from "./DocumentViewer";

interface ReportsMenuProps {
  reports: ReportFile[];
  clientId: string;
}

export default function ReportsMenu({ reports, clientId }: ReportsMenuProps) {
  const [viewerLink, setViewerLink] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const downloadReport = async (fileName: string) => {
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

  const viewReport = async (fileName: string) => {
    try {
      const response = await axios.get(
        `http://localhost:8080/api/reports/${clientId}/files/${fileName}`,
        { responseType: "blob" } // still need blob
      );

      const pdfLink = URL.createObjectURL(response.data);

      setViewerLink(pdfLink);
      setDialogOpen(true);
    } catch (error) {
      console.error("Failed to view report", error);
    }
  };

  return (
    <Box sx={{ p: 3, width: "100%", textAlign: "left" }}>
      <Typography variant="h6" gutterBottom>
        My Reports
      </Typography>
      <List>
        {reports.map((report, idx) => (
          <Box key={idx}>
            <ListItem
              secondaryAction={
                <Box>
                  <Button
                    size="small"
                    variant="outlined"
                    sx={{ mr: 1 }}
                    onClick={() => viewReport(report.file_name)}
                  >
                    View
                  </Button>
                  <Button
                    size="small"
                    variant="contained"
                    onClick={() => downloadReport(report.file_name)}
                  >
                    Download
                  </Button>
                </Box>
              }
            >
              <ListItemText
                primary={report.display_name}
                secondary={`Uploaded: ${new Date(
                  report.upload_date
                ).toLocaleString()}`}
              />
            </ListItem>
            {idx < reports.length - 1 && <Divider />}
          </Box>
        ))}
      </List>
      {dialogOpen && viewerLink && (
        <DocumentViewer
          pdf={viewerLink}
          dialogOpen={dialogOpen}
          onDialogClosed={setDialogOpen}
        />
      )}
    </Box>
  );
}

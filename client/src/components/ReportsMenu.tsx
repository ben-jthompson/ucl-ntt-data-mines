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
import { viewReport, downloadReport } from "@/utilities/Utilities";

interface ReportsMenuProps {
  reports: ReportFile[];
  clientId: string;
}

export default function ReportsMenu({ reports, clientId }: ReportsMenuProps) {
  const [viewerLink, setViewerLink] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <Box sx={{ p: 3, width: "100%", textAlign: "left"}}>
      <Typography variant="h6" gutterBottom>
        My Reports
      </Typography>
      <Box sx={{ p: 3, width: "100%", textAlign: "left", 
      maxHeight: 400,
      overflow: "auto" }}>
      <List>
        {[...reports]
          .sort(
            (a, b) =>
              new Date(b.upload_date).getTime() -
              new Date(a.upload_date).getTime()
          )
          .map((report, idx) => (
            <Box key={idx}>
              <ListItem
                secondaryAction={
                  <Box>
                    <Button
                      size="small"
                      variant="outlined"
                      sx={{ mr: 1 }}
                      onClick={() =>
                        viewReport(
                          clientId,
                          report.file_name,
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
                      onClick={() => downloadReport(clientId, report.file_name)}
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
    </Box>
  );
}

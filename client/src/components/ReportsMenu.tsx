"use client";

import {
  Box,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import Delete from "@mui/icons-material/Delete";
import axios from "axios";
import { useState } from "react";
import { ReportFile } from "@/types/ReportFile";
import DocumentViewer from "./DocumentViewer";
import {
  viewReport,
  downloadReport,
  deleteReport,
} from "@/utilities/Utilities";

interface ReportsMenuProps {
  reports: ReportFile[];
  clientId: string;
  setReports: (reports: ReportFile[]) => void;
}

export default function ReportsMenu({
  reports,
  clientId,
  setReports,
}: ReportsMenuProps) {
  const [viewerLink, setViewerLink] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<ReportFile | null>(null);

  const handleCloseDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setReportToDelete(null);
  };

  const handleConfirmDelete = () => {
    if (reportToDelete) {
      deleteReport(clientId, reportToDelete.file_name);
      setDeleteDialogOpen(false);
      setReportToDelete(null);
      setReports(
        reports.filter(
          (report) => report.file_name !== reportToDelete.file_name
        )
      );
    }
  };

  const handleOpenDeleteDialog = (report: ReportFile) => {
    setDeleteDialogOpen(true);
    setReportToDelete(report);
  };

  return (
    <Box sx={{ p: 3, width: "100%", textAlign: "left" }}>
      <Typography variant="h6" gutterBottom>
        My Reports
      </Typography>
      <Box
        sx={{
          p: 3,
          width: "100%",
          textAlign: "left",
          maxHeight: 400,
          overflow: "auto",
        }}
      >
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
                        onClick={() =>
                          downloadReport(clientId, report.file_name)
                        }
                      >
                        Download
                      </Button>

                      <IconButton
                        edge="end"
                        onClick={() => handleOpenDeleteDialog(report)}
                      >
                        <Delete />
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemText
                    primary={
                      report.display_name.slice(0, 20) +
                      (report.display_name.length > 20 ? "..." : "")
                    }
                    secondary={`Uploaded: ${new Date(
                      report.upload_date
                    ).toLocaleString()}`}
                  />
                </ListItem>
                {idx < reports.length - 1 && <Divider />}
              </Box>
            ))}
        </List>
        {reportToDelete && (
          <Dialog open={deleteDialogOpen} onClose={handleCloseDeleteDialog}>
            <DialogTitle>Remove Report</DialogTitle>
            <DialogContent>
              <DialogContentText>
                Are you sure you want to remove{" "}
                <b>{reportToDelete.display_name}</b>?
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDeleteDialog} color="primary">
                No
              </Button>
              <Button onClick={handleConfirmDelete} color="error" autoFocus>
                Yes
              </Button>
            </DialogActions>
          </Dialog>
        )}
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

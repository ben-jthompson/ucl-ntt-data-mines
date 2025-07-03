import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Input,
} from "@mui/material";

type UploadWidgetProps = {
  open: boolean;
  handleClose: () => void;
  onFilesUploaded: (files: string[]) => void;
  existingFiles: string[];
};

export default function UploadWidget({
  open,
  handleClose,
  onFilesUploaded,
  existingFiles,
}: UploadWidgetProps) {
  const [localFiles, setLocalFiles] = useState<string[]>(existingFiles);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const newFiles = Array.from(files).map((file) => file.name);
    const updated = [...localFiles, ...newFiles];
    setLocalFiles(updated);
    onFilesUploaded(updated);
  };

  const handleFileRemove = (fileName: string) => {
    const updated = localFiles.filter((file) => file !== fileName);
    setLocalFiles(updated);
    onFilesUploaded(updated);
  };

  const handleDialogClose = () => {
    handleClose();
  };

  return (
    <Dialog open={open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Files</DialogTitle>
      <DialogContent>
        <Box>
          <Button variant="contained" component="label">
            Choose Files
            <Input
              type="file"
              onChange={handleFileChange}
              sx={{ display: "none" }}
            />
          </Button>
        </Box>

        <Box mt={3}>
          <Typography variant="subtitle1" gutterBottom>
            Uploaded Files
          </Typography>
          {localFiles.length > 0 ? (
            <List dense>
              {localFiles.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => handleFileRemove(file)}
                    >
                      Delete
                    </IconButton>
                  }
                >
                  <ListItemText primary={file} />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body2">No files uploaded yet.</Typography>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleDialogClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
}

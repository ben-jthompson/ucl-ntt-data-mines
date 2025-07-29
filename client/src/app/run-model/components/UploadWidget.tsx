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
  TextField,
} from "@mui/material";
import Delete from "@mui/icons-material/Delete";

import axios from "axios";
import { UploadedFile } from "@/types/UploadedFile";

type UploadWidgetProps = {
  open: boolean;
  handleClose: () => void;
  onFilesUploaded: (files: UploadedFile[]) => void;
  existingFiles: UploadedFile[];
};

export default function UploadWidget({
  open,
  handleClose,
  onFilesUploaded,
  existingFiles,
}: UploadWidgetProps) {
  const [localFiles, setLocalFiles] = useState<UploadedFile[]>(existingFiles);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileToDelete, setFileToDelete] = useState<File | null>(null);
  const [description, setDescription] = useState("");

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    axios
      .post("http://localhost:8080/api/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        console.log("Upload successful:", response.data);
        const updated = [
          ...localFiles,
          {
            file_name: selectedFile.name,
            description: description,
            id: 3,
          },
        ];
        setLocalFiles(updated);
        onFilesUploaded(updated);
        setSelectedFile(null);
        setDescription("");
      })
      .catch((error) => {
        console.error("Upload error:", error);
      });
  };

  const handleFileRemove = (filename: string) => {
    axios
      .post("http://localhost:8080/api/delete", { file: filename })
      .then((response) => {
        console.log("Upload successful:", response.data);
        const updated = localFiles.filter((doc) => doc.file_name !== filename);
        setLocalFiles(updated);
        onFilesUploaded(updated);
      });
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
              onChange={handleFileSelect}
              accept=".doc,.docx,.xml,.shp,.pdf"
              sx={{ display: "none" }}
            />
          </Button>

          {selectedFile && (
            <>
              <Typography variant="body1">
                Selected file: <strong>{selectedFile.name}</strong>
              </Typography>
              <TextField
                label="File Description"
                variant="outlined"
                fullWidth
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </>
          )}
          <Button
            variant="contained"
            component="label"
            onClick={handleFileUpload}
          >
            Submit
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
                      onClick={() => handleFileRemove(file.file_name)}
                    >
                      <Delete />
                    </IconButton>
                  }
                >
                  <ListItemText primary={file.file_name} />
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

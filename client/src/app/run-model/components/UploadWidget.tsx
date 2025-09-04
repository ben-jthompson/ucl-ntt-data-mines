import React, { useState, useRef } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Checkbox,
  List,
  ListItem,
  IconButton,
  Input,
  TextField,
  OutlinedInput,
  InputLabel,
  MenuItem,
  FormControl,
  FormHelperText,
  ListItemText,
  Select,
  SelectChangeEvent,
} from "@mui/material";
import Delete from "@mui/icons-material/Delete";
import { v4 as uuidv4 } from "uuid";

import axios from "axios";
import { UploadedFile } from "@/types/UploadedFile";

type UploadWidgetProps = {
  open: boolean;
  handleClose: () => void;
  setUploadedFiles: (files: UploadedFile[]) => void;
  uploadedFiles: UploadedFile[] | null;
};

export default function UploadWidget({
  open,
  handleClose,
  setUploadedFiles,
  uploadedFiles,
}: UploadWidgetProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [description, setDescription] = useState("");
  const [tags, setTags] = useState<string[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const availableTags = [
    "Mine History",
    "Labour Availability",
    "Energy Availability",
    "Local Authorities",
    "Existing Mine Regeneration Projects",
    "Transport Availability",
  ];
  const ITEM_HEIGHT = 48;
  const ITEM_PADDING_TOP = 8;
  const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log("File selected");
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setDescription("");
      setTags(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleTagChange = (event: SelectChangeEvent<string[]>) => {
    const {
      target: { value },
    } = event;

    setTags(typeof value === "string" ? value.split(",") : value);
  };

  const handleFileUpload = (event: React.MouseEvent) => {
    if (!selectedFile) return;
    const selectedFileId = uuidv4();
    const formData = new FormData();
    const client = localStorage.getItem("clientId") ?? "unknown";
    formData.append("file", selectedFile);
    formData.append("id", selectedFileId);
    formData.append("description", description ?? "");
    formData.append("tags", tags ? tags.join(", ") : "");

    axios
      .post(`http://localhost:8080/api/clients/${client}/files`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        console.log("Upload successful:", response.data);
        // TODO add id assignment
        if (uploadedFiles) {
          setUploadedFiles([
            ...uploadedFiles,
            {
              file_name: response.data.filename,
              display_name: selectedFile.name,
              description: description,
              id: selectedFileId,
              tags: tags ?? undefined,
            },
          ]);
        } else {
          setUploadedFiles([
            {
              file_name: response.data.filename,
              display_name: selectedFile.name,
              description: description,
              id: selectedFileId,
              tags: tags ?? undefined,
            },
          ]);
        }
        setSelectedFile(null);
        setDescription("");
        setTags(null);
      })
      .catch((error) => {
        if (error.response) {
          if (error.response.data.error === "Invalid file type") {
            alert("Please select a valid file (file type not supported).");
          } else if (error.response.status === 409) {
            alert(
              "File under the same name has already been uploaded. Please rename or select another file."
            );
          } else if (error.response.status === 413) {
            alert(
              "File must not be more than 10MB. Please select another file."
            );
          }
        } else {
          console.error("Upload error:", error);
        }
      });
  };

  const handleFileRemove = (file: UploadedFile) => {
    const client = localStorage.getItem("clientId") ?? "unknown";
    axios
      .delete(`http://localhost:8080/api/clients/${client}/files/${file.id}`, {
        data: {
          file: file.file_name,
        },
      })
      .then((response) => {
        if (uploadedFiles) {
          setUploadedFiles(
            uploadedFiles.filter(
              (doc) => doc.id.trim() !== response.data.id.trim()
            )
          );
        }
      })
      .catch((error) => {
        if (error.response) {
          if (error.response.status === 500) {
            alert("Failed to delete file: " + error.response.data.error);
          }
        } else {
          alert("Delete failed: Network or server error");
        }
      });
  };
  const handleDialogClose = () => {
    setSelectedFile(null);
    setDescription("");
    setTags(null);
    handleClose();
  };

  return (
    <Dialog open={open} onClose={handleDialogClose} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Files</DialogTitle>
      <DialogContent>
        <Box>
          <Button variant="contained" component="label">
            Choose Files
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".docx, .doc, .xls, .xlsx, .json, .geojson, .geo.json, .pdf"
              style={{ display: "none" }}
              ref={fileInputRef}
            />
          </Button>
          <Typography variant="body2" color="secondary">
            Supported inputs: .pdf, .docx, .doc, .xlsx, .xls, .csv, .json,
            .geojson
          </Typography>
          {selectedFile && (
            <>
              <Typography variant="body1">
                Selected file: <strong>{selectedFile?.name}</strong>
              </Typography>

              <TextField
                label="File Description"
                variant="outlined"
                fullWidth
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                sx={{ my: 2 }}
              />

              <FormControl sx={{ m: 1, width: 300 }}>
                <InputLabel id="tag-select-label">Tag</InputLabel>
                <Select
                  labelId="tag-select-label"
                  id="tag-select"
                  multiple
                  value={tags ?? []}
                  onChange={handleTagChange}
                  input={<OutlinedInput label="Tag" />}
                  renderValue={(selected) => selected.join(", ")}
                  MenuProps={MenuProps}
                >
                  {availableTags.map((availableTag) => (
                    <MenuItem key={availableTag} value={availableTag}>
                      <Checkbox
                        checked={tags ? tags.includes(availableTag) : false}
                      />
                      <ListItemText primary={availableTag} />
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>Select any that apply</FormHelperText>
              </FormControl>

              <Button
                variant="contained"
                onClick={handleFileUpload}
                sx={{ mt: 2 }}
              >
                Submit
              </Button>
            </>
          )}
        </Box>

        <Box mt={3}>
          <Typography variant="subtitle1" gutterBottom>
            Uploaded Files
          </Typography>
          {uploadedFiles ? (
            <List dense>
              {uploadedFiles.map((file, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => handleFileRemove(file)}
                    >
                      <Delete />
                    </IconButton>
                  }
                >
                  <ListItemText primary={file.display_name} />
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

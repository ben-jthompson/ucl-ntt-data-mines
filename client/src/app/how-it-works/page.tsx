import {
  Box,
  Container,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
} from "@mui/material";

export default function HowItWorks() {
  return (
    <Container maxWidth="md" sx={{ py: 6 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Typography variant="h4" gutterBottom align="center">
          How to Use This Application
        </Typography>

        <Typography variant="body1" paragraph align="center">
          Follow these simple steps to generate reports and explore your
          results.
        </Typography>

        <Divider sx={{ my: 3 }} />

        <List>
          <ListItem>
            <ListItemText
              primary="1. Configure Settings"
              secondary="Choose your preferred coordinates and radius values. You can click on the map to select a location, or input an address."
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="2. Upload Your Data"
              secondary="Upload relevant files into to tailor the analysis to your goals. Make sure to tag your documents with the relevant topic."
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="3. Run the Analysis"
              secondary="The application will process your data and display your results on the interactive map."
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="4. Explore Results"
              secondary="Click on the marker to view your report in the application, and use the side panel for additional functionality, such as downloading accompanying figures and documents."
            />
          </ListItem>

          <ListItem>
            <ListItemText
              primary="5. View All Your Reports"
              secondary="Navigate to the Reports page to see, download or delete your historical reports."
            />
          </ListItem>
        </List>
      </Paper>
    </Container>
  );
}

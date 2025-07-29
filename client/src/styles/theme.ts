// theme.ts
import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#2e7d32", // Forest green
      contrastText: "#ffffff",
    },
    secondary: {
      main: "#81c784", // Light green
    },
    background: {
      default: "#f1f8e9", // Light green-tinted background
      paper: "#ffffff",
    },
    text: {
      primary: "#1b5e20", // Darker forest green
      secondary: "#4e342e", // Earthy brown
    },
  },
  typography: {
    fontFamily: "Roboto, Arial, sans-serif",
    button: {
      textTransform: "none",
      fontWeight: 500,
    },
    h6: {
      fontWeight: 700,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: "8px",
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "#1b5e20", // deep green
        },
      },
    },
  },
});

export default theme;

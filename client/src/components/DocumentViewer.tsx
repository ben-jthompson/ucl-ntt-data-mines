import { Worker, Viewer } from "@react-pdf-viewer/core";
import "@react-pdf-viewer/core/lib/styles/index.css";
import pdfjsWorker from "pdfjs-dist/build/pdf.worker.entry";
import { defaultLayoutPlugin } from "@react-pdf-viewer/default-layout";
import "@react-pdf-viewer/core/lib/styles/index.css";
import "@react-pdf-viewer/default-layout/lib/styles/index.css";
import { Dialog, IconButton } from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

export default function DocumentViewer({
  pdf,
  dialogOpen,
  onDialogClosed,
}: {
  pdf: string;
  dialogOpen: boolean;
  onDialogClosed: (dialogOpen: boolean) => void;
}) {
  const workerUrl = `https://unpkg.com/pdfjs-dist@${pdfjsWorker}/build/pdf.worker.min.js`;
  const plugin = defaultLayoutPlugin();
  return (
    <Dialog
      open={dialogOpen}
      onClose={() => onDialogClosed(false)}
      maxWidth="lg"
      fullWidth
    >
      <IconButton
        onClick={() => onDialogClosed(false)}
        style={{ position: "absolute", right: 8, top: 8, zIndex: 10 }}
      >
        <CloseIcon />
      </IconButton>

      <div style={{ height: "80vh" }}>
        <Worker workerUrl={workerUrl}>
          <Viewer fileUrl={pdf} defaultScale={1.0} plugins={[plugin]} />
        </Worker>
      </div>
    </Dialog>
  );
}

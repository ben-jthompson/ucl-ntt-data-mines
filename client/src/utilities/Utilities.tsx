import axios from "axios";

const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

export function formatDate(dateStr: string) {
  const dateObj = new Date(dateStr);
  const formattedDate = dateObj.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
  return formattedDate;
}

export const downloadReport = async (clientId: string, fileName: string) => {
  try {
    const response = await axios.get(
      `${backendUrl}/api/reports/${clientId}/files/${fileName}`,
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

export const viewReport = async (
  clientId: string,
  fileName: string,
  setDialogOpen: (open: boolean) => void,
  setViewerLink: (link: string) => void
) => {
  try {
    const response = await axios.get(
      `${backendUrl}/api/reports/${clientId}/files/${fileName}`,
      { responseType: "blob" }
    );

    const pdfLink = URL.createObjectURL(response.data);

    setViewerLink(pdfLink);
    setDialogOpen(true);
  } catch (error) {
    console.error("Failed to view report", error);
  }
};

export const deleteReport = async (clientId: string, fileName: string) => {
  try {
    const response = await axios.delete(
      `${backendUrl}/api/reports/${clientId}/files/${fileName}`
    );
    return response.data;
  } catch (error) {
    console.error("Failed to delete report", error);
  }
};

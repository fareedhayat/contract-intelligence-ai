import { useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Title2,
  Text,
  Button,
  Card,
  makeStyles,
  tokens,
  Spinner,
  MessageBar,
  MessageBarBody,
} from "@fluentui/react-components";
import { ArrowUploadRegular, DocumentRegular } from "@fluentui/react-icons";
import { uploadContract, triggerAnalysis } from "../services/api";

const useStyles = makeStyles({
  dropZone: {
    marginTop: "24px",
    border: `2px dashed ${tokens.colorNeutralStroke2}`,
    borderRadius: tokens.borderRadiusLarge,
    padding: "48px",
    textAlign: "center",
    cursor: "pointer",
    transition: "all 0.2s",
    "&:hover": {
      borderColor: tokens.colorBrandStroke1,
      backgroundColor: tokens.colorNeutralBackground2,
    },
  },
  dropZoneActive: {
    borderColor: tokens.colorBrandStroke1,
    backgroundColor: tokens.colorBrandBackground2,
  },
  fileInfo: {
    marginTop: "24px",
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "16px",
  },
  actions: {
    marginTop: "16px",
    display: "flex",
    gap: "12px",
  },
});

function Upload() {
  const styles = useStyles();
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<{ contractId: string; filename: string } | null>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    setError(null);
    setSuccess(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      const result = await uploadContract(file);
      await triggerAnalysis(result.contract_id);
      setSuccess({ contractId: result.contract_id, filename: result.filename });
      setFile(null);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <Title2>Upload Contract</Title2>
      <Text style={{ display: "block", marginTop: 8, color: tokens.colorNeutralForeground3 }}>
        Upload a contract document to analyze. Supported formats: PDF, Word, TXT.
      </Text>

      {error && (
        <MessageBar intent="error" style={{ marginTop: 16 }}>
          <MessageBarBody>{error}</MessageBarBody>
        </MessageBar>
      )}

      {success && (
        <MessageBar intent="success" style={{ marginTop: 16 }}>
          <MessageBarBody>
            "{success.filename}" uploaded and analysis started.{" "}
            <Button
              appearance="transparent"
              size="small"
              onClick={() => navigate(`/contracts/${success.contractId}`)}
            >
              View details
            </Button>
          </MessageBarBody>
        </MessageBar>
      )}

      <div
        className={`${styles.dropZone} ${dragOver ? styles.dropZoneActive : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => {
          const input = document.createElement("input");
          input.type = "file";
          input.accept = ".pdf,.doc,.docx,.txt";
          input.onchange = (e) => {
            const f = (e.target as HTMLInputElement).files?.[0];
            if (f) handleFile(f);
          };
          input.click();
        }}
      >
        <ArrowUploadRegular fontSize={48} />
        <Text size={400} weight="semibold" style={{ display: "block", marginTop: 12 }}>
          Drag and drop a contract file here
        </Text>
        <Text size={300} style={{ display: "block", marginTop: 4, color: tokens.colorNeutralForeground3 }}>
          or click to browse
        </Text>
      </div>

      {file && (
        <>
          <Card className={styles.fileInfo}>
            <DocumentRegular fontSize={24} />
            <div>
              <Text weight="semibold">{file.name}</Text>
              <Text size={200} style={{ display: "block", color: tokens.colorNeutralForeground3 }}>
                {(file.size / 1024).toFixed(1)} KB
              </Text>
            </div>
          </Card>
          <div className={styles.actions}>
            <Button appearance="primary" onClick={handleUpload} disabled={uploading}>
              {uploading ? <Spinner size="tiny" /> : "Upload & Analyze"}
            </Button>
            <Button appearance="secondary" onClick={() => setFile(null)} disabled={uploading}>
              Clear
            </Button>
          </div>
        </>
      )}
    </div>
  );
}

export default Upload;

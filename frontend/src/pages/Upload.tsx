import { Title2, Text } from "@fluentui/react-components";

function Upload() {
  return (
    <div>
      <Title2>Upload Contract</Title2>
      <Text style={{ display: "block", marginTop: 12 }}>
        Drag and drop or select a contract file to upload and analyze.
      </Text>
    </div>
  );
}

export default Upload;

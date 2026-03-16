import { useParams } from "react-router-dom";
import { Title2, Text } from "@fluentui/react-components";

function ContractDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <Title2>Contract Detail</Title2>
      <Text style={{ display: "block", marginTop: 12 }}>
        Analysis results for contract {id} will appear here.
      </Text>
    </div>
  );
}

export default ContractDetail;

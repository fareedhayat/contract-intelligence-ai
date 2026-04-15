import { useState } from "react";
import {
  Title2,
  Title3,
  Text,
  Card,
  Button,
  Dropdown,
  Option,
  Spinner,
  Badge,
  makeStyles,
  tokens,
  MessageBar,
  MessageBarBody,
} from "@fluentui/react-components";
import { compareContracts } from "../services/api";
import { useData } from "../components/DataProvider";
import type { ComparisonResult } from "../types";

const useStyles = makeStyles({
  selector: {
    display: "flex",
    gap: "16px",
    alignItems: "flex-end",
    marginTop: "20px",
    flexWrap: "wrap",
  },
  dropdownWrapper: {
    display: "flex",
    flexDirection: "column",
    gap: "4px",
    minWidth: "250px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    marginTop: "16px",
    "& th, & td": {
      padding: "12px 16px",
      textAlign: "left",
      borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    },
    "& th": {
      backgroundColor: tokens.colorNeutralBackground3,
      fontWeight: "600",
    },
  },
  assessment: {
    marginTop: "24px",
    padding: "20px",
  },
});

function Compare() {
  const styles = useStyles();
  const { contracts, loading: loadingContracts } = useData();
  const analyzedContracts = contracts.filter((c) => c.status === "completed");
  const [contractA, setContractA] = useState<string>("");
  const [contractB, setContractB] = useState<string>("");
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!contractA || !contractB) return;
    setLoading(true);
    setError(null);
    setComparison(null);

    try {
      const result = await compareContracts(contractA, contractB);
      setComparison(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Comparison failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const advantageColor = (a: string) =>
    a === "contract_a" ? "success" : a === "contract_b" ? "danger" : "informative";

  return (
    <div>
      <Title2>Compare Contracts</Title2>
      <Text style={{ display: "block", marginTop: 8, color: tokens.colorNeutralForeground3 }}>
        Select two analyzed contracts to compare side by side.
      </Text>

      {loadingContracts ? (
        <Spinner label="Loading contracts..." />
      ) : analyzedContracts.length < 2 ? (
        <MessageBar intent="warning" style={{ marginTop: 16 }}>
          <MessageBarBody>
            You need at least two analyzed contracts to compare. Upload and analyze contracts first.
          </MessageBarBody>
        </MessageBar>
      ) : (
        <>
          <div className={styles.selector}>
            <div className={styles.dropdownWrapper}>
              <Text size={200} weight="semibold">Contract A</Text>
              <Dropdown
                placeholder="Select contract..."
                value={analyzedContracts.find((c) => c.id === contractA)?.filename || ""}
                onOptionSelect={(_, data) => setContractA(data.optionValue as string)}
              >
                {analyzedContracts
                  .filter((c) => c.id !== contractB)
                  .map((c) => (
                    <Option key={c.id} value={c.id}>{c.filename}</Option>
                  ))}
              </Dropdown>
            </div>
            <div className={styles.dropdownWrapper}>
              <Text size={200} weight="semibold">Contract B</Text>
              <Dropdown
                placeholder="Select contract..."
                value={analyzedContracts.find((c) => c.id === contractB)?.filename || ""}
                onOptionSelect={(_, data) => setContractB(data.optionValue as string)}
              >
                {analyzedContracts
                  .filter((c) => c.id !== contractA)
                  .map((c) => (
                    <Option key={c.id} value={c.id}>{c.filename}</Option>
                  ))}
              </Dropdown>
            </div>
            <Button
              appearance="primary"
              onClick={handleCompare}
              disabled={!contractA || !contractB || loading}
            >
              {loading ? <Spinner size="tiny" /> : "Compare"}
            </Button>
          </div>

          {error && (
            <MessageBar intent="error" style={{ marginTop: 16 }}>
              <MessageBarBody>{error}</MessageBarBody>
            </MessageBar>
          )}

          {comparison && (
            <div style={{ marginTop: 32 }}>
              <Title3>Term Comparison</Title3>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Term</th>
                    <th>Contract A</th>
                    <th>Contract B</th>
                    <th>Advantage</th>
                  </tr>
                </thead>
                <tbody>
                  {comparison.term_comparisons.map((tc, i) => (
                    <tr key={i}>
                      <td><Text weight="semibold">{tc.term_name}</Text></td>
                      <td><Text>{tc.contract_a_value || "—"}</Text></td>
                      <td><Text>{tc.contract_b_value || "—"}</Text></td>
                      <td>
                        <Badge appearance="filled" color={advantageColor(tc.advantage)}>
                          {tc.advantage === "contract_a" ? "A" :
                           tc.advantage === "contract_b" ? "B" : "Neutral"}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {comparison.risk_diff && (
                <div style={{ marginTop: 24 }}>
                  <Title3>Risk Difference</Title3>
                  <Card className={styles.assessment} style={{ marginTop: 12 }}>
                    <Text style={{ whiteSpace: "pre-wrap" }}>{comparison.risk_diff}</Text>
                  </Card>
                </div>
              )}

              <Card className={styles.assessment}>
                <Title3>Overall Assessment</Title3>
                <Text style={{ display: "block", marginTop: 8, whiteSpace: "pre-wrap" }}>
                  {comparison.overall_assessment}
                </Text>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Compare;

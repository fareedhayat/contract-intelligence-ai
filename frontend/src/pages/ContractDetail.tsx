import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  Title2,
  Title3,
  Text,
  Card,
  Badge,
  Spinner,
  Accordion,
  AccordionItem,
  AccordionHeader,
  AccordionPanel,
  makeStyles,
  tokens,
  Divider,
  MessageBar,
  MessageBarBody,
} from "@fluentui/react-components";
import { getContract, getAnalysisStatus } from "../services/api";
import { useData } from "../components/DataProvider";
import type { ContractDocument, AnalysisResult } from "../types";

const useStyles = makeStyles({
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "24px",
  },
  section: {
    marginTop: "24px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
    gap: "12px",
    marginTop: "12px",
  },
  fieldCard: {
    padding: "16px",
  },
  fieldLabel: {
    color: tokens.colorNeutralForeground3,
    display: "block",
    marginBottom: "4px",
  },
  riskItem: {
    padding: "12px 16px",
    marginTop: "8px",
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground2,
  },
  riskHeader: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "8px",
  },
  obligationItem: {
    padding: "12px 16px",
    marginTop: "8px",
    borderRadius: tokens.borderRadiusMedium,
    backgroundColor: tokens.colorNeutralBackground2,
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  provisionList: {
    listStyleType: "disc",
    paddingLeft: "20px",
    marginTop: "8px",
    "& li": {
      marginBottom: "6px",
    },
  },
});

const severityColor = (s: string) =>
  s === "high" ? "danger" : s === "medium" ? "warning" : "success";

function ContractDetail() {
  const { id } = useParams<{ id: string }>();
  const styles = useStyles();
  const { getContractAnalysis, refreshAll } = useData();
  const [contract, setContract] = useState<ContractDocument | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    async function load() {
      try {
        const c = await getContract(id!);
        setContract(c);

        const a = await getContractAnalysis(id!);
        setAnalysis(a);
      } catch {
        setError("Contract not found");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, getContractAnalysis]);

  // Poll if analysis is in progress
  useEffect(() => {
    if (!id || !analysis || (analysis.status !== "pending" && analysis.status !== "in_progress")) return;

    const interval = setInterval(async () => {
      try {
        const status = await getAnalysisStatus(id);
        if (status.status === "completed" || status.status === "failed") {
          // Refresh to get latest data
          const a = await getContractAnalysis(id, true);
          setAnalysis(a);
          // Also refresh global state
          await refreshAll();
          clearInterval(interval);
        }
      } catch {
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id, analysis?.status, getContractAnalysis, refreshAll]);

  if (loading) return <Spinner label="Loading contract..." />;
  if (error) return <MessageBar intent="error"><MessageBarBody>{error}</MessageBarBody></MessageBar>;
  if (!contract) return null;

  const ed = analysis?.extracted_data;
  const isAnalyzing = analysis?.status === "pending" || analysis?.status === "in_progress";

  return (
    <div>
      <div className={styles.header}>
        <div>
          <Title2>{contract.filename}</Title2>
          <Text size={200} style={{ display: "block", color: tokens.colorNeutralForeground3 }}>
            Uploaded {new Date(contract.upload_date).toLocaleDateString()}
          </Text>
        </div>
        <Badge
          appearance="filled"
          size="large"
          color={
            analysis?.status === "completed" ? "success" :
            analysis?.status === "failed" ? "danger" :
            isAnalyzing ? "warning" : "informative"
          }
        >
          {analysis?.status ?? "no analysis"}
        </Badge>
      </div>

      {isAnalyzing && <Spinner label="Analysis in progress..." />}

      {analysis?.status === "failed" && (
        <MessageBar intent="error">
          <MessageBarBody>{analysis.error_message || "Analysis failed"}</MessageBarBody>
        </MessageBar>
      )}

      {analysis?.status === "completed" && (
        <>
          {/* Executive Summary */}
          {analysis.summary && (
            <div className={styles.section}>
              <Title3>Executive Summary</Title3>
              <Card className={styles.fieldCard} style={{ marginTop: 12 }}>
                <Text style={{ whiteSpace: "pre-wrap" }}>{analysis.summary.executive_summary}</Text>
              </Card>
            </div>
          )}

          {/* Extracted Data */}
          {ed && (
            <div className={styles.section}>
              <Title3>Extracted Data</Title3>
              <div className={styles.grid}>
                <Card className={styles.fieldCard}>
                  <Text className={styles.fieldLabel} size={200}>Parties</Text>
                  <Text>{ed.parties.join(", ") || "—"}</Text>
                </Card>
                <Card className={styles.fieldCard}>
                  <Text className={styles.fieldLabel} size={200}>Contract Type</Text>
                  <Text>{ed.contract_type || "—"}</Text>
                </Card>
                <Card className={styles.fieldCard}>
                  <Text className={styles.fieldLabel} size={200}>Effective Date</Text>
                  <Text>{ed.effective_date || "—"}</Text>
                </Card>
                <Card className={styles.fieldCard}>
                  <Text className={styles.fieldLabel} size={200}>Expiration Date</Text>
                  <Text>{ed.expiration_date || "—"}</Text>
                </Card>
                <Card className={styles.fieldCard}>
                  <Text className={styles.fieldLabel} size={200}>Governing Law</Text>
                  <Text>{ed.governing_law || "—"}</Text>
                </Card>
              </div>

              {ed.financial_terms.length > 0 && (
                <>
                  <Title3 style={{ marginTop: 20 }}>Financial Terms</Title3>
                  <div className={styles.grid}>
                    {ed.financial_terms.map((ft, i) => (
                      <Card key={i} className={styles.fieldCard}>
                        <Text className={styles.fieldLabel} size={200}>{ft.term_type}</Text>
                        <Text weight="semibold">
                          {ft.value != null ? `${ft.currency} ${ft.value.toLocaleString()}` : ft.description}
                        </Text>
                        {ft.value != null && ft.description && (
                          <Text size={200} style={{ display: "block", marginTop: 4, color: tokens.colorNeutralForeground3 }}>
                            {ft.description}
                          </Text>
                        )}
                      </Card>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          <Divider style={{ margin: "24px 0" }} />

          {/* Risk Flags */}
          <div className={styles.section}>
            <Title3>Risk Flags ({analysis.risk_flags.length})</Title3>
            {analysis.risk_flags.length === 0 ? (
              <Text style={{ color: tokens.colorNeutralForeground3, marginTop: 8, display: "block" }}>
                No risks identified.
              </Text>
            ) : (
              <Accordion multiple collapsible>
                {analysis.risk_flags.map((rf, i) => (
                  <AccordionItem key={i} value={`risk-${i}`}>
                    <AccordionHeader>
                      <div className={styles.riskHeader}>
                        <Badge appearance="filled" color={severityColor(rf.severity)}>
                          {rf.severity.toUpperCase()}
                        </Badge>
                        <Text weight="semibold">{rf.category.replace(/_/g, " ")}</Text>
                      </div>
                    </AccordionHeader>
                    <AccordionPanel>
                      <Text style={{ display: "block" }}>{rf.explanation}</Text>
                      {rf.clause_text && (
                        <Card className={styles.fieldCard} style={{ marginTop: 8, fontStyle: "italic" }}>
                          <Text size={200}>"{rf.clause_text}"</Text>
                        </Card>
                      )}
                      {rf.mitigation && (
                        <Text size={200} style={{ display: "block", marginTop: 8, color: tokens.colorNeutralForeground3 }}>
                          Mitigation: {rf.mitigation}
                        </Text>
                      )}
                    </AccordionPanel>
                  </AccordionItem>
                ))}
              </Accordion>
            )}
          </div>

          <Divider style={{ margin: "24px 0" }} />

          {/* Obligations */}
          <div className={styles.section}>
            <Title3>Obligations ({analysis.obligations.length})</Title3>
            {analysis.obligations.length === 0 ? (
              <Text style={{ color: tokens.colorNeutralForeground3, marginTop: 8, display: "block" }}>
                No obligations extracted.
              </Text>
            ) : (
              analysis.obligations.map((ob, i) => (
                <div key={i} className={styles.obligationItem}>
                  <div>
                    <Text weight="semibold">{ob.description}</Text>
                    <Text size={200} style={{ display: "block", color: tokens.colorNeutralForeground3 }}>
                      Party: {ob.party}
                      {ob.recurring && ` | Recurring: ${ob.frequency || "yes"}`}
                    </Text>
                  </div>
                  <Badge appearance="outline">
                    {ob.due_date || "No date"}
                  </Badge>
                </div>
              ))
            )}
          </div>

          {/* Key Provisions */}
          {analysis.summary && analysis.summary.key_provisions.length > 0 && (
            <>
              <Divider style={{ margin: "24px 0" }} />
              <div className={styles.section}>
                <Title3>Key Provisions</Title3>
                <ul className={styles.provisionList}>
                  {analysis.summary.key_provisions.map((p, i) => (
                    <li key={i}><Text>{p}</Text></li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default ContractDetail;

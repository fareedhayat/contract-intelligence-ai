import { useNavigate } from "react-router-dom";
import {
  Title2,
  Title3,
  Text,
  Card,
  makeStyles,
  tokens,
  Badge,
  Button,
  Spinner,
} from "@fluentui/react-components";
import {
  DocumentSearchRegular,
  CheckmarkCircleRegular,
  ClockRegular,
  ErrorCircleRegular,
  WarningRegular,
  ShieldErrorRegular,
  ShieldCheckmarkRegular,
  CalendarCheckmarkRegular,
} from "@fluentui/react-icons";
import { useData } from "../components/DataProvider";

const useStyles = makeStyles({
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginTop: "20px",
    marginBottom: "32px",
  },
  statCard: {
    padding: "20px",
  },
  statValue: {
    fontSize: "32px",
    fontWeight: "bold",
    display: "block",
    marginTop: "8px",
  },
  statLabel: {
    color: tokens.colorNeutralForeground3,
  },
  riskSection: {
    marginTop: "32px",
    marginBottom: "32px",
  },
  riskGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
    gap: "12px",
    marginTop: "12px",
  },
  riskCard: {
    padding: "16px",
    textAlign: "center",
  },
  riskValue: {
    fontSize: "28px",
    fontWeight: "bold",
    display: "block",
  },
  highRisk: {
    borderLeft: `4px solid ${tokens.colorPaletteRedBorder2}`,
  },
  mediumRisk: {
    borderLeft: `4px solid ${tokens.colorPaletteYellowBorder2}`,
  },
  lowRisk: {
    borderLeft: `4px solid ${tokens.colorPaletteGreenBorder2}`,
  },
  commonRisk: {
    marginTop: "16px",
    padding: "16px",
    backgroundColor: tokens.colorNeutralBackground2,
    borderRadius: tokens.borderRadiusMedium,
  },
  contractList: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
    marginTop: "12px",
  },
  contractRow: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "12px 16px",
    backgroundColor: tokens.colorNeutralBackground2,
    borderRadius: tokens.borderRadiusMedium,
    cursor: "pointer",
    "&:hover": {
      backgroundColor: tokens.colorNeutralBackground3,
    },
  },
  contractInfo: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
});

function Dashboard() {
  const styles = useStyles();
  const navigate = useNavigate();
  const { stats, contracts, loading } = useData();

  if (loading) return <Spinner label="Loading dashboard..." />;

  return (
    <div>
      <Title2>Dashboard</Title2>

      {/* Main Stats */}
      <div className={styles.statsGrid}>
        <Card className={styles.statCard}>
          <DocumentSearchRegular fontSize={24} />
          <Text className={styles.statLabel}>Total Contracts</Text>
          <Text className={styles.statValue}>{stats?.total_contracts ?? 0}</Text>
        </Card>
        <Card className={styles.statCard}>
          <CheckmarkCircleRegular fontSize={24} />
          <Text className={styles.statLabel}>Analyzed</Text>
          <Text className={styles.statValue}>{stats?.analyzed ?? 0}</Text>
        </Card>
        <Card className={styles.statCard}>
          <ClockRegular fontSize={24} />
          <Text className={styles.statLabel}>Pending</Text>
          <Text className={styles.statValue}>{stats?.pending ?? 0}</Text>
        </Card>
        <Card className={styles.statCard}>
          <CalendarCheckmarkRegular fontSize={24} />
          <Text className={styles.statLabel}>Obligations</Text>
          <Text className={styles.statValue}>{stats?.total_obligations ?? 0}</Text>
        </Card>
        <Card className={styles.statCard}>
          <ErrorCircleRegular fontSize={24} />
          <Text className={styles.statLabel}>Failed</Text>
          <Text className={styles.statValue}>{stats?.failed ?? 0}</Text>
        </Card>
      </div>

      {/* Risk Breakdown */}
      <div className={styles.riskSection}>
        <Title3>
          <ShieldErrorRegular style={{ marginRight: 8 }} />
          Risk Overview
        </Title3>
        <div className={styles.riskGrid}>
          <Card className={`${styles.riskCard} ${styles.highRisk}`}>
            <Text className={styles.statLabel}>High Risk</Text>
            <Text className={styles.riskValue} style={{ color: tokens.colorPaletteRedForeground1 }}>
              {stats?.high_risk ?? 0}
            </Text>
          </Card>
          <Card className={`${styles.riskCard} ${styles.mediumRisk}`}>
            <Text className={styles.statLabel}>Medium Risk</Text>
            <Text className={styles.riskValue} style={{ color: tokens.colorPaletteYellowForeground2 }}>
              {stats?.medium_risk ?? 0}
            </Text>
          </Card>
          <Card className={`${styles.riskCard} ${styles.lowRisk}`}>
            <Text className={styles.statLabel}>Low Risk</Text>
            <Text className={styles.riskValue} style={{ color: tokens.colorPaletteGreenForeground1 }}>
              {stats?.low_risk ?? 0}
            </Text>
          </Card>
          <Card className={styles.riskCard}>
            <ShieldCheckmarkRegular fontSize={20} />
            <Text className={styles.statLabel}>No Risks</Text>
            <Text className={styles.riskValue}>
              {(stats?.analyzed ?? 0) - (stats?.contracts_with_risks ?? 0)}
            </Text>
          </Card>
        </div>
        
        {stats?.most_common_risk && (
          <div className={styles.commonRisk}>
            <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
              Most common risk category:
            </Text>
            <Text weight="semibold" style={{ marginLeft: 8 }}>
              {stats.most_common_risk.replace(/_/g, " ")}
            </Text>
            <Badge appearance="outline" style={{ marginLeft: 8 }}>
              {stats.most_common_risk_count} occurrence{stats.most_common_risk_count !== 1 ? "s" : ""}
            </Badge>
          </div>
        )}
      </div>

      {/* Recent Contracts */}
      <Title3>Recent Contracts</Title3>
      {contracts.length === 0 ? (
        <Text style={{ display: "block", marginTop: 12, color: tokens.colorNeutralForeground3 }}>
          No contracts uploaded yet.{" "}
          <Button appearance="transparent" onClick={() => navigate("/upload")}>
            Upload one
          </Button>
        </Text>
      ) : (
        <div className={styles.contractList}>
          {contracts.slice(0, 10).map((c) => (
            <div
              key={c.id}
              className={styles.contractRow}
              onClick={() => navigate(`/contracts/${c.id}`)}
            >
              <div className={styles.contractInfo}>
                <DocumentSearchRegular fontSize={20} />
                <div>
                  <Text weight="semibold">{c.filename}</Text>
                  <Text size={200} style={{ display: "block", color: tokens.colorNeutralForeground3 }}>
                    {new Date(c.upload_date).toLocaleDateString()}
                  </Text>
                </div>
              </div>
              <Badge
                appearance="filled"
                color={
                  c.status === "completed" ? "success" :
                  c.status === "failed" ? "danger" :
                  c.status === "in_progress" ? "warning" : "informative"
                }
              >
                {c.status}
              </Badge>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Title2,
  Text,
  Card,
  CardHeader,
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
} from "@fluentui/react-icons";
import { getDashboardStats, listContracts } from "../services/api";
import type { DashboardStats, ContractDocument } from "../types";

const useStyles = makeStyles({
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
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
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [contracts, setContracts] = useState<ContractDocument[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [statsData, contractsData] = await Promise.all([
          getDashboardStats(),
          listContracts(0, 10),
        ]);
        setStats(statsData);
        setContracts(contractsData.contracts);
      } catch {
        // API not available yet
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <Spinner label="Loading dashboard..." />;

  return (
    <div>
      <Title2>Dashboard</Title2>

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
          <WarningRegular fontSize={24} />
          <Text className={styles.statLabel}>With Risks</Text>
          <Text className={styles.statValue}>{stats?.contracts_with_risks ?? 0}</Text>
        </Card>
        <Card className={styles.statCard}>
          <ErrorCircleRegular fontSize={24} />
          <Text className={styles.statLabel}>Failed</Text>
          <Text className={styles.statValue}>{stats?.failed ?? 0}</Text>
        </Card>
      </div>

      <Title2>Recent Contracts</Title2>
      {contracts.length === 0 ? (
        <Text style={{ display: "block", marginTop: 12, color: tokens.colorNeutralForeground3 }}>
          No contracts uploaded yet.{" "}
          <Button appearance="transparent" onClick={() => navigate("/upload")}>
            Upload one
          </Button>
        </Text>
      ) : (
        <div className={styles.contractList}>
          {contracts.map((c) => (
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

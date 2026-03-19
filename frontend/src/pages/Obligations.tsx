import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Title2,
  Text,
  Card,
  Badge,
  Spinner,
  Dropdown,
  Option,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import {
  CalendarCheckmarkRegular,
  ArrowRepeatAllRegular,
} from "@fluentui/react-icons";
import { getUpcomingObligations, listObligations } from "../services/api";
import type { ObligationWithContract } from "../types";

const useStyles = makeStyles({
  controls: {
    display: "flex",
    gap: "16px",
    alignItems: "center",
    marginTop: "20px",
    marginBottom: "20px",
  },
  list: {
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  item: {
    padding: "16px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    cursor: "pointer",
    "&:hover": {
      backgroundColor: tokens.colorNeutralBackground3,
    },
  },
  itemLeft: {
    display: "flex",
    gap: "12px",
    flex: 1,
  },
  itemRight: {
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-end",
    gap: "4px",
  },
  meta: {
    display: "flex",
    gap: "8px",
    alignItems: "center",
    marginTop: "4px",
  },
});

type TimeRange = "30" | "60" | "90" | "180" | "365" | "all";

function Obligations() {
  const styles = useStyles();
  const navigate = useNavigate();
  const [obligations, setObligations] = useState<ObligationWithContract[]>([]);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState<TimeRange>("30");

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        if (range === "all") {
          const data = await listObligations(undefined, 0, 200);
          setObligations(data.obligations);
        } else {
          const data = await getUpcomingObligations(parseInt(range));
          setObligations(data.obligations);
        }
      } catch {
        // API not available
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [range]);

  return (
    <div>
      <Title2>Obligations Tracker</Title2>
      <Text style={{ display: "block", marginTop: 8, color: tokens.colorNeutralForeground3 }}>
        Track deadlines, deliverables, and compliance requirements across all contracts.
      </Text>

      <div className={styles.controls}>
        <Text size={200} weight="semibold">Show:</Text>
        <Dropdown
          value={range === "all" ? "All obligations" : `Next ${range} days`}
          onOptionSelect={(_, data) => setRange(data.optionValue as TimeRange)}
        >
          <Option value="30">Next 30 days</Option>
          <Option value="60">Next 60 days</Option>
          <Option value="90">Next 90 days</Option>
          <Option value="180">Next 180 days</Option>
          <Option value="365">Next 365 days</Option>
          <Option value="all">All obligations</Option>
        </Dropdown>
        <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
          {obligations.length} obligation{obligations.length !== 1 ? "s" : ""}
        </Text>
      </div>

      {loading ? (
        <Spinner label="Loading obligations..." />
      ) : obligations.length === 0 ? (
        <Text style={{ color: tokens.colorNeutralForeground3 }}>
          No obligations found for this time range.
        </Text>
      ) : (
        <div className={styles.list}>
          {obligations.map((ob, i) => (
            <Card
              key={i}
              className={styles.item}
              onClick={() => navigate(`/contracts/${ob.contract_id}`)}
            >
              <div className={styles.itemLeft}>
                <CalendarCheckmarkRegular fontSize={20} style={{ marginTop: 2 }} />
                <div>
                  <Text weight="semibold">{ob.description}</Text>
                  <div className={styles.meta}>
                    <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                      {ob.party}
                    </Text>
                    {ob.filename && (
                      <Text size={200} style={{ color: tokens.colorNeutralForeground3 }}>
                        | {ob.filename}
                      </Text>
                    )}
                    {ob.recurring && (
                      <Badge appearance="outline" size="small" icon={<ArrowRepeatAllRegular />}>
                        {ob.frequency || "Recurring"}
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
              <div className={styles.itemRight}>
                <Badge appearance="filled" color={ob.due_date ? "warning" : "informative"}>
                  {ob.due_date || "No date"}
                </Badge>
                <Badge appearance="outline" size="small">
                  {ob.status}
                </Badge>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default Obligations;

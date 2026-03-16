import { Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  makeStyles,
  tokens,
  Text,
  Tab,
  TabList,
} from "@fluentui/react-components";
import {
  DocumentSearchRegular,
  ArrowUploadRegular,
  ScalesRegular,
  CalendarCheckmarkRegular,
  GridRegular,
} from "@fluentui/react-icons";

const useStyles = makeStyles({
  root: {
    display: "flex",
    height: "100vh",
  },
  sidebar: {
    width: "240px",
    backgroundColor: tokens.colorNeutralBackground3,
    borderRight: `1px solid ${tokens.colorNeutralStroke2}`,
    display: "flex",
    flexDirection: "column",
    padding: "16px 0",
  },
  logo: {
    padding: "0 20px 20px",
    borderBottom: `1px solid ${tokens.colorNeutralStroke2}`,
    marginBottom: "12px",
  },
  content: {
    flex: 1,
    overflow: "auto",
    padding: "24px",
    backgroundColor: tokens.colorNeutralBackground1,
  },
});

const navItems = [
  { path: "/dashboard", label: "Dashboard", icon: <GridRegular /> },
  { path: "/upload", label: "Upload Contract", icon: <ArrowUploadRegular /> },
  { path: "/compare", label: "Compare", icon: <ScalesRegular /> },
  { path: "/obligations", label: "Obligations", icon: <CalendarCheckmarkRegular /> },
];

function Layout() {
  const styles = useStyles();
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className={styles.root}>
      <nav className={styles.sidebar}>
        <div className={styles.logo}>
          <DocumentSearchRegular fontSize={24} />
          <Text weight="semibold" size={400} style={{ marginLeft: 8 }}>
            Contract AI
          </Text>
        </div>
        <TabList
          vertical
          selectedValue={location.pathname}
          onTabSelect={(_, data) => navigate(data.value as string)}
        >
          {navItems.map((item) => (
            <Tab key={item.path} value={item.path} icon={item.icon}>
              {item.label}
            </Tab>
          ))}
        </TabList>
      </nav>
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  );
}

export default Layout;

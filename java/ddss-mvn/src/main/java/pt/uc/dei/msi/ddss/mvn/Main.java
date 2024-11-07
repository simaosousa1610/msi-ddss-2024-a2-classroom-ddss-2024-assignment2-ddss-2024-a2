/**
 * =============================================
 * = Design and Development of Secure Software =
 * =============== MSI 2019/2020 ===============
 * ========== Practical Assignment #2 ==========
 * ================== Part #1 ==================
 * =============================================
 * =============================================
 * === Department of Informatics Engineering ===
 * =========== University of Coimbra ===========
 * =============================================
 * <p>
 * Prof. Marco Vieira <mvieira@dei.uc.pt>
 * Prof. Nuno Antunes <nmsa@dei.uc.pt>
 * <p>
 * <p>
 * Repository: https://github.com/msi-ddss/ddss2019
 */
package pt.uc.dei.msi.ddss.mvn;

import java.net.UnknownHostException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import spark.utils.IOUtils;

import static spark.Spark.get;
import static spark.Spark.post;
import static spark.Spark.staticFiles;
import static pt.uc.dei.msi.ddss.mvn.Impl.part1_correct;
import static pt.uc.dei.msi.ddss.mvn.Impl.part1_vulnerable;
import static pt.uc.dei.msi.ddss.mvn.Impl.part2_correct;
import static pt.uc.dei.msi.ddss.mvn.Impl.part2_vulnerable;
import static pt.uc.dei.msi.ddss.mvn.Impl.part3_correct;
import static pt.uc.dei.msi.ddss.mvn.Impl.part3_vulnerable;

/**
 * Important: these sources are merely suggestions of implementations.
 * You are responsible for all the content that is delivered, and therefore you
 * should modify everything you deem as necessary
 * <p>
 * <p>
 *
 * @author Nuno Antunes <nmsa@dei.uc.pt>
 */
public class Main {

    private static final Logger CL_LOG = LoggerFactory.getLogger("clear-logger");
    private static final Logger LOGGER = LoggerFactory.getLogger(Main.class);

    private static final String JDBC_PSQL_CONN_LOCAL = "jdbc:postgresql://localhost:5432/ddss-database-assignment-2";
    private static final String JDBC_PSQL_CONN_DOCKER = "jdbc:postgresql://db:5432/ddss-database-assignment-2";
    private static final String JDBC_USER = "ddss-database-assignment-2";
    private static final String JDBC_PASS = "ddss-database-assignment-2";

    /**
     * The dockerfile is configured to run "java -jar ddss-mvn-1.0.jar docker"
     */
//    private static String jdbcConnection = JDBC_PSQL_CONN_DOCKER;
    private static String jdbcURL = JDBC_PSQL_CONN_LOCAL;

    public static void main(String[] args) throws UnknownHostException {
        for (String arg : args) {
            if (arg.contains("docker")) {
                jdbcURL = JDBC_PSQL_CONN_DOCKER;
            }
        }

        showDatabaseContent();

        staticFiles.location("/public");

        // Main handle
        post("/part1_vulnerable", (req, res) -> part1_vulnerable(req, res));
        get("/part1_vulnerable", (req, res) -> part1_vulnerable(req, res));
        post("/part1_correct", (req, res) -> part1_correct(req, res));
        get("/part1_correct", (req, res) -> part1_correct(req, res));
        post("/part2_vulnerable", (req, res) -> part2_vulnerable(req, res));
        get("/part2_vulnerable", (req, res) -> part2_vulnerable(req, res));
        post("/part2_correct", (req, res) -> part2_correct(req, res));
        get("/part2_correct", (req, res) -> part2_correct(req, res));
        post("/part3_vulnerable", (req, res) -> part3_vulnerable(req, res));
        get("/part3_vulnerable", (req, res) -> part3_vulnerable(req, res));
        post("/part3_correct", (req, res) -> part3_correct(req, res));
        get("/part3_correct", (req, res) -> part3_correct(req, res));

        // Default info handle
        get("*", (req, res) -> IOUtils.toString(spark.Spark.class.getResourceAsStream("/public/index.html")));

        // Ready info
        spark.Spark.awaitInitialization();
        LOGGER.info("\n\n\nServer is listening at@ http://0.0.0.0:{}/\n\n\n", spark.Spark.port());
    }

    private static void showDatabaseContent() {
        Connection conn = getConnection();
        if (conn == null) {
            LOGGER.error("Could not obtain connection to the database.");
            return;
        }
        try {

            ResultSet users = conn.createStatement().executeQuery("SELECT * from users");
            LOGGER.info("\n\n == Users Contents == \n");
            printResultSet(users);

            ResultSet messages = conn.createStatement().executeQuery("SELECT * from messages");
            CL_LOG.info("\n\n == Messages Contents == \n");
            printResultSet(messages);

            ResultSet books = conn.createStatement().executeQuery("SELECT * from books");
            CL_LOG.info("\n == Books Contents == \n");
            printResultSet(books);

            CL_LOG.info("\n---------------------\n\n");
        } catch (SQLException ex) {
            LOGGER.error("Error printing database content.", ex);
        }
        close(conn);
    }

    private static void printResultSet(ResultSet rs) {
        try {
            while (rs.next()) {
                for (int i = 0; i < rs.getMetaData().getColumnCount(); i++) {
                    CL_LOG.info("| " + rs.getString(i + 1) + "\t");
                }
                CL_LOG.info("|\n");
            }
        } catch (SQLException ex) {
            LOGGER.error("Error obtaining data: ", ex);
        }
    }

    private static Connection getConnection() {
        try {
            Class.forName("org.postgresql.Driver");
            Connection c = DriverManager.getConnection(jdbcURL, JDBC_USER, JDBC_PASS);
            return c;
        } catch (ClassNotFoundException | SQLException ex) {
            LOGGER.error("Could not obtain connection to the database: ", ex);
        }
        return null;
    }

    private static void close(Connection conn) {
        if (conn != null) {
            try {
                conn.close();
            } catch (SQLException ex) {
                LOGGER.error("Error closing connection to the database: ", ex);
            }
        }
    }
}
